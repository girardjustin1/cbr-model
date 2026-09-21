"""Real Dukascopy bid/ask quotes and classified interval metadata for execution (owner ruling D39, Phase 14A.1).

Data plumbing only: no execution semantic from D38 changes here, and no CBR rule is consulted. Quotes come from the
stored canonical tick files — never from midpoint, candle OHLC, futures, vendor bars or interpolation.

Interval classification **translates** the project's existing Phase 9 criterion (AC-07: a minute with no data that is
not `expected_closed` is an unexpected gap) rather than defining a second, different one.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data import market_closures as mc
from cbr.data.sessions import expected_closed
from cbr.execution import prices as px

TICKS = dk.RAW / "{instrument}" / "ticks"
DAY_MANIFEST = dk.RAW / "manifest.json"
SCHEDULED_CLOSURE = px.SCHEDULED_CLOSURE
ROLLOVER_EXCLUSION = "ROLLOVER_EXCLUSION"
DATA_GAP = px.DATA_GAP
VALID_SPARSE_QUOTES = "VALID_SPARSE_QUOTES"
NOT_LOADED = "NOT_LOADED"
VERIFIED_MARKET_DATA_CLOSURE = mc.VERIFIED_MARKET_DATA_CLOSURE
M1 = pd.Timedelta(minutes=1)


class TickDataError(RuntimeError):
    """A source file is unusable. Execution never silently skips one."""


@dataclass(frozen=True)
class TickProvenance:
    """Enough to reproduce a replay exactly (D39 §10)."""

    instrument: str
    requested_window: tuple[str, str]
    loaded_window: tuple[str | None, str | None]
    tick_count: int
    source_file_ids: tuple[str, ...]
    source_hashes: dict
    missing_days: tuple[str, ...]
    gap_manifest_version: str | None
    day_manifest_sha256: str | None
    duplicate_timestamps: int
    classified: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"instrument": self.instrument, "requested_window": list(self.requested_window),
                "loaded_window": list(self.loaded_window), "tick_count": self.tick_count,
                "source_file_ids": list(self.source_file_ids), "source_hashes": self.source_hashes,
                "missing_days": list(self.missing_days), "gap_manifest_version": self.gap_manifest_version,
                "day_manifest_sha256": self.day_manifest_sha256,
                "duplicate_timestamps": self.duplicate_timestamps, "classified_intervals": self.classified}


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tick_dir(instrument: str):
    return dk.RAW / instrument / "ticks"


def _day_manifest() -> tuple[dict, str | None]:
    if not DAY_MANIFEST.exists():
        return {}, None
    return json.loads(DAY_MANIFEST.read_text()), _sha(DAY_MANIFEST)


def validate_ticks(ticks: pd.DataFrame, source: str) -> pd.DataFrame:
    """D39 §2: ask > bid, both positive, UTC, chronological. Duplicates follow the Phase 9 policy (kept, stable)."""
    missing = [c for c in ("ts", "bid", "ask") if c not in ticks.columns]
    if missing:
        raise TickDataError(f"{source}: tick file missing {missing}")
    t = ticks.sort_values("ts", kind="stable")                    # Phase 9 policy: stable order, duplicates retained
    ts = pd.DatetimeIndex(t["ts"])
    if ts.tz is None:
        raise TickDataError(f"{source}: tick timestamps must be timezone-aware UTC")
    if (t["bid"] <= 0).any() or (t["ask"] <= 0).any():
        raise TickDataError(f"{source}: non-positive bid or ask")
    if (t["ask"] <= t["bid"]).any():
        raise TickDataError(f"{source}: ask must be strictly greater than bid")
    return t.set_index(ts.tz_convert("UTC")).drop(columns=["ts"])


def load_quotes(start: pd.Timestamp, end: pd.Timestamp, *, instrument: str = "xauusd"
                ) -> tuple[pd.DataFrame, TickProvenance]:
    """Executable bid/ask quotes for [start, end], straight from stored ticks (D39 §2-3)."""
    manifest, manifest_hash = _day_manifest()
    frames, files, hashes, missing = [], [], {}, []
    duplicates = 0
    for day in pd.date_range(start.floor("D"), end, freq="D", tz="UTC"):
        name = f"{day.date().isoformat()}.parquet"
        path = _tick_dir(instrument) / name
        if not path.exists():
            missing.append(day.date().isoformat())
            continue
        raw = pd.read_parquet(path)                                # a malformed file raises, never skipped silently
        t = validate_ticks(raw, str(path))
        duplicates += int(t.index.duplicated().sum())
        frames.append(t)
        rel = str(path.relative_to(dk.ROOT))
        files.append(rel)
        hashes[rel] = _sha(path)
    if not frames:
        quotes = pd.DataFrame(columns=list(px.QUOTE_COLUMNS))
        quotes.index = pd.DatetimeIndex([], tz="UTC", name="time")
        loaded = (None, None)
        count = 0
    else:
        t = pd.concat(frames).sort_index(kind="stable")
        t = t[(t.index >= start) & (t.index <= end)]
        quotes = px.quotes_from_ticks(t.rename(columns={"bid": "bid", "ask": "ask"}))
        loaded = (str(quotes.index[0]), str(quotes.index[-1])) if len(quotes) else (None, None)
        count = len(quotes)
    prov = TickProvenance(
        instrument=instrument, requested_window=(str(start), str(end)), loaded_window=loaded, tick_count=count,
        source_file_ids=tuple(files), source_hashes=hashes, missing_days=tuple(missing),
        gap_manifest_version=manifest.get("cli") if manifest else None, day_manifest_sha256=manifest_hash,
        duplicate_timestamps=duplicates)
    return px.validate(quotes), prov


def classify_intervals(start: pd.Timestamp, end: pd.Timestamp, quotes: pd.DataFrame, prov: TickProvenance, *,
                       rollover_pre_min: int, rollover_post_min: int, rollover_ny_time: str = "17:00",
                       closures: mc.Registry | None = None) -> tuple[list[px.Gap], dict]:
    """Minute-level classification, translating Phase 9's AC-07 criterion (D39 §4).

    A minute with quotes is live. A minute without them is a SCHEDULED_CLOSURE, a ROLLOVER_EXCLUSION, a day that was
    NOT_LOADED, a VERIFIED_MARKET_DATA_CLOSURE, or — exactly Phase 9's "unexpected gap" — a DATA_GAP. Sparse quoting
    inside a live minute is never a gap, and only DATA_GAP runs are returned to the simulator as `px.Gap`.

    **Verified closures are not gaps** (D43 §5). During a proven closure there is no executable quote stream at all,
    so a fill cannot have occurred inside the interval and there is nothing to call unprovable. No quote is
    fabricated and no price is interpolated: the clock simply holds no executable market event there. An interval
    the evidence does **not** establish as closed stays a DATA_GAP and keeps its D38/D39 unprovable semantics
    unchanged (D43 §6).
    """
    reg = closures if closures is not None else mc.load()
    minutes = pd.date_range(start.floor("1min"), end.ceil("1min"), freq="1min", tz="UTC", inclusive="left")
    have = set(quotes.index.floor("1min")) if len(quotes) else set()
    missing_days = set(prov.missing_days)
    kinds: dict[pd.Timestamp, str] = {}
    for m in minutes:
        if m in have:
            kinds[m] = VALID_SPARSE_QUOTES
        elif m.date().isoformat() in missing_days:
            kinds[m] = NOT_LOADED
        elif expected_closed(m):
            kinds[m] = SCHEDULED_CLOSURE
        elif px.in_rollover_window(m, pre_min=rollover_pre_min, post_min=rollover_post_min, ny_time=rollover_ny_time):
            kinds[m] = ROLLOVER_EXCLUSION
        elif mc.closed_at(m, reg):
            kinds[m] = VERIFIED_MARKET_DATA_CLOSURE
        else:
            kinds[m] = DATA_GAP
    gaps, counts = [], {}
    run_kind, run_start, prev = None, None, None
    for m in minutes:
        k = kinds[m]
        counts[k] = counts.get(k, 0) + 1
        if k != run_kind:
            if run_kind in (DATA_GAP, NOT_LOADED) and run_start is not None:
                gaps.append(px.Gap(run_start, prev + M1, DATA_GAP))
            run_kind, run_start = k, m
        prev = m
    if run_kind in (DATA_GAP, NOT_LOADED) and run_start is not None and prev is not None:
        gaps.append(px.Gap(run_start, prev + M1, DATA_GAP))
    return gaps, counts
