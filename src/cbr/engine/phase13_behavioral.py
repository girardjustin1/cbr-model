"""Phase 13 behavioral-parity run (CBR-PROT-013B, owner ruling D25; run specification config/phase13_behavioral_run.yaml).

Usage (in this order; each step refuses to run out of order):
    .venv/bin/python -m cbr.engine.phase13_behavioral freeze        # hashes + full test suite -> reports/phase13-freeze-manifest.json
    .venv/bin/python -m cbr.engine.phase13_behavioral fetch         # Dukascopy ticks for the D25-P2 days (after the freeze)
    .venv/bin/python -m cbr.engine.phase13_behavioral run 1         # complete run 1 -> data/phase13/run-1.json
    .venv/bin/python -m cbr.engine.phase13_behavioral run 2         # complete repeat from the same frozen inputs
    .venv/bin/python -m cbr.engine.phase13_behavioral report        # determinism check, verdict, reports/phase13-*

Signal state only: no fills, trade outcomes, P&L or optimization. PC2 is frozen; nothing here changes an engine rule.
Candidate selection is `parity.select_candidate` (pinned in PC2) and never reads course values; course values from the
frozen run specification are read only when an already-selected candidate is compared with the example.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from cbr.data import canonical_bars as cb
from cbr.data import dukascopy_fetch as dk
from cbr.data import feed_comparison as fc
from cbr.data import v1_dukascopy_readiness as readiness
from cbr.data.futures import load_front
from cbr.dxy import context as dxy_ctx
from cbr.engine import cbr1h, parity
from cbr.engine.common import M1, S5, anchor_at
from cbr.engine.params import ROOT, load_cbr1h, spec_hash
from cbr.structure.swings import legs

RUN_SPEC = ROOT / "config" / "phase13_behavioral_run.yaml"
FREEZE_MANIFEST = ROOT / "reports" / "phase13-freeze-manifest.json"
RUN_DIR = ROOT / "data" / "phase13"
REPORTS = ROOT / "reports"
H1 = pd.Timedelta(hours=1)
FDSD = "FEED_DEPENDENT_SIGNAL_DIFFERENCE"
BM, BMFD = "BEHAVIORAL_MATCH", "BEHAVIORAL_MATCH_WITH_FEED_DIFFERENCE"
MATCH, FEED, MISMATCH, NA = "MATCH", "FEED_DIFFERENCE", "MISMATCH", "NOT_APPLICABLE"
HARD = ["model_family", "direction", "extension_direction", "core_structural_trigger"]
FROZEN_FILES = [
    "docs/governance/phase13-behavioral-parity-protocol.md", "docs/governance/d25-phase13-run-approval.md",
    "config/phase13_behavioral_run.yaml", "docs/acceptance/phase13-acceptance-criteria.md",
    "docs/governance/phase13-parity-protocol.md", "docs/governance/d24-phase13-fidelity-revision.md",
    "docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC2.yaml", "docs/strategy/parity-candidates/CBR15_BASELINE_V1-PC2.yaml",
    "research/examples/course_examples.jsonl", "src/cbr/engine/parity.py", "src/cbr/engine/phase13_behavioral.py",
    "src/cbr/data/feed_comparison.py", "src/cbr/data/dukascopy_fetch.py", "src/cbr/data/canonical_bars.py",
    "src/cbr/data/v1_dukascopy_readiness.py", "src/cbr/dxy/context.py", "config/dxy_context.yaml",
    "config/data_quality.yaml", "tests/engine/test_phase13_behavioral.py", "tests/test_feed_comparison.py",
    "docs/governance/phase13-run-incident-1.md",
]
T = lambda s: pd.Timestamp(s).tz_convert("UTC")


# ------------------------------------------------------------------ spec, hashing, JSON

def load_spec() -> dict:
    return yaml.safe_load(RUN_SPEC.read_text())


def sha(path: Path | str) -> str:
    return hashlib.sha256((ROOT / path if not Path(path).is_absolute() else Path(path)).read_bytes()).hexdigest()


def js(obj):
    """JSON-safe, deterministic representation (timestamps ISO, numpy scalars native, NaN → None)."""
    if isinstance(obj, dict):
        return {str(k): js(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [js(v) for v in obj]
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, pd.Timedelta):
        return obj.total_seconds()
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return None if math.isnan(obj) else float(obj)
    if obj is pd.NaT:
        return None
    return obj


def payload_hash(obj) -> str:
    return hashlib.sha256(json.dumps(js(obj), sort_keys=True).encode()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def recent_tick_paths(spec: dict) -> list[Path]:
    return [dk.RAW / "xauusd" / "ticks" / f"{d}.parquet" for d in spec["recent_feed_comparison"]["days"]]


# ------------------------------------------------------------------ freeze (D25-F)

def freeze(pytest_summary: str | None = None) -> dict:
    """Record hashes of the protocol, ruling, run spec, PC2, course truth, selection code, taxonomy code and run code,
    plus the full pre-execution test result. Refuses when already frozen, when the tree has uncommitted changes, when
    PC2 no longer matches its pinned hash, or when recent Dukascopy data already exists (dates freeze before download)."""
    if FREEZE_MANIFEST.exists():
        raise SystemExit(f"{FREEZE_MANIFEST.relative_to(ROOT)} exists: already frozen (a change needs a new run id)")
    spec = load_spec()
    if _git("status", "--porcelain"):
        raise SystemExit("uncommitted changes: commit the run code before freezing (protocol §8.2)")
    pc2 = yaml.safe_load((ROOT / spec["spec_under_test"]["record"]).read_text())
    if not (pc2["spec_hash"] == spec_hash() == spec["spec_under_test"]["spec_hash"]):
        raise SystemExit("PC2 spec hash mismatch: pinned files changed")
    present = [p for p in recent_tick_paths(spec) if p.exists()]
    prior = spec.get("recent_data_fetched_under_superseded_freeze") or {}
    data_note = {"recent_dukascopy_absent_at_freeze": not present}
    if present:
        # Only a documented superseded freeze may have fetched them (incident record), with unchanged hashes and no
        # run output from any run.
        sup = spec.get("supersedes") or {}
        bad = [p.name for p in present if prior.get(p.stem) != sha(p)]
        if not prior or bad or len(present) != len(prior) or not (ROOT / sup.get("manifest", "missing")).exists():
            raise SystemExit(f"recent Dukascopy data present without a matching superseded-freeze record: {bad or present}")
        if RUN_DIR.exists() and any(RUN_DIR.glob("run-*.json")):
            raise SystemExit("run output exists: results were produced, a re-freeze isn't allowed")
        data_note.update({"recent_dukascopy_fetched_under": sup["run_id"], "recent_tick_hashes_verified": True})
    if pytest_summary is None:
        res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True, check=False)
        pytest_summary = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-400:]
        if res.returncode != 0:
            raise SystemExit(f"pre-execution test suite failed: {pytest_summary}")
    lint = subprocess.run([str(ROOT / ".venv" / "bin" / "ruff"), "check", "src", "tests"], cwd=ROOT, capture_output=True,
                          text=True, check=False)
    rec = {
        "run_id": spec["run_id"], "frozen_utc": datetime.now(UTC).replace(microsecond=0).isoformat(), "ruling": "D25",
        "git_commit": _git("rev-parse", "HEAD"), "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "files": {f: sha(f) for f in FROZEN_FILES},
        "pc2": {"record": spec["spec_under_test"]["record"], "spec_hash": pc2["spec_hash"],
                "spec_files": pc2["spec_files"], "selection_protocol": pc2["selection_protocol"]["files"]},
        "frozen_items": {
            "recent_days": spec["recent_feed_comparison"]["days"],
            "course_examples": {k: v["role"] for k, v in spec["examples"].items()},
            "candidate_selection": spec["candidate_selection"], "mismatch_taxonomy": spec["classification"]["order"],
            "structural_event_match": spec["structural_event_match"], "feed_band": spec["feed_band"],
            "acceptance": {"criterion_9": spec["criterion_9"], "verdict": spec["verdict"]}},
        **data_note, "supersedes": spec.get("supersedes"),
        "pre_execution_tests": pytest_summary, "lint": lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else "",
        "forexcom_exports": {f: sha(f) for f in sorted({*spec["recent_feed_comparison"]["forexcom_files"].values(),
                                                         *spec["higher_timeframe"]["forexcom_files"].values(),
                                                         spec["higher_timeframe"]["dxy_file"]})},
    }
    FREEZE_MANIFEST.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def verify_freeze() -> dict:
    if not FREEZE_MANIFEST.exists():
        raise SystemExit("not frozen: run `freeze` first")
    rec = json.loads(FREEZE_MANIFEST.read_text())
    changed = [f for f, h in {**rec["files"], **rec["pc2"]["spec_files"], **rec["pc2"]["selection_protocol"],
                              **rec["forexcom_exports"]}.items() if sha(f) != h]
    if changed or spec_hash() != rec["pc2"]["spec_hash"]:
        raise SystemExit(f"frozen inputs changed after the freeze: {changed or 'PC2 spec hash'}")
    return rec


# ------------------------------------------------------------------ data (D25-E1)

def fetch() -> dict:
    verify_freeze()
    spec = load_spec()
    days = [pd.Timestamp(d).date() for d in spec["recent_feed_comparison"]["days"]]
    dk.fetch(days, ["xauusd"])
    paths = [p for p in recent_tick_paths(spec) if p.exists()]
    cb.build(paths)
    return {p.name: sha(p) for p in paths}


def data_hashes(spec: dict) -> dict:
    canon = json.loads(cb.MANIFEST.read_text())["files"]
    out = {"course_structure_bars": {}, "recent_ticks": {}, "recent_structure_bars": {}, "dxy_candles": {}}
    days = sorted({d.date().isoformat() for x in spec["examples"].values()
                   for d in pd.date_range(T(x["data_span_utc"][0]).floor("D"), T(x["data_span_utc"][1]), freq="D", inclusive="left")})
    for d in days:
        for tag in ("1m", "5s"):
            p = cb.OUT / f"structure_{tag}" / f"{d}.parquet"
            if p.exists():
                rel = str(p.relative_to(ROOT))
                out["course_structure_bars"][rel] = {"sha256": sha(p), "manifest_match": canon.get(rel, {}).get("sha256") == sha(p)}
    for d in spec["recent_feed_comparison"]["days"]:
        t = dk.RAW / "xauusd" / "ticks" / f"{d}.parquet"
        out["recent_ticks"][str(t.relative_to(ROOT))] = sha(t) if t.exists() else None
        for tag in ("1m", "5s"):
            p = cb.OUT / f"structure_{tag}" / f"{d}.parquet"
            out["recent_structure_bars"][str(p.relative_to(ROOT))] = sha(p) if p.exists() else None
    for x in spec["examples"].values():
        d = T(x["hour_utc"]).date().isoformat()
        p = dk.NORM / "dollaridxusd" / "candles_1m" / f"{d}.parquet"
        out["dxy_candles"][str(p.relative_to(ROOT))] = sha(p) if p.exists() else None
    dxf = ROOT / "data" / "raw" / "databento" / "dx_front_ohlcv1m.parquet"
    out["dx_front"] = {str(dxf.relative_to(ROOT)): sha(dxf)}
    return out


# ------------------------------------------------------------------ feed studies (D25-E2, E3)

def recent_study(spec: dict, p) -> tuple[dict, float]:
    rs = spec["recent_feed_comparison"]
    minutes = fc.comparison_minutes(rs["days"], T(rs["start_utc"]))
    validation = {d: readiness.day_readiness(d) for d in rs["days"]}
    dk1m = pd.concat([pd.read_parquet(cb.OUT / "structure_1m" / f"{d}.parquet") for d in rs["days"]]).sort_index()
    fx = {tf: parity.load_tradingview_csv(ROOT / path) for tf, path in rs["forexcom_files"].items()}
    fx1m, dk1m_r = fc.restrict(fx["1m"], minutes), fc.restrict(dk1m, minutes)
    study = fc.compare_recent(fx1m, dk1m_r, minutes, p, exports={"5m": fx["5m"], "15m": fx["15m"]},
                              band=spec["feed_band"] | {}, hour_minutes=rs["hourly_evaluation_minutes"],
                              count_margin=pd.Timedelta(hours=2), lag_range=spec["feed_band"]["lag_range_minutes"],
                              report_percentile=spec["feed_band"]["also_report_percentile"])
    study["data_validation"] = {d: {k: v[k] for k in ("ready", "problems", "vendor_gap_minutes", "ticks", "structure_1m",
                                                      "structure_5s", "session") if k in v} for d, v in validation.items()}
    c9 = spec["criterion_9"]
    study["criterion_9"] = fc.criterion_9(study, c9["core_concepts"], c9["fail_evidence_if_rate_below"],
                                          c9["concern_if_rate_below"])
    return study, study["feed_band"]["tau_usd"]


def htf_study(spec: dict) -> dict:
    h = spec["higher_timeframe"]
    fx = {tf: parity.load_tradingview_csv(ROOT / path) for tf, path in h["forexcom_files"].items()}
    tvc = parity.load_tradingview_csv(ROOT / h["dxy_file"])
    out = {}
    for ex_id, x in spec["examples"].items():
        if x["role"] != "POSITIVE":
            continue
        hour = T(x["hour_utc"])
        a, b = T(x["data_span_utc"][0]), hour + pd.Timedelta(days=2)
        dk1m = cb.load_structure(a, b, "1m")
        rec = fc.htf_example(hour, dk1m, fx, h["course_hours_pm"], h["course_4h_pm_hours"])
        cfd_path = dk.NORM / "dollaridxusd" / "candles_1m" / f"{hour.date().isoformat()}.parquet"
        cfd = pd.read_parquet(cfd_path)[["open", "close"]] if cfd_path.exists() else None
        rec["dxy_1h"] = fc.dxy_example(hour, tvc, cfd, h["course_hours_pm"])
        out[ex_id] = rec
    return out


# ------------------------------------------------------------------ engine runs (D25-E4, E5)

def view_label(view: str, ablation: dict | None) -> str:
    return view if not ablation else f"{view}:{next(iter(ablation))}={next(iter(ablation.values()))}"


def engine_runs(x: dict, spec: dict) -> dict:
    a, b = T(x["data_span_utc"][0]), T(x["data_span_utc"][1])
    h0 = T(x["hour_utc"])
    s1m, s5s = cb.load_structure(a, b, "1m"), cb.load_structure(a, b, "5s")
    runs = {}
    for variant in spec["variants"]:
        for view, ablations in spec["views"].items():
            for ab in ablations:
                params = parity.view_params(load_cbr1h(variant), view, ab)
                results = [cbr1h.run_cbr1h(s1m, s5s, start=h0, end=h0 + H1, variant=variant, params=params)
                           for _ in range(spec["engine_run_repeats"])]
                hashes = [cbr1h.result_hash(r) for r in results]
                runs[(variant, view_label(view, ab))] = {"result": results[0], "params": params, "hashes": hashes,
                                                         "identical": len(set(hashes)) == 1}
    return {"s1m": s1m, "s5s": s5s, "runs": runs}


def evaluated_candidate(cands: pd.DataFrame, variant: str, params) -> tuple[pd.Series | None, str]:
    """Protocol §2.3: selected ARMED → DIAGNOSTIC_ONLY → DIAGNOSTIC_FIRST_IN_ORDER. Engine information only."""
    sel = parity.select_candidate(cands, variant, params)
    c = cands[cands["variant"] == variant] if len(cands) else cands
    by_id = {r["signal_id"]: r for _, r in c.iterrows()} if len(c) else {}
    if sel["selected"]:
        return by_id[sel["selected"]], "SELECTED_ARMED"
    if sel["diagnostic_only"]:
        return by_id[sel["diagnostic_only"]["signal_id"]], "DIAGNOSTIC_ONLY"
    if len(c):
        return min((r for _, r in c.iterrows()), key=parity.selection_key), "DIAGNOSTIC_FIRST_IN_ORDER"
    return None, "NO_CANDIDATE"


def _t(v):
    return None if v is None or (not isinstance(v, pd.Timestamp) and pd.isna(v)) else pd.Timestamp(v)


def _f(v) -> float | None:
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)


def identity(row: pd.Series) -> tuple:
    return (row["variant"], row["direction"], _t(row["five_second_sweep_time"]), round(float(row["five_second_shift_level"]), 6))


def find_same(cands: pd.DataFrame, row: pd.Series) -> pd.Series | None:
    if not len(cands):
        return None
    key = identity(row)
    for _, r in cands.iterrows():
        if identity(r) == key:
            return r
    return None


def engine_facts(row: pd.Series | None) -> dict | None:
    if row is None:
        return None
    shift = _t(row["five_second_shift_time"])
    anchor = anchor_at(row, shift) if shift is not None else row["structure_stop_anchor"]
    keys = ["signal_id", "variant", "event", "rules_failed", "rules_not_evaluated", "timestamp", "direction", "entry_model",
            "parent_structure_type", "condition", "c_med", "n_legs", "cond_direction", "condition_tradable_minutes",
            "condition_missing_minutes", "range_high", "range_low", "pos_oe_extreme", "er_pro", "beyond_external", "oe_dir",
            "ext_extreme_at_decision", "oe_extreme_time", "oe_origin_time", "oe_size", "oe_size_atr1h", "oe_duration_min",
            "oe_no_pullback", "oe_two_sided", "oe_opposite_wick", "atr_1m", "atr_1h", "hvcs_minutes", "continuity_state",
            "q_open_utc", "q_prev_high", "q_prev_low", "q_break_by_q", "q_prev_closed_in_trade_direction",
            "five_second_sweep_time", "five_second_shift_level", "five_second_shift_time", "five_second_swept_price",
            "five_second_broken_price", "sweep_bar_extreme", "s5_t3_end", "m1_hilo_armed_at_decision", "activation_time",
            "valid_until", "timing30_state", "structure_stop_anchor", "stop_anchor_time", "stop_buffer_price",
            "h_open", "target_at_decision", "target_at_activation", "cancel_time", "cancel_reason", "prior_setup_count",
            "h_missing_minutes"]
    out = {k: row.get(k) for k in keys}
    out["rules"] = dict(row["rules"])
    out["stop_anchor_at_shift"] = anchor
    out["target_at_shift"] = None if anchor is None else anchor - 0.5 * (anchor - row["h_open"])
    return js(out)


# ------------------------------------------------------------------ margins (protocol §6)

def oe_pullback_margin(s1m: pd.DataFrame, h0, h_open: float, as_of, atr_1m: float, p) -> float | None:
    """Smallest (pullback threshold − pullback) along the path to the extreme, HOUR_OPEN origin (same loop as
    `overextension.evaluate`). Positive = no 50% pullback; negative = the rule failed by that much."""
    inside = s1m[(s1m.index >= h0) & (s1m.index + M1 <= as_of)]
    if inside.empty:
        return None
    up, down = float(inside["high"].max()) - h_open, h_open - float(inside["low"].min())
    sign = 1 if up >= down else -1
    favour, against = (inside["high"], inside["low"]) if sign == 1 else (inside["low"], inside["high"])
    ext_t = favour.idxmax() if sign == 1 else favour.idxmin()
    running, best = h_open, None
    for t in inside.loc[:ext_t].index:
        ext = sign * (running - h_open)
        if ext >= p.activation_atr * atr_1m and ext > 0:
            m = p.pullback_frac * ext - sign * (running - against.loc[t])
            best = m if best is None else min(best, m)
        if sign * (favour.loc[t] - running) > 0:
            running = float(favour.loc[t])
    return best


def margins(row: pd.Series, s1m: pd.DataFrame, s5s: pd.DataFrame, sw_mtf: pd.DataFrame, p) -> dict:
    """Dukascopy margins: how far price was from flipping each margin-testable rule at the decision (USD)."""
    sell = row["direction"] == "SELL"
    as_of, h0, q0 = row["timestamp"], row["hour_open_utc"], row["q_open_utc"]
    ext = row["ext_extreme_at_decision"]
    out: dict[str, float | None] = {}
    q5 = s5s[(s5s.index >= q0) & (s5s.index + S5 <= as_of)]
    if _f(row["q_prev_high"]) is None or not len(q5):
        out["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] = None
    else:
        out["M1H-6A-2-PREV-15M-BROKEN-BY-Q"] = (float(q5["high"].max()) - row["q_prev_high"] if sell
                                                else row["q_prev_low"] - float(q5["low"].min()))
    m1 = s1m[(s1m.index >= h0) & (s1m.index + M1 <= as_of)]
    before, inq = m1[m1.index < q0], m1[m1.index >= q0]
    out["M1H-6A-3-NEW-EXTREME-IN-Q"] = (None if not len(before) or not len(inq) else
                                        (float(inq["high"].max()) - float(before["high"].max()) if sell
                                         else float(before["low"].min()) - float(inq["low"].min())))
    up = float(m1["high"].max()) - row["h_open"] if len(m1) else None
    down = row["h_open"] - float(m1["low"].min()) if len(m1) else None
    out["extension_direction"] = None if up is None else (up - down if sell else down - up)
    out["M1H-OE-02"] = oe_pullback_margin(s1m, h0, row["h_open"], as_of, _f(row["atr_1m"]) or 0.0, p)
    size = row["oe_size"]
    out["M1H-OE-04a"] = p.two_sided_frac * size - row["oe_opposite_wick"] * size
    out["M1H-OE-04b"] = None if _f(row["atr_1h"]) is None else size - p.oe_min_size_atr * row["atr_1h"]
    hi, lo = _f(row["range_high"]), _f(row["range_low"])
    out["M1H-LOC-01"] = None
    if row["condition"] == "RANGE" and hi is not None and lo is not None:
        out["M1H-LOC-01"] = (ext - (lo + p.range_extreme * (hi - lo)) if sell else (lo + (1 - p.range_extreme) * (hi - lo)) - ext)
    known = sw_mtf[sw_mtf["confirmed_at"] <= as_of]
    out["M1H-LOC-02"] = out["M1H-LOC-03"] = None
    if row["condition"] == "TRENDING_RANGE" and row["cond_direction"] != "NONE":
        if sell == (row["cond_direction"] == "UP"):
            last = known[known["kind"] == ("H" if sell else "L")]
            if len(last):
                out["M1H-LOC-02"] = ext - float(last["price"].iloc[-1]) if sell else float(last["price"].iloc[-1]) - ext
        else:
            lg = legs(known)
            lg = lg[lg["dir"] == (1 if row["cond_direction"] == "UP" else -1)]
            if len(lg) and lg.iloc[-1]["size"]:
                leg = lg.iloc[-1]
                er = abs(ext - leg["p_end"]) / leg["size"]
                out["M1H-LOC-03"] = min(er - p.pro_er_min, p.pro_er_max - er) * leg["size"]
    return js(out)


# ------------------------------------------------------------------ classification (protocol §5, §6)

def classify(ev: parity.MismatchEvidence, feed_dependent: str | None = None, tags: list[str] | None = None) -> dict:
    """Frozen order with FEED_DEPENDENT_SIGNAL_DIFFERENCE after FEED_DIFFERENCE (protocol §5). Without a feed-dependent
    flag this is exactly `parity.classify_mismatch`."""
    if feed_dependent is None:
        out = parity.classify_mismatch(ev)
    else:
        order = [(parity.DATA_LIMITATION, ev.data_limitation), (parity.FEED_DIFFERENCE, ev.feed_difference),
                 (FDSD, feed_dependent), (parity.EXECUTION_DEPENDENT, ev.execution_dependent),
                 (parity.OWNER_BASELINE_CHOICE, ev.owner_baseline_choice),
                 (parity.UNRESOLVED_SPEC_AMBIGUITY, ev.open_question), (parity.IMPLEMENTATION_BUG, ev.failing_spec_test),
                 (parity.CANON_MISMATCH, ev.canon_evidence)]
        applicable = [c for c, flag in order if flag]
        out = {"primary": applicable[0], "secondary": applicable[1:], "implementation_bug": ev.failing_spec_test is not None,
               "blocks_gate": ev.failing_spec_test is not None,
               "evidence": {**{k: v for k, v in dataclasses.asdict(ev).items() if v}, "feed_dependent": feed_dependent}}
    out["tags"] = list(tags or [])
    return out


def _course_quote(course: dict, field: str) -> str:
    node = course.get(field) or {}
    return f"{course['example_id']} {field}: {node.get('value')} ({node.get('timestamp')})" if node else ""


def classify_rule(rule: str, row: pd.Series, strict: dict, marg: dict, tau: float, spec: dict, course: dict) -> dict:
    cl = spec["classification"]
    dl = f"{rule}: data incomplete in stored STRUCTURE bars" if rule in cl["data_limitation_rules"] else None
    fd, tags = None, []
    m = marg.get(rule)
    if rule in cl["margin_rules"] and m is not None and abs(m) <= tau:
        fd, tags = f"{rule}: Dukascopy margin {m:+.4f} within feed band τ = {tau}", ["UNVERIFIED", "DATA_LIMITATION"]
    obc = [label for label, r in strict.items() if r is not None and rule not in r["rules_failed"]]
    oq_node = cl["open_questions"].get(rule)
    oq = None
    if oq_node and (oq_node.get("when_condition") in (None, row["condition"])):
        oq = f"{rule} governed by {', '.join(oq_node['oq'])}"
    canon = cl["canon_evidence"].get(rule, ["1h-cbr-machine-spec.md"])
    ev = parity.MismatchEvidence(
        data_limitation=dl, owner_baseline_choice=(f"{rule} passes under {', '.join(obc)} (same candidate identity)"
                                                   if obc else None),
        open_question=oq, canon_evidence=f"PC2 rule {rule} ({', '.join(canon)}); engine value from STRUCTURE bars; "
                                         f"course: {_course_quote(course, 'mtf_model') or course['example_id']}")
    out = classify(ev, fd, tags)
    out["margin_usd"] = m
    return out


def dim_record(n: int, name: str, engine, course, status: str, klass: dict | None = None, **extra) -> dict:
    primary = BM if status == MATCH else FEED if status == FEED else NA if status == NA else klass["primary"]
    return {"dim": n, "name": name, "engine": js(engine), "course": js(course), "status": status, "class": primary,
            "classification": klass, **js(extra)}


def p3_equivalent(t: pd.Timestamp | None, x: dict, direction_ok: bool, spec: dict) -> dict:
    if t is None:
        return {"equivalent": False, "reason": "no completed shift"}
    lo, hi = T(x["tom_time_utc"][0]), T(x["tom_time_utc"][1])
    dist = max(lo - t, t - hi, pd.Timedelta(0))
    same_q = t.floor("15min") == T(x["entry_15m_candle_utc"])
    ok = direction_ok and same_q and dist <= pd.Timedelta(minutes=spec["structural_event_match"]["max_abs_time_difference_minutes"])
    return {"equivalent": bool(ok), "distance_to_tom_interval_s": dist.total_seconds(), "same_15m_candle": bool(same_q),
            "direction_agrees": bool(direction_ok)}


def time_status(t: pd.Timestamp | None, x: dict) -> bool:
    if t is None:
        return False
    tol = pd.Timedelta(seconds=x["time_tolerance_s"])
    return T(x["tom_time_utc"][0]) - tol <= t <= T(x["tom_time_utc"][1]) + tol


def dimensions(row: pd.Series | None, x: dict, course: dict, spec: dict, p, *, tau: float, delta_h: float | None,
               marg: dict, strict_eval: dict | None, strict_same: dict, dxy: dict | None) -> list[dict]:
    """Dimension table for one evaluated candidate (protocol §4, run spec `dimensions`). `strict_eval` maps each
    STRICT_COURSE view to its own evaluated candidate (None when scoring a STRICT_COURSE view itself); `strict_same` maps
    it to the candidate with the same identity."""
    cl = spec["classification"]
    dims = []
    canon = lambda key, quote: parity.MismatchEvidence(
        canon_evidence=f"{', '.join(cl['canon_evidence'].get(key, ['PC2']))}; course {quote}")
    if row is None:
        k = classify(canon("shift", _course_quote(course, "entry_model")))
        return [dim_record(1, "model", None, "CBR1H 5s-shift candidate in H", MISMATCH, k)]
    e = engine_facts(row)
    shift = _t(row["five_second_shift_time"])
    # 1 model
    dims.append(dim_record(1, "model", {"entry_model": row["entry_model"], "variant": row["variant"],
                                         "parent": row["parent_structure_type"]}, "CBR1H 5s shift", MATCH))
    # 2 direction
    ok = row["direction"] == x["direction"]
    dims.append(dim_record(2, "direction", row["direction"], x["direction"], MATCH if ok else MISMATCH,
                           None if ok else classify(canon("shift", _course_quote(course, "entry_model")))))
    # 3 condition
    acc = any(row["condition"] == a["condition"] and ("direction" not in a or a["direction"] == row["cond_direction"])
              for a in x["accepted_conditions"])
    k3 = None
    if not acc:
        if row["condition"] == "TREND":
            k3 = classify(parity.MismatchEvidence(canon_evidence=f"{', '.join(cl['open_questions']['condition_trend']['evidence'])}"
                                                                 f" (D25-P6: TREND not equivalent); course {_course_quote(course, 'mtf_model')}"))
        elif row["condition"] == "UNDEFINED":
            k3 = classify(parity.MismatchEvidence(open_question="UNDEFINED condition governed by OQ-02, OQ-03, OQ-40"))
        elif any(row["condition"] == a["condition"] for a in x["accepted_conditions"]):
            k3 = classify(parity.MismatchEvidence(open_question="trending-range direction governed by "
                                                                + ", ".join(cl["open_questions"]["condition_direction"]["oq"])))
        else:
            k3 = classify(parity.MismatchEvidence(open_question="RANGE / TRENDING_RANGE boundary governed by "
                                                                + ", ".join(cl["open_questions"]["condition_class_boundary"]["oq"])))
    dims.append(dim_record(3, "condition", {"condition": row["condition"], "cond_direction": row["cond_direction"],
                                             "c_med": row["c_med"], "n_legs": row["n_legs"]},
                           x["accepted_conditions"], MATCH if acc else MISMATCH, k3))
    # 4 TR direction
    want = x["trending_range_direction"]
    if want is None:
        dims.append(dim_record(4, "tr_direction", row["cond_direction"], None, NA))
    else:
        ok = row["cond_direction"] == want
        dims.append(dim_record(4, "tr_direction", row["cond_direction"], want, MATCH if ok else MISMATCH,
                               None if ok else classify(parity.MismatchEvidence(
                                   open_question="direction governed by " + ", ".join(cl["open_questions"]["condition_direction"]["oq"])
                                   + ("; NONE = TREND_DIRECTION_UNRESOLVED (D17-4)" if row["cond_direction"] == "NONE" else "")))))
    # 5 extension direction
    ok = row["oe_dir"] == x["extension_direction"]
    k5 = None
    if not ok:
        m = marg.get("extension_direction")
        fd = None if m is None or abs(m) > tau else f"extension-direction margin {m:+.4f} within τ = {tau}"
        k5 = classify(canon("M1H-OE-02", _course_quote(course, "overextension")), fd, ["UNVERIFIED", "DATA_LIMITATION"] if fd else [])
    dims.append(dim_record(5, "extension_direction", row["oe_dir"], x["extension_direction"], MATCH if ok else MISMATCH, k5,
                           margin_usd=marg.get("extension_direction")))
    # 6 extension timing
    ref = shift or row["timestamp"]
    ext_t = _t(row["oe_extreme_time"])
    ok = row["oe_duration_min"] >= p.oe_min_minutes and ext_t is not None and ext_t < ref
    k6 = None
    if not ok:
        obc = [v for v, r in strict_same.items() if r is not None and "oe_origin" in v
               and r["oe_duration_min"] >= p.oe_min_minutes and _t(r["oe_extreme_time"]) is not None and _t(r["oe_extreme_time"]) < ref]
        k6 = classify(parity.MismatchEvidence(owner_baseline_choice=f"duration ≥ {p.oe_min_minutes} under {obc}" if obc else None,
                                              canon_evidence=f"{', '.join(cl['canon_evidence']['M1H-OE-01'])}; course "
                                                             f"{_course_quote(course, 'overextension')}"))
    dims.append(dim_record(6, "extension_timing", {"oe_duration_min": row["oe_duration_min"], "oe_extreme_time": ext_t,
                                                    "oe_no_pullback": row["oe_no_pullback"], "reference_time": ref},
                           "duration ≥ 20 min, extreme before the shift" + ("; course 20-30 min" if course["example_id"] == "CX-TE1-1" else ""),
                           MATCH if ok else MISMATCH, k6))
    # 7 previous 15m take
    ok = bool(row["q_break_by_q"])
    k7 = None
    m7 = marg.get("M1H-6A-2-PREV-15M-BROKEN-BY-Q")
    if not ok:
        fd = None if m7 is None or abs(m7) > tau else f"previous-15m take margin {m7:+.4f} within τ = {tau}"
        k7 = classify(canon("M1H-6A-2-PREV-15M-BROKEN-BY-Q", _course_quote(course, "fifteen_min_cb")), fd,
                      ["UNVERIFIED", "DATA_LIMITATION"] if fd else [])
    dims.append(dim_record(7, "previous_15m_take", {"q_break_by_q": row["q_break_by_q"],
                                                     "q_prev_closed_in_trade_direction": row["q_prev_closed_in_trade_direction"],
                                                     "q_open_utc": row["q_open_utc"]},
                           course.get("fifteen_min_cb", {}).get("value"), MATCH if ok else MISMATCH, k7, margin_usd=m7))
    # 8 shift type
    ok8 = shift is not None and row["direction"] == x["direction"]
    k8 = None
    if not ok8:
        reason = row["cancel_reason"]
        node = cl["open_questions"]["shift_not_completed"].get(reason, {})
        obc = [v for v, r in (strict_eval or {}).items() if r is not None and _t(r["five_second_shift_time"]) is not None
               and r["direction"] == x["direction"]]
        k8 = classify(parity.MismatchEvidence(
            owner_baseline_choice=f"a completed shift in the course direction under {obc}" if obc else None,
            open_question=f"shift ended {reason}: governed by {', '.join(node['oq'])}" if "oq" in node else None,
            canon_evidence=f"{', '.join(node.get('evidence', node.get('else_evidence', cl['canon_evidence']['shift'])))}; "
                           f"cancel {reason}; course {_course_quote(course, 'entry_model')}"))
    dims.append(dim_record(8, "shift_type", {"s5_type3_direction": row["direction"], "shift_completed": shift is not None,
                                              "cancel_reason": row["cancel_reason"],
                                              "m1_hilo_armed_at_decision": row["m1_hilo_armed_at_decision"]},
                           course.get("entry_model", {}).get("value"), MATCH if ok8 else MISMATCH, k8))
    # 9 shift time
    in_tol = time_status(shift, x)
    eq = p3_equivalent(shift, x, row["direction"] == x["direction"], spec)
    if ok8 and in_tol:
        st9, k9 = MATCH, None
    elif ok8 and eq["equivalent"]:
        st9, k9 = FEED, None
    else:
        st9 = MISMATCH
        obc = [v for v, r in (strict_eval or {}).items() if r is not None
               and p3_equivalent(_t(r["five_second_shift_time"]), x, r["direction"] == x["direction"], spec)["equivalent"]]
        k9 = k8 if not ok8 else classify(parity.MismatchEvidence(
            owner_baseline_choice=f"D25-P3-equivalent shift selected under {obc}" if obc else None,
            canon_evidence=f"{', '.join(cl['canon_evidence']['shift'])}; frozen selection D19-10 takes the first shift; "
                           f"course {_course_quote(course, 'cb_hour_timing')}"))
    dims.append(dim_record(9, "shift_time", shift, {"tom_interval": x["tom_time_utc"], "tolerance_s": x["time_tolerance_s"]},
                           st9, k9, p3=eq))
    # 10 stop anchor concept
    anchor = e["stop_anchor_at_shift"]
    tom_stop = x["tom_prices"]["stop"]
    adj = None if delta_h is None else tom_stop - delta_h
    k10, st10 = None, MISMATCH
    if anchor is None or adj is None:
        k10 = classify(parity.MismatchEvidence(data_limitation="anchor or FOREXCOM hour offset unavailable"))
    else:
        beyond = adj <= anchor if x["direction"] == "BUY" else adj >= anchor
        if beyond:
            st10 = MATCH if abs(tom_stop - anchor) <= 0.01 else FEED
        elif abs(adj - anchor) <= tau:
            st10 = FEED
        else:
            k10 = classify(canon("stop_anchor", "stop at a level inside the engine extension"))
    dims.append(dim_record(10, "stop_anchor", {"anchor_at_shift": anchor, "source": row["stop_anchor_source"],
                                                "buffer_price": row["stop_buffer_price"]},
                           {"tom_stop": tom_stop, "delta_h": delta_h, "tom_stop_minus_delta_h": adj}, st10, k10,
                           tom_minus_engine=None if anchor is None else tom_stop - anchor,
                           adjusted_minus_engine=None if anchor is None or adj is None else adj - anchor))
    # 11 target concept
    tgt = e["target_at_shift"]
    tom_t = x["tom_prices"]["target"]
    if x["target_concept"] == "FIFTY_PERCENT_OF_MOVE":
        st11 = MATCH if tgt is not None and abs(tom_t - tgt) <= 0.01 else FEED
        k11 = None
    else:
        st11 = MISMATCH
        k11 = classify(parity.MismatchEvidence(canon_evidence=f"M1H-TP-01 50% of the hour extension; course discretion: "
                                                              f"{_course_quote(course, 'target_description')}"))
    dims.append(dim_record(11, "target_concept", {"target_at_shift": tgt, "concept": "50% of extension from H.open"},
                           {"tom_target": tom_t, "concept": x["target_concept"]}, st11, k11,
                           tom_minus_engine=None if tgt is None else tom_t - tgt,
                           adjusted_minus_engine=None if tgt is None or delta_h is None else tom_t - delta_h - tgt))
    # 12 DXY (descriptive)
    if dxy is None or dxy.get("value") in (None, "None", "nan"):
        dims.append(dim_record(12, "dxy", dxy, x["dxy_note"], MISMATCH,
                               classify(parity.MismatchEvidence(data_limitation="DXY context unavailable")), descriptive=True))
    else:
        ok = dxy["value"] == x["dxy_note"]["direction"]
        k12 = None
        if not ok:
            tvc_ok = dxy.get("tvc_hour_direction") == x["dxy_note"]["direction"]
            k12 = classify(parity.MismatchEvidence(feed_difference="TVC:DXY 1h agrees with the note; CFD differs" if tvc_ok else None,
                                                   canon_evidence=f"no DXY rule in CBR1H V1 (D25-P8); course {x['dxy_note']['text']}"))
        dims.append(dim_record(12, "dxy", dxy, x["dxy_note"], MATCH if ok else MISMATCH, k12, descriptive=True))
    return dims


def hard_dimensions(dims: list[dict]) -> dict:
    by = {d["dim"]: d for d in dims}
    get = lambda n: by.get(n, {"status": MISMATCH, "class": by[1]["class"]})
    trig_ok = get(8)["status"] == MATCH and get(9)["status"] in (MATCH, FEED)
    trig_class = get(8)["class"] if get(8)["status"] != MATCH else get(9)["class"]
    return {
        "model_family": {"met": get(1)["status"] == MATCH, "class": get(1)["class"]},
        "direction": {"met": get(2)["status"] == MATCH, "class": get(2)["class"]},
        "extension_direction": {"met": get(5)["status"] == MATCH, "class": get(5)["class"]},
        "core_structural_trigger": {"met": trig_ok, "class": trig_class if not trig_ok else get(9)["class"]},
    }


def example_verdict(dims: list[dict], acceptance: list[dict], spec: dict) -> str:
    order = spec["classification"]["example_verdict_order"]
    agg = {BM: BM, FEED: BMFD, NA: BM, parity.DATA_LIMITATION: parity.UNRESOLVED_SPEC_AMBIGUITY,
           parity.EXECUTION_DEPENDENT: parity.UNRESOLVED_SPEC_AMBIGUITY}
    classes = [agg.get(d["class"], d["class"]) for d in dims if not d.get("descriptive")]
    classes += [agg.get(a["classification"]["primary"], a["classification"]["primary"]) for a in acceptance]
    if any(d.get("classification") and d["classification"].get("implementation_bug") for d in dims):
        classes.append(parity.IMPLEMENTATION_BUG)
    return min(classes, key=order.index) if classes else BM


# ------------------------------------------------------------------ DXY at the shift (P-8, descriptive)

def dxy_at(t: pd.Timestamp, field: str, htf: dict | None) -> dict | None:
    day = t.floor("D")
    p = dk.NORM / "dollaridxusd" / "candles_1m" / f"{day.date().isoformat()}.parquet"
    if not p.exists():
        return None
    dxy = pd.read_parquet(p)[["open", "close"]]
    dx = load_front("dx_front_ohlcv1m")
    ctx = dxy_ctx.build_context(dxy, pd.DatetimeIndex([t]), (day, day + pd.Timedelta(days=1)), dx=dx,
                                dx_range=(dx.index.min(), dx.index.max() + M1), hindsight=False)
    rec = ctx.iloc[0]
    out = {"time": t, "field": field, "value": rec[field],
           **{k: rec[k] for k in ("dxy_1h_forming_direction", "dxy_1h_last_direction", "dxy_15m_forming_direction",
                                  "dxy_15m_last_direction", "dxy_1h_forming_state", "dxy_15m_forming_state",
                                  "dxy_confidence", "dxy_reason_codes")}}
    if htf:
        hour = [r for r in htf.get("dxy_1h", []) if r["bar"] == str(t.floor("1h"))]
        if hour and "tvc_direction" in hour[0]:
            out["tvc_hour_direction"] = {1: "UP", -1: "DOWN", 0: "FLAT"}[hour[0]["tvc_direction"]]
            out["tvc_note"] = "TVC:DXY 1h bar final direction (hour close; hindsight, descriptive)"
    return js(out)


# ------------------------------------------------------------------ causality spot checks (gate A evidence)

def causality_checks(s1m, s5s, h0, variant, params, row: pd.Series | None) -> dict:
    """Truncation and future mutation at mid-minute cuts after the evaluated candidate's decision and shift."""
    if row is None:
        return {"checked": False}
    full = cbr1h.run_cbr1h(s1m, s5s, start=h0, end=h0 + H1, variant=variant, params=params)
    dec_full, trg_full = cbr1h.decision_frame(full), cbr1h.trigger_frame(full)
    out = {}
    cuts = {"decision": row["timestamp"] + pd.Timedelta(seconds=32)}
    if _t(row["five_second_shift_time"]) is not None:
        cuts["shift"] = _t(row["five_second_shift_time"]) + pd.Timedelta(seconds=32)
    for label, cut in cuts.items():
        k1, k5 = s1m[s1m.index + M1 <= cut], s5s[s5s.index + S5 <= cut]
        m1, m5 = s1m.copy(), s5s.copy()
        for m, blen in ((m1, M1), (m5, S5)):
            after = m.index + blen > cut
            m.loc[after, ["open", "high", "low", "close"]] = m.loc[after, ["open", "high", "low", "close"]] * 1.03 + 0.5
        res = {}
        for kind, (b1, b5) in (("truncation", (k1, k5)), ("future_mutation", (m1, m5))):
            r = cbr1h.run_cbr1h(b1, b5, start=h0, end=h0 + H1, variant=variant, params=params)
            want = dec_full[dec_full["timestamp"] <= cut].reset_index(drop=True).astype(str)
            got = cbr1h.decision_frame(r)
            got = got[got["timestamp"] <= cut].reset_index(drop=True).astype(str)
            tw = trg_full[pd.to_datetime(trg_full["five_second_shift_time"], utc=True) <= cut].reset_index(drop=True).astype(str)
            tg = cbr1h.trigger_frame(r)
            tg = tg[pd.to_datetime(tg["five_second_shift_time"], utc=True) <= cut].reset_index(drop=True).astype(str)
            res[kind] = {"decision_rows": len(want), "decision_identical": bool(want.equals(got)),
                         "trigger_rows": len(tw), "trigger_identical": bool(tw.equals(tg))}
        out[label] = {"cut": cut, **res}
    out["checked"] = True
    out["all_identical"] = all(v[k][f] for lab, v in out.items() if isinstance(v, dict) and "cut" in v
                               for k in ("truncation", "future_mutation") for f in ("decision_identical", "trigger_identical"))
    return js(out)


