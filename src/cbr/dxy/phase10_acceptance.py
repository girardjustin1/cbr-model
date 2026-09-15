"""Phase 10 DXY context acceptance (CBR-ACC-010) -> reports/phase10-dxy-context.{json,md}.

Usage:
    .venv/bin/python -m cbr.dxy.phase10_acceptance

Runs the DXY context module on every fixture day and AC-11A sample day and checks AC10-01…AC10-10. Holdout-period
fixture days are used for integrity/context only: no trades, no P&L.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.data.futures import load_front
from cbr.data.phase9_acceptance import fixture_days
from cbr.data.sessions import expected_closed_mask
from cbr.dxy import context as cm

ROOT = dk.ROOT
REPORT_JSON = ROOT / "reports" / "phase10-dxy-context.json"
REPORT_MD = ROOT / "reports" / "phase10-dxy-context.md"
SEEDED_TIMES = 300
DX_MOVE_MIN = 0.01
AGREEMENT_CONCERN = 0.80
RULED = [("2020-03-09T20:00:00+00:00", "2020-03-09T21:00:00+00:00"),
         ("2019-03-11T00:00:00+00:00", "2019-03-11T01:00:00+00:00")]
MIN = pd.Timedelta(minutes=1)


class Checks:
    def __init__(self) -> None:
        self.items: dict[str, list] = {}

    def add(self, ac: str, ok: bool, detail) -> None:
        self.items.setdefault(ac, []).append({"ok": bool(ok), "detail": detail})

    def status(self, ac: str) -> str:
        rows = self.items.get(ac, [])
        return "NOT RUN" if not rows else "MET" if all(r["ok"] for r in rows) else "FAIL"


def _days() -> list[tuple[str, date]]:
    return [("fixture", d) for d in fixture_days()] + [(sid, d) for sid, d in dk.SAMPLE_DAYS.items()]


def _frames_equal(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    try:
        pd.testing.assert_frame_equal(a, b, check_dtype=False)
        return True
    except AssertionError:
        return False


def _day(label: str, day: date, dx: pd.DataFrame, dx_range, cfg: dict, chk: Checks) -> dict:
    dxy = pd.read_parquet(dk.NORM / "dollaridxusd" / "candles_1m" / f"{day.isoformat()}.parquet")[["open", "close"]]
    lo = pd.Timestamp(day, tz="UTC")
    loaded = (lo, lo + pd.Timedelta(days=1))
    grid = pd.date_range(lo + MIN, lo + pd.Timedelta(days=1), freq="1min")
    ctx = cm.build_context(dxy, grid, loaded, dx=dx, dx_range=dx_range, cfg=cfg)
    causal = cm.causal_columns(ctx)
    key = f"{label} {day}"

    # AC10-01 UTC
    utc_cols = [c for c in ctx.columns if c.endswith("_utc")]
    chk.add("AC10-01", str(ctx.index.tz) == "UTC" and all(str(ctx[c].dt.tz) == "UTC" for c in utc_cols), key)
    try:
        cm.build_context(dxy.tz_localize(None), grid[:1], loaded, cfg=cfg)
        chk.add("AC10-01", False, f"{key}: naive input accepted")
    except ValueError:
        chk.add("AC10-01", True, f"{key}: naive input rejected")

    # AC10-02 truncation / AC10-03 future mutation
    rng = np.random.default_rng(day.toordinal())
    times = pd.DatetimeIndex(sorted(rng.choice(grid, SEEDED_TIMES, replace=False)))
    trunc_bad, mut_bad = [], []
    for t in times:
        known = dxy[dxy.index + MIN <= t]
        kdx = dx[(dx.index + MIN <= t)]
        one = cm.build_context(known, pd.DatetimeIndex([t]), loaded, dx=kdx, dx_range=dx_range, cfg=cfg,
                               hindsight=False)
        if not _frames_equal(one[causal], ctx.loc[[t], causal]):
            trunc_bad.append(str(t))
        fut = dxy.copy()
        after = fut.index + MIN > t
        fut.loc[after, ["open", "close"]] = fut.loc[after, ["open", "close"]] * 1.03 + 0.5
        fut = fut.drop(fut.index[after][::4])
        mdx = dx.copy()
        mdx.loc[(mdx.index + MIN > t) & (mdx.index < loaded[1] + pd.Timedelta(hours=2)), "volume"] = 0.0
        mut = cm.build_context(fut, pd.DatetimeIndex([t]), loaded, dx=mdx, dx_range=dx_range, cfg=cfg,
                               hindsight=False)
        if not _frames_equal(mut, ctx.loc[[t], causal]):
            mut_bad.append(str(t))
    chk.add("AC10-02", not trunc_bad, {"day": key, "times": SEEDED_TIMES, "mismatches": trunc_bad[:5]})
    chk.add("AC10-03", not mut_bad, {"day": key, "times": SEEDED_TIMES, "mismatches": mut_bad[:5]})

    # AC10-04 causal invariants + hindsight on ruled intervals
    viol = []
    for tf in cfg["timeframes"]:
        for kind in ("last", "forming"):
            p = f"dxy_{tf}_{kind}_"
            has_dir = ctx[p + "direction"].notna()
            if (has_dir & ctx[p + "state"].isin(["VENDOR_MISSING", "NO_QUOTES", "CLOSED_SCHEDULE", "NOT_LOADED",
                                                 "NO_ELAPSED_TIME"])).any():
                viol.append(f"{p}: direction on an unavailable window")
            if (has_dir & (ctx[p + "rows"] == 0)).any():
                viol.append(f"{p}: direction without rows")
    avail = ctx[ctx["dxy_available"]]
    if (avail["dxy_quote_age_s"] > cfg["max_quote_age_minutes"] * 60).any():
        viol.append("quote carried beyond max age")
    closed = expected_closed_mask(pd.date_range(lo - pd.Timedelta(hours=1), lo + pd.Timedelta(days=1), freq="1min",
                                                inclusive="left"))
    base = lo - pd.Timedelta(hours=1)
    for t, row in avail.iterrows():
        a = int((row["dxy_quote_close_utc"] - base) // MIN)
        b = int((t - base) // MIN)
        if closed[a:b].any():
            viol.append(f"quote carried across session closure at {t}")
            break
    chk.add("AC10-04", not viol, {"day": key, "violations": viol})
    ruled_detail = []
    for s, e in RULED:
        s_, e_ = pd.Timestamp(s), pd.Timestamp(e)
        if s_.date() != day:
            continue
        inside = ctx[(ctx.index > s_) & (ctx.index <= e_)]
        mask_ok = bool(inside["dq_hindsight_vendor_gap"].all())
        shown = int(inside["dxy_available"].sum())
        ruled_detail.append({"interval": [s, e], "hindsight_mask_all_minutes": mask_ok,
                             "causal_quote_shown_minutes": shown,
                             "causal_quote_shown_max_age_s": float(inside.loc[inside["dxy_available"],
                                                                              "dxy_quote_age_s"].max() or 0)})
        chk.add("AC10-04", mask_ok and shown <= cfg["max_quote_age_minutes"], {"day": key, "ruled": ruled_detail[-1]})

    # AC10-04b hindsight isolation
    chk.add("AC10-04b", _frames_equal(cm.build_context(dxy, grid, loaded, dx=dx, dx_range=dx_range, cfg=cfg,
                                                       hindsight=False), ctx[causal]), key)

    # AC10-05 no DX substitution
    garbage = dx.copy()
    garbage[["open", "high", "low", "close"]] = 999.0
    same = _frames_equal(cm.build_context(dxy, grid, loaded, dx=garbage, dx_range=dx_range, cfg=cfg), ctx)
    nodx = cm.build_context(dxy, grid, loaded, cfg=cfg, hindsight=False)
    num = [c for c in causal if ctx[c].dtype.kind == "f"]
    only_removes = all(((ctx[c] == nodx[c]) | ctx[c].isna()).all() for c in num)
    chk.add("AC10-05", same and only_removes, {"day": key, "dx_prices_irrelevant": same, "dx_only_removes": only_removes})

    # AC10-06 closure labelling
    bad = []
    for tf, mins in cfg["timeframes"].items():
        p = f"dxy_{tf}_last_"
        for t, row in ctx.iterrows():
            if row[p + "state"] in ("NOT_LOADED", "NO_ELAPSED_TIME"):
                continue
            a = int((row[p + "open_utc"] - base) // MIN)
            all_closed = bool(closed[a:a + mins].all())
            if all_closed != (row[p + "state"] == "CLOSED_SCHEDULE"):
                bad.append(f"{tf} {t}")
                break
    chk.add("AC10-06", not bad, {"day": key, "mismatches": bad})

    # AC10-07 naive recomputation of directions
    wrong = 0
    checked = 0
    for tf, mins in cfg["timeframes"].items():
        p = f"dxy_{tf}_last_"
        at_close = ctx[(ctx.index.minute % mins == 0) & ctx[p + "direction"].notna()]
        for _, row in at_close.iterrows():
            o = row[p + "open_utc"]
            w = dxy[(dxy.index >= o) & (dxy.index < o + pd.Timedelta(minutes=mins))]
            mv = float(w["close"].iloc[-1] - w["open"].iloc[0])
            d = "UP" if mv > cfg["flat_epsilon"] else "DOWN" if mv < -cfg["flat_epsilon"] else "FLAT"
            checked += 1
            wrong += int(d != row[p + "direction"] or not np.isclose(mv, row[p + "move"]))
    chk.add("AC10-07", wrong == 0, {"day": key, "windows_checked": checked, "wrong": wrong})

    # AC10-08 determinism
    again = cm.build_context(dxy, grid, loaded, dx=dx, dx_range=dx_range, cfg=cfg)
    h1, h2 = cm.context_hash(ctx), cm.context_hash(again)
    chk.add("AC10-08", h1 == h2, {"day": key, "hash": h1})

    # AC10-09 reference coverage flags
    has_ref = bool(dx_range[0] <= lo)
    unverified = int(ctx["dxy_reason_codes"].str.contains("DX_REFERENCE_UNAVAILABLE").sum())
    chk.add("AC10-09", (unverified == 0) if has_ref else (unverified > 0),
            {"day": key, "dx_reference": has_ref, "decision_times_with_DX_REFERENCE_UNAVAILABLE": unverified})

    # AC10-10 comparison vs DX (reporting)
    comp = {}
    if has_ref:
        dxd = dx[(dx.index >= lo) & (dx.index < loaded[1]) & (dx["volume"] > 0)][["open", "close"]]
        dctx = cm.build_context(dxd, grid, loaded, cfg=cfg, hindsight=False)
        for tf, mins in cfg["timeframes"].items():
            p = f"dxy_{tf}_last_"
            sel = ((ctx.index.minute % mins == 0) & (ctx[p + "confidence"] == "FULL")
                   & (dctx[p + "confidence"] == "FULL") & (dctx[p + "move"].abs() >= DX_MOVE_MIN))
            n = int(sel.sum())
            agree = int((ctx.loc[sel, p + "direction"] == dctx.loc[sel, p + "direction"]).sum())
            comp[tf] = {"windows": n, "agree": agree}

    dist = {}
    for tf in cfg["timeframes"]:
        for kind in ("last", "forming"):
            p = f"dxy_{tf}_{kind}_"
            dist[f"{tf}_{kind}"] = {"states": ctx[p + "state"].value_counts().to_dict(),
                                    "confidence": ctx[p + "confidence"].value_counts().to_dict()}
    quote = {"available_share": round(float(ctx["dxy_available"].mean()), 4),
             "confidence": ctx["dxy_confidence"].value_counts().to_dict(),
             "age_s_p50_p95_when_available": [float(avail["dxy_quote_age_s"].quantile(x)) for x in (.5, .95)]
             if len(avail) else None}
    unavailable_by_hour = (ctx["dxy_15m_last_confidence"] == "UNAVAILABLE").groupby(ctx.index.hour).sum()
    asia_h1 = ctx[(ctx.index > lo + pd.Timedelta(minutes=15)) & (ctx.index <= lo + pd.Timedelta(hours=1))]
    asia_h1_no_dxy = int(asia_h1["dxy_15m_last_state"].isin(["NO_QUOTES", "VENDOR_MISSING"]).sum())
    return {"label": label, "day": day.isoformat(), "rows": len(ctx), "hash": h1, "dx_reference": has_ref,
            "utc_offset_ny": int(pd.Timestamp(day, tz="America/New_York").utcoffset().total_seconds() // 3600),
            "unavailable_15m_last_by_utc_hour": {int(k): int(v) for k, v in unavailable_by_hour.items() if v},
            "asia_hour1_decisions_without_dxy_quotes": asia_h1_no_dxy, "weekday": day.weekday(),
            "comparison_vs_dx": comp, "distributions": dist, "quote": quote, "ruled_intervals": ruled_detail}


def evaluate() -> dict:
    cfg = cm.load_config()
    dx = load_front("dx_front_ohlcv1m")
    dx_range = (dx.index.min(), dx.index.max() + MIN)
    chk = Checks()
    days = [_day(label, d, dx, dx_range, cfg, chk) for label, d in _days()]
    for tf in cfg["timeframes"]:
        n = sum(d["comparison_vs_dx"].get(tf, {}).get("windows", 0) for d in days)
        a = sum(d["comparison_vs_dx"].get(tf, {}).get("agree", 0) for d in days)
        rate = a / n if n else None
        chk.add("AC10-10", rate is not None and rate >= AGREEMENT_CONCERN,
                {"timeframe": tf, "windows": n, "agree": a, "rate": round(rate, 4) if rate is not None else None})
    chk.add("AC10-09", len(days) == len(_days()) == 24, {"days_processed": len(days)})
    criteria = ["AC10-01", "AC10-02", "AC10-03", "AC10-04", "AC10-04b", "AC10-05", "AC10-06", "AC10-07", "AC10-08",
                "AC10-09"]
    status = {c: chk.status(c) for c in criteria}
    status["AC10-10"] = "MET" if chk.status("AC10-10") == "MET" else "CONCERN"
    concerns = _concerns(days, cfg, status)
    if any(v != "MET" for k, v in status.items() if k != "AC10-10"):
        verdict = "FAIL"
    elif concerns or status["AC10-10"] != "MET":
        verdict = "PASS WITH CONCERNS"
    else:
        verdict = "PASS"
    return {"generated_utc": datetime.now(UTC).isoformat(), "config": cfg, "verdict": verdict, "criteria": status,
            "concerns": concerns, "checks": chk.items, "days": days}


def _concerns(days: list[dict], cfg: dict, status: dict) -> list[str]:
    """Documented limitations affecting later use (CBR-ACC-010 §4), each computed from this run."""
    out = []
    shown = [x for d in days for x in d["ruled_intervals"] if x["causal_quote_shown_minutes"]]
    if shown:
        out.append(f"Causal quote shown for up to {max(x['causal_quote_shown_minutes'] for x in shown)} decision minutes "
                   f"at the start of a ruled vendor outage (max age {cfg['max_quote_age_minutes']} min, REDUCED "
                   "confidence) before it becomes UNAVAILABLE; hindsight mask marks the full outage. Ledger use: OQ-31.")
    est = [d for d in days if d["utc_offset_ny"] == -5 and d["weekday"] != 6]        # Sundays are closed anyway
    asia = [d for d in est if d["asia_hour1_decisions_without_dxy_quotes"]]
    if asia:
        out.append(f"On {len(asia)} of {len(est)} EST (winter) trading days, last-closed 15m DXY context has no quotes "
                   "(NO_QUOTES/VENDOR_MISSING) for decision times 00:15-01:00 UTC (Asia hour 1, tradable after NT_SYDNEY): "
                   "the CFD does not quote 18:00-20:00 New York. CBR setups there will carry DXY UNAVAILABLE.")
    out.append("Report artifact, not a data property: each day file starts at 00:00 UTC, so windows reaching back before "
               "00:00 are NOT_LOADED for the first 15 (15m) / 60 (1h) decision minutes of every test day. Contiguous "
               "multi-day loads (engine use) don't have this.")
    reduced = sum(sum(d["distributions"][f"{tf}_last"]["confidence"].get("REDUCED", 0) for tf in cfg["timeframes"])
                  for d in days if d["day"] < "2020-01-01")
    if reduced:
        out.append(f"{reduced} last-closed window decision times REDUCED (low coverage) on 2018-2019 days: early DXY CFD "
                   "quoting is thinner (Phase 9: 16-20% zero 1m returns in 2019).")
    out.append("IMPL thresholds (flat_epsilon 0, min_coverage_full 0.5, max_quote_age 10 min) validated on 24 days only; "
               "revalidate on AC-11B history before baseline use.")
    out.append("No DXY highs/lows, extension extremes, range condition or DXY shifts: those need OQ-25 and remain "
               "Phase 17/18 ablation inputs; 1m/5s DXY structure excluded (D12-6).")
    return out


def render_md(r: dict) -> str:
    lines = ["# Phase 10 DXY Context Acceptance Report", "",
             f"Generated {r['generated_utc']} by `src/cbr/dxy/phase10_acceptance.py` against CBR-ACC-010 v1.0.", "",
             f"## Verdict: **{r['verdict']}**", "", "| Criterion | Status |", "|---|---|",
             *[f"| {k} | {v} |" for k, v in r["criteria"].items()], "",
             "## Concerns", "", *[f"- {c}" for c in r["concerns"]], "",
             "## AC10-10: last-closed direction agreement vs DX (FULL on both, |DX move| ≥ 0.01)", ""]
    lines += [f"- {c['detail']['timeframe']}: {c['detail']['agree']} / {c['detail']['windows']} = {c['detail']['rate']}"
              for c in r["checks"].get("AC10-10", [])]
    lines += ["", "## Ruled vendor-gap intervals (D12-1, D12-2)", ""]
    for d in r["days"]:
        for x in d["ruled_intervals"]:
            lines.append(f"- {x['interval'][0]} → {x['interval'][1]}: hindsight mask on every minute = "
                         f"{x['hindsight_mask_all_minutes']}; causal quote still shown for "
                         f"{x['causal_quote_shown_minutes']} decision minutes (max age {x['causal_quote_shown_max_age_s']:.0f} s)")
    lines += ["", "## Per-day summary", "",
              "| Day | DX ref | Quote available | 15m last FULL/REDUCED/UNAVAIL | 1h last FULL/REDUCED/UNAVAIL | 15m agree | 1h agree | Hash |",
              "|---|---|---|---|---|---|---|---|"]
    def cc(day: dict, k: str) -> str:
        c = day["distributions"][k]["confidence"]
        return f"{c.get('FULL', 0)}/{c.get('REDUCED', 0)}/{c.get('UNAVAILABLE', 0)}"

    def ag(day: dict, tf: str) -> str:
        comp = day["comparison_vs_dx"]
        return f"{comp[tf]['agree']}/{comp[tf]['windows']}" if tf in comp else "—"

    for d in r["days"]:
        lines.append(f"| {d['label']} {d['day']} | {d['dx_reference']} | {d['quote']['available_share']} | "
                     f"{cc(d, '15m_last')} | {cc(d, '1h_last')} | {ag(d, '15m')} | {ag(d, '1h')} | `{d['hash'][:12]}` |")
    lines += ["", "## Last-closed 15m UNAVAILABLE decision minutes by UTC hour", "",
              "| Day | NY offset | Hours (UTC: minutes) |", "|---|---|---|"]
    for d in r["days"]:
        hrs = ", ".join(f"{h:02d}: {n}" for h, n in d["unavailable_15m_last_by_utc_hour"].items())
        lines.append(f"| {d['label']} {d['day']} | {d['utc_offset_ny']} | {hrs} |")
    lines += ["", "## Check details", ""]
    for ac, items in r["checks"].items():
        failed = [i for i in items if not i["ok"]]
        lines.append(f"- {ac}: {len(items) - len(failed)} / {len(items)} passed"
                     + (f"; failures: {failed[:3]}" if failed else ""))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    r = evaluate()
    REPORT_JSON.write_text(json.dumps(r, indent=2, default=str) + "\n")
    REPORT_MD.write_text(render_md(r))
    print("VERDICT:", r["verdict"])
    for k, v in r["criteria"].items():
        print(f"  {k}: {v}")
    for c in r["checks"].get("AC10-10", []):
        print("  AC10-10", c["detail"])


if __name__ == "__main__":
    main()
