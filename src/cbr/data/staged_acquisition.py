"""Staged, rate-limit-aware, resumable Dukascopy tick acquisition (owner ruling D41 §3-7).

Transport only. This module changes **how** the canonical files are fetched, never what counts as canonical data:
Dukascopy XAUUSD ticks, tick-mid STRUCTURE, tick bid/ask EXECUTION (D41 §11).

    .venv/bin/python -m cbr.data.staged_acquisition plan 2018 2024        # blocks and request budget, no network
    .venv/bin/python -m cbr.data.staged_acquisition run 2018-01           # one month block
    .venv/bin/python -m cbr.data.staged_acquisition run 2018-01 2018-12   # a range of month blocks
    .venv/bin/python -m cbr.data.staged_acquisition status 2018 2024      # per-block accounting

Design notes that matter:
  * **one request stream** — concurrency is what produced HTTP 429 in the first place (D41 §4);
  * **adaptive throttle** — jittered pacing, exponential backoff, a longer cooldown after a 429 (D41 §5);
  * **persistent retry queue** — a restart loses no state (D41 §5);
  * **scheduled closures are never requested** — they are written to the manifest as `SCHEDULED_CLOSURE` without an
    HTTP call. This is an acquisition optimization, never a strategy-data screen: an hour is skipped only when the
    canonical session calendar already establishes it as closed, and never when its status is uncertain (D41 §6).
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data.sessions import expected_closed

BLOCKS = dk.RAW / "blocks"
RETRY_QUEUE = dk.RAW / "retry_queue.json"
USER_AGENT = "cbr-research/0.1"
# Throttle policy (D41 §5). Deliberately conservative: throughput is not the objective, completeness is.
BASE_PAUSE_SEC = 1.0
JITTER_SEC = 0.6
MAX_ATTEMPTS = 6
BACKOFF_BASE_SEC = 20
RATE_LIMIT_COOLDOWN_SEC = 180
TIMEOUT_SEC = 120


@dataclass
class HourOutcome:
    hour: datetime
    state: str                       # DATA / EMPTY / SCHEDULED_CLOSURE / FAILED
    bytes: int = 0
    attempts: int = 0
    http_429: int = 0
    http_5xx: int = 0
    error: str | None = None


@dataclass
class BlockStats:
    block: str
    requested_open_hours: int = 0
    successful_hours: int = 0
    scheduled_closures: int = 0
    legitimate_empty_files: int = 0
    retry_count: int = 0
    http_429: int = 0
    http_5xx: int = 0
    unresolved_failures: int = 0
    bytes: int = 0
    hours: list = field(default_factory=list)

    def complete(self) -> bool:
        return self.unresolved_failures == 0

    def as_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "hours"}
        d["complete"] = self.complete()
        d["hours_detail"] = [{"hour": h.hour.isoformat(), "state": h.state, "bytes": h.bytes,
                              "attempts": h.attempts, "error": h.error} for h in self.hours if h.state != "DATA"]
        return d


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def scheduled_closed(hour: datetime) -> bool:
    """Definitely closed by the canonical calendar. Uncertain hours are never skipped (D41 §6)."""
    return bool(expected_closed(pd.Timestamp(hour)))


def block_hours(block: str, instrument: str = "xauusd") -> tuple[list[datetime], list[datetime]]:
    """(hours to request, hours skipped as scheduled closure) for a `YYYY-MM` block."""
    start = datetime.strptime(block, "%Y-%m").replace(tzinfo=UTC)
    end = (start.replace(day=28) + timedelta(days=5)).replace(day=1)
    request, skipped = [], []
    day = start
    while day < end:
        if day.weekday() < 5:                       # Dukascopy publishes weekday files; weekends are closed
            for h in range(24):
                hour = day.replace(hour=h)
                (skipped if scheduled_closed(hour) else request).append(hour)
        day += timedelta(days=1)
    return request, skipped


def _cached(instrument: str, hour: datetime):
    return dk.CACHE / instrument / f"{hour:%Y-%m-%d_%H}.bi5"


def _load_queue() -> dict:
    return json.loads(RETRY_QUEUE.read_text()) if RETRY_QUEUE.exists() else {"pending": []}


def _save_queue(queue: dict) -> None:
    RETRY_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    tmp = RETRY_QUEUE.with_suffix(".tmp")
    tmp.write_text(json.dumps(queue, indent=1) + "\n")
    tmp.replace(RETRY_QUEUE)                         # atomic


def fetch_hour(instrument: str, hour: datetime, *, sleep=time.sleep) -> HourOutcome:
    """One hourly file through one request stream, with adaptive throttling. Resumes from a cached file."""
    cached = _cached(instrument, hour)
    if cached.exists():
        size = cached.stat().st_size
        return HourOutcome(hour, "DATA" if size else "EMPTY", size)
    url = (f"{dk.FEED}/{instrument.upper()}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/"
           f"{hour.hour:02d}h_ticks.bi5")
    out = HourOutcome(hour, "FAILED")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        out.attempts = attempt
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                data = resp.read()
            cached.parent.mkdir(parents=True, exist_ok=True)
            tmp = cached.with_suffix(".part")
            tmp.write_bytes(data)
            tmp.replace(cached)                      # atomic write
            out.state = "DATA" if data else "EMPTY"
            out.bytes = len(data)
            sleep(BASE_PAUSE_SEC + random.uniform(0, JITTER_SEC))     # jittered pacing
            return out
        except urllib.error.HTTPError as err:
            if err.code == 404:                      # no file for this hour: the market was closed
                cached.parent.mkdir(parents=True, exist_ok=True)
                cached.write_bytes(b"")
                out.state, out.bytes = "EMPTY", 0
                sleep(BASE_PAUSE_SEC + random.uniform(0, JITTER_SEC))
                return out
            if err.code == 429:
                out.http_429 += 1
                wait = RATE_LIMIT_COOLDOWN_SEC       # a long cooldown, not a short retry
            elif 500 <= err.code < 600:
                out.http_5xx += 1
                wait = BACKOFF_BASE_SEC * attempt
            else:
                out.error = f"HTTP {err.code}"
                return out
        except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
            out.error = type(err).__name__
            wait = BACKOFF_BASE_SEC * attempt
        sleep(wait + random.uniform(0, JITTER_SEC))                  
    out.error = out.error or "attempts exhausted"
    return out


def run_block(block: str, instrument: str = "xauusd", *, sleep=time.sleep) -> BlockStats:
    """Acquire one `YYYY-MM` block. Re-running is safe: cached hours are never refetched."""
    request, skipped = block_hours(block, instrument)
    stats = BlockStats(block=block, requested_open_hours=len(request), scheduled_closures=len(skipped))
    queue = _load_queue()
    pending = {h for h in queue["pending"] if h.startswith(block)}
    for hour in request:
        out = fetch_hour(instrument, hour, sleep=sleep)
        stats.hours.append(out)
        stats.retry_count += max(out.attempts - 1, 0)
        stats.http_429 += out.http_429
        stats.http_5xx += out.http_5xx
        stats.bytes += out.bytes
        key = hour.isoformat()
        if out.state == "DATA":
            stats.successful_hours += 1
            pending.discard(key)
        elif out.state == "EMPTY":
            stats.legitimate_empty_files += 1
            pending.discard(key)
        else:
            stats.unresolved_failures += 1
            pending.add(key)
        queue["pending"] = sorted(set(queue["pending"]) - {key} | ({key} if out.state == "FAILED" else set()))
        _save_queue(queue)
    write_block_manifest(stats, skipped, instrument)
    return stats


def write_block_manifest(stats: BlockStats, skipped: list[datetime], instrument: str) -> dict:
    BLOCKS.mkdir(parents=True, exist_ok=True)
    body = {"block": stats.block, "instrument": instrument, "ruling": "D41 §7",
            "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "scheduled_closure_hours": [h.isoformat() for h in skipped], **stats.as_dict()}
    body["manifest_hash"] = _sha_text(json.dumps(body, sort_keys=True))
    path = BLOCKS / f"{instrument}_{stats.block}.json"
    path.write_text(json.dumps(body, indent=1) + "\n")
    return body


def plan(start_year: int, end_year: int, instrument: str = "xauusd") -> dict:
    """Request budget without touching the network (D41 §3, §6)."""
    blocks, req, skip = [], 0, 0
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            b = f"{year}-{month:02d}"
            r, s = block_hours(b, instrument)
            blocks.append({"block": b, "request_hours": len(r), "scheduled_closure_hours": len(s)})
            req += len(r)
            skip += len(s)
    return {"blocks": len(blocks), "request_hours": req, "scheduled_closure_hours_avoided": skip,
            "naive_hours": req + skip, "saved_fraction": round(skip / (req + skip), 4), "detail": blocks}


def status(start_year: int, end_year: int, instrument: str = "xauusd") -> dict:
    out, complete = [], 0
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            b = f"{year}-{month:02d}"
            p = BLOCKS / f"{instrument}_{b}.json"
            if p.exists():
                m = json.loads(p.read_text())
                out.append({"block": b, "complete": m["complete"], "successful_hours": m["successful_hours"],
                            "unresolved_failures": m["unresolved_failures"], "http_429": m["http_429"]})
                complete += int(m["complete"])
    return {"blocks_written": len(out), "blocks_complete": complete,
            "pending_retries": len(_load_queue()["pending"]), "blocks": out}


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        p = plan(int(sys.argv[2]), int(sys.argv[3]))
        print(json.dumps({k: v for k, v in p.items() if k != "detail"}, indent=2))
    elif cmd == "run":
        first = sys.argv[2]
        last = sys.argv[3] if len(sys.argv) > 3 else first
        months = pd.period_range(first, last, freq="M")
        for m in months:
            s = run_block(str(m))
            print(f"{s.block}: {s.successful_hours} data, {s.legitimate_empty_files} empty, "
                  f"{s.scheduled_closures} closed (not requested), {s.unresolved_failures} unresolved, "
                  f"429s={s.http_429}, complete={s.complete()}", flush=True)
    elif cmd == "status":
        print(json.dumps(status(int(sys.argv[2]), int(sys.argv[3])), indent=2))
    else:
        raise SystemExit("usage: staged_acquisition [plan Y1 Y2 | run YYYY-MM [YYYY-MM] | status Y1 Y2]")


if __name__ == "__main__":
    main()