# ------------------------------------------------------------------ complete run

def course_record(ex_id: str) -> dict:
    for line in (ROOT / "research" / "examples" / "course_examples.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["example_id"] == ex_id:
            return r
    raise KeyError(ex_id)


def run_complete(repeat: int) -> dict:
    freeze_rec = verify_freeze()
    spec = load_spec()
    p = load_cbr1h("A")
    missing = [str(x) for x in recent_tick_paths(spec) if not x.exists()]
    if missing:
        raise SystemExit(f"recent Dukascopy days not fetched: {missing}")
    study, tau = recent_study(spec, p)                                                 # §8 order: fixes τ first
    htf = htf_study(spec)
    examples, negative = {}, None
    runs_cache: dict[str, dict] = {}
    determinism = {}
    for ex_id, x in spec["examples"].items():
        span_key = f"{x['hour_utc']}|{x['data_span_utc']}"
        if span_key not in runs_cache:
            runs_cache[span_key] = engine_runs(x, spec)
        er = runs_cache[span_key]
        for (variant, label), r in er["runs"].items():
            determinism[f"{span_key}|{variant}|{label}"] = {"hashes": r["hashes"], "identical": r["identical"]}
        if x["role"] == "NEGATIVE_CONTROL":
            negative = negative_control(ex_id, x, er, spec)
            continue
        examples[ex_id] = evaluate_example(ex_id, x, er, spec, p, tau, htf.get(ex_id))
    payload = {"run_id": spec["run_id"], "freeze_commit": freeze_rec["git_commit"], "pc2_spec_hash": spec_hash(),
               "data_hashes": data_hashes(spec), "recent_feed_comparison": study, "higher_timeframe": htf,
               "examples": examples, "negative_control": negative, "engine_run_determinism": determinism}
    out = {"repeat": repeat, "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
           "result_hash": payload_hash(payload), "payload": js(payload)}
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / f"run-{repeat}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out


def evaluate_example(ex_id: str, x: dict, er: dict, spec: dict, p, tau: float, htf: dict | None) -> dict:
    course = course_record(ex_id)
    h0 = T(x["hour_utc"])
    delta_h = None if htf is None else htf.get("delta_h")
    ctx_mtf = cbr1h._Context(er["s1m"], er["s5s"], p).sw_mtf
    variants = {}
    for variant in spec["variants"]:
        base = er["runs"][(variant, "BASELINE_SPEC")]
        cands, params = base["result"].candidates, base["params"]
        row, how = evaluated_candidate(cands, variant, params)
        strict_labels = [view_label("STRICT_COURSE", ab) for ab in spec["views"]["STRICT_COURSE"]]
        strict_eval_rows = {lab: evaluated_candidate(er["runs"][(variant, lab)]["result"].candidates, variant,
                                                     er["runs"][(variant, lab)]["params"])[0] for lab in strict_labels}
        strict_same = {lab: (None if row is None else find_same(er["runs"][(variant, lab)]["result"].candidates, row))
                       for lab in strict_labels}
        marg = {} if row is None else margins(row, er["s1m"], er["s5s"], ctx_mtf, params)
        ref_t = None if row is None else (_t(row["five_second_shift_time"]) or row["timestamp"])
        dxy = None if ref_t is None else dxy_at(ref_t, x["dxy_note"]["compare_field"], htf)
        dims = dimensions(row, x, course, spec, p, tau=tau, delta_h=delta_h, marg=marg, strict_eval=strict_eval_rows,
                          strict_same=strict_same, dxy=dxy)
        acceptance = [] if row is None else [
            {"rule": rule, "classification": classify_rule(rule, row, strict_same, marg, tau, spec, course)}
            for rule in row["rules_failed"]]
        strict_tables = {}
        for lab, srow in strict_eval_rows.items():
            sp = er["runs"][(variant, lab)]["params"]
            smarg = {} if srow is None else margins(srow, er["s1m"], er["s5s"], ctx_mtf, sp)
            sdims = dimensions(srow, x, course, spec, p, tau=tau, delta_h=delta_h, marg=smarg, strict_eval=None,
                               strict_same={}, dxy=None)
            strict_tables[lab] = {"how": evaluated_candidate(er["runs"][(variant, lab)]["result"].candidates, variant, sp)[1],
                                  "engine": engine_facts(srow), "dimensions": [d for d in sdims if d["dim"] != 12],
                                  "hard": hard_dimensions(sdims)}
        variants[variant] = {
            "how_selected": how, "engine": engine_facts(row), "margins_usd": marg, "dimensions": dims,
            "hard": hard_dimensions(dims), "acceptance": {"event": None if row is None else row["event"], "failed_rules": acceptance},
            "example_verdict": example_verdict(dims, acceptance, spec),
            "strict_course": strict_tables,
            "candidates_in_hour": 0 if not len(cands) else int((cands["variant"] == variant).sum()),
            "armed_in_hour": 0 if not len(cands) else int(((cands["variant"] == variant) & (cands["event"] == "ARMED")).sum()),
            "causality": causality_checks(er["s1m"], er["s5s"], h0, variant, params, row),
        }
    met = {v: sum(variants[v]["hard"][h]["met"] for h in HARD) for v in variants}
    scored = next((v for v in spec["variants"] if met[v] == len(HARD)), None) or max(spec["variants"], key=lambda v: (met[v], -spec["variants"].index(v)))
    return {"example_id": ex_id, "hour_utc": x["hour_utc"], "direction": x["direction"], "variants": variants,
            "scored_variant": scored, "hard_met": variants[scored]["hard"], "example_verdict": variants[scored]["example_verdict"],
            "course_record_sha256": hashlib.sha256(json.dumps(course, sort_keys=True).encode()).hexdigest()}


def negative_control(ex_id: str, x: dict, er: dict, spec: dict) -> dict:
    lo, hi = T(x["control_window_utc"][0]), T(x["control_window_utc"][1])
    in_window, signals = [], []
    for variant in spec["variants"]:
        cands = er["runs"][(variant, "BASELINE_SPEC")]["result"].candidates
        if not len(cands):
            continue
        for _, r in cands[cands["variant"] == variant].iterrows():
            t = _t(r["five_second_shift_time"])
            if t is None or not (lo <= t < hi):
                continue
            rec = {"variant": variant, "signal_id": r["signal_id"], "event": r["event"], "direction": r["direction"],
                   "decision": r["timestamp"], "shift_time": t, "shift_level": r["five_second_shift_level"],
                   "rules_failed": list(r["rules_failed"])}
            in_window.append(rec)
            if r["event"] == "ARMED":
                gone = []
                for ab in spec["views"]["STRICT_COURSE"]:
                    lab = view_label("STRICT_COURSE", ab)
                    same = find_same(er["runs"][(variant, lab)]["result"].candidates, r)
                    st = None if same is None else _t(same["five_second_shift_time"])
                    if same is None or same["event"] != "ARMED" or st is None or not (lo <= st < hi):
                        gone.append({"view": lab, "rules_failed": None if same is None else list(same["rules_failed"])})
                ev = parity.MismatchEvidence(
                    owner_baseline_choice=f"signal absent under {[g['view'] for g in gone]}" if gone else None,
                    open_question="OQ-08: shift size and cleanliness (Tom's stated rejection reasons) are unquantified in PC2")
                k = classify(ev, tags=["OUT_OF_SCOPE_INSTRUMENT: gold spread (D7)"])
                signals.append({**rec, "absent_under": gone, "classification": k,
                                "rule_differences": [t["reason"] for t in x["tom_reasons"]]})
    return js({"example_id": ex_id, "window_utc": x["control_window_utc"], "expected": x["expected"],
               "result": "NO_ELIGIBLE_CANONICAL_SIGNAL" if not signals else "ELIGIBLE_CANONICAL_SIGNAL_PRODUCED",
               "eligible_signals": signals, "all_candidates_with_shift_in_window": in_window,
               "course_record_sha256": hashlib.sha256(json.dumps(course_record(ex_id), sort_keys=True).encode()).hexdigest()})


# ------------------------------------------------------------------ verdict (D25-P5-V, O-5, O-6)

def verdict(run1: dict, run2: dict, spec: dict) -> dict:
    pl = run1["payload"]
    reasons_fail, reasons_owner, concerns = [], [], []
    if run1["result_hash"] != run2["result_hash"]:
        reasons_fail.append("gate A: complete-run repeat not identical")
    if not all(v["identical"] for v in pl["engine_run_determinism"].values()):
        reasons_fail.append("gate A: an engine-run repeat not identical")
    causal = [v["causality"].get("all_identical") for ex in pl["examples"].values() for v in ex["variants"].values()
              if v["causality"].get("checked")]
    if not all(causal):
        reasons_fail.append("gate A: a truncation / future-mutation spot check differed")
    if pl["pc2_spec_hash"] != spec["spec_under_test"]["spec_hash"] or spec_hash() != spec["spec_under_test"]["spec_hash"]:
        reasons_fail.append("gate B: PC2 spec hash changed")
    hard_table = {}
    for ex_id, ex in pl["examples"].items():
        v = ex["variants"][ex["scored_variant"]]
        hard_table[ex_id] = ex["hard_met"]
        for h, rec in ex["hard_met"].items():
            if rec["met"]:
                continue
            if rec["class"] == parity.OWNER_BASELINE_CHOICE:
                reasons_owner.append(f"{ex_id} {h}: failed with OWNER_BASELINE_CHOICE only")
            else:
                reasons_fail.append(f"{ex_id} {h}: not met ({rec['class']})")
        bugs = [d for d in v["dimensions"] if d.get("classification") and d["classification"].get("implementation_bug")]
        bugs += [a for a in v["acceptance"]["failed_rules"] if a["classification"].get("implementation_bug")]
        if bugs:
            reasons_fail.append(f"{ex_id}: open IMPLEMENTATION_BUG")
        for d in v["dimensions"]:
            if d.get("descriptive") or d["class"] in (BM, NA):
                continue
            concerns.append(f"{ex_id} dim {d['dim']} {d['name']}: {d['class']}")
        if v["acceptance"]["event"] != "ARMED":
            concerns.append(f"{ex_id}: engine candidate {v['acceptance']['event']} (failed: "
                            + ", ".join(f"{a['rule']}={a['classification']['primary']}" for a in v["acceptance"]["failed_rules"]) + ")")
    neg = pl["negative_control"]
    if neg["result"] != "NO_ELIGIBLE_CANONICAL_SIGNAL":
        if any(s["classification"].get("implementation_bug") for s in neg["eligible_signals"]):
            reasons_fail.append("negative control: IMPLEMENTATION_BUG")
        concerns.append("negative control CX-LT3-1 produced an eligible canonical signal: "
                        + "; ".join(f"{s['signal_id']} {s['classification']['primary']}" for s in neg["eligible_signals"]))
    c9 = pl["recent_feed_comparison"]["criterion_9"]
    if c9["status"] == "FAIL_EVIDENCE":
        reasons_fail.append(f"criterion 9: FAIL evidence {c9['fail_evidence']}")
    elif c9["status"] == "CONCERN":
        concerns.append(f"criterion 9 concern: {c9['concerns']}")
    if reasons_fail:
        v_ = "FAIL"
    elif reasons_owner:
        v_ = "OWNER_DETERMINATION_REQUIRED"
    elif concerns:
        v_ = "PASS WITH CONCERNS"
    else:
        v_ = "PASS"
    criteria = {
        "1_model_family_3of3": all(h["model_family"]["met"] for h in hard_table.values()),
        "2_direction_3of3": all(h["direction"]["met"] for h in hard_table.values()),
        "3_extension_direction_3of3": all(h["extension_direction"]["met"] for h in hard_table.values()),
        "4_core_structural_trigger_3of3": all(h["core_structural_trigger"]["met"] for h in hard_table.values()),
        "5_negative_control_clean": neg["result"] == "NO_ELIGIBLE_CANONICAL_SIGNAL",
        "6_no_open_implementation_bug": not any("IMPLEMENTATION_BUG" in r for r in reasons_fail),
        "7_no_unexplained_canon_mismatch": True,              # every CANON_MISMATCH carries cited evidence (classify_mismatch)
        "8_every_mismatch_classified": True,                  # by construction: each non-match has a primary class
        "9_feed_study": c9["status"]}
    return {"verdict": v_, "criteria": criteria, "fail_reasons": reasons_fail, "owner_determination": reasons_owner,
            "concerns": concerns, "deterministic_rerun": run1["result_hash"] == run2["result_hash"],
            "result_hashes": [run1["result_hash"], run2["result_hash"]]}


# ------------------------------------------------------------------ CLI

def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "freeze":
        rec = freeze()
        print(json.dumps({"frozen": rec["run_id"], "commit": rec["git_commit"], "tests": rec["pre_execution_tests"]}, indent=2))
    elif cmd == "fetch":
        print(json.dumps(fetch(), indent=2))
    elif cmd == "run":
        out = run_complete(int(args[1]))
        print(json.dumps({"repeat": out["repeat"], "result_hash": out["result_hash"]}, indent=2))
    elif cmd == "report":
        from cbr.engine.phase13_report import write_reports
        print(json.dumps(write_reports(), indent=2))
    else:
        raise SystemExit("usage: python -m cbr.engine.phase13_behavioral [freeze|fetch|run N|report]")


if __name__ == "__main__":
    main()
