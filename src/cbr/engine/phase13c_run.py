"""Phase 13C scored parity run of PC3 (CBR-PROT-013C v1.1, owner ruling D31). Run id CBR-RUN-013C-1.

Usage (exact order, each step refuses to run out of order):
    .venv/bin/python -m cbr.engine.phase13c_run freeze     # verify frozen hashes + full suite -> reports/phase13c-freeze-manifest.json
    .venv/bin/python -m cbr.engine.phase13c_run run 1      # complete machine-set run -> data/phase13c/run-1.json
    .venv/bin/python -m cbr.engine.phase13c_run run 2      # deterministic repeat from the same frozen inputs
    .venv/bin/python -m cbr.engine.phase13c_run report     # determinism check, verdict, reports/phase13c-*

Signal state only: no fills, outcomes or P&L at any point (D31-17). PC3, the parity-set manifest and the scoring fields
are never modified during the run. The scoring mappings M-1…M-7 are frozen in D31 and applied verbatim here.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.engine import cbr1h_pc3 as pc3
from cbr.engine import parity
from cbr.engine.params import ROOT, spec_hash
from cbr.engine.params_pc3 import load_cbr1h_pc3, spec_hash_pc3
from cbr.engine.parity_set import MANIFEST as SET_MANIFEST
from cbr.engine.phase13_behavioral import js, payload_hash

RUN_ID = "CBR-RUN-013C-1"
FREEZE_MANIFEST = ROOT / "reports" / "phase13c-freeze-manifest.json"
RUN_DIR = ROOT / "data" / "phase13c"
REPORTS = ROOT / "reports"
H1, M1, S5 = pd.Timedelta(hours=1), pd.Timedelta(minutes=1), pd.Timedelta(seconds=5)
SELECTION_MISMATCH = "CANDIDATE_SELECTION_MISMATCH"
EXPECTED_HASHES = {                                            # D31-1
    "pc3_spec": "7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453",
    "pc2_spec": "4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2",
    "parity_manifest": "a3ee0bd6ba225ce6b89d8bc61fbefd227ce8097a3f6bfac2f9414e19cd81ea9c",
}
FROZEN_FILES = [
    "docs/governance/phase13c-pc3-parity-protocol.md", "docs/governance/d31-pc3-scored-parity-authorization.md",
    "docs/governance/d29-pc3-authorization.md", "docs/governance/d30-pc3-parity-preparation.md",
    "docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC3.yaml",
    "docs/strategy/parity-candidates/CBR15_BASELINE_V1-PC3.yaml",
    "docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC2.yaml", "research/examples/parity_set_manifest.json",
    "config/strategy.yaml", "config/strategy_pc3.yaml", "src/cbr/engine/cbr1h_pc3.py", "src/cbr/engine/params_pc3.py",
    "src/cbr/engine/parity.py", "src/cbr/engine/parity_set.py", "src/cbr/engine/phase13c_run.py",
    "src/cbr/structure/shifts_pc3.py", "src/cbr/structure/overextension_pc3.py", "src/cbr/structure/condition_pc3.py",
]
# M-1 accepted conditions (D25-P6, unchanged); M-4/M-5 journal mappings; all frozen in D31.
ACCEPTED_CONDITIONS = {
    "CX-LT1-1": [{"condition": "RANGE"}, {"condition": "TRENDING_RANGE"}],
    "CX-TE1-1": [{"condition": "TRENDING_RANGE", "direction": "DOWN"}, {"condition": "RANGE"}],
    "CX-LT3-2": [{"condition": "TRENDING_RANGE", "direction": "UP"}],
}
COURSE_EXTENSION_DIR = {"CX-LT1-1": "DOWN", "CX-TE1-1": "DOWN", "CX-LT3-2": "UP", "CX-LT3-1": "UP"}
TOM_TIMES = {
    "CX-LT1-1": ("2025-10-21T01:39:15+00:00", "2025-10-21T01:39:15+00:00", "2025-10-21T01:30:00+00:00"),
    "CX-TE1-1": ("2025-10-24T04:37:00+00:00", "2025-10-24T04:39:00+00:00", "2025-10-24T04:30:00+00:00"),
    "CX-LT3-2": ("2025-11-10T01:40:00+00:00", "2025-11-10T01:40:00+00:00", "2025-11-10T01:30:00+00:00"),
}
JOURNAL_CONDITION = {"Trending": ["TRENDING_RANGE", "RANGE"], "Volume": None, "Ranging": ["RANGE", "TRENDING_RANGE"]}
TIMING_BUCKET = {37: (30, 45), 52: (45, 60)}
NARRATIVE_ASSESSMENT = {                                        # D31-19, qualitative, no machine-pass contribution
    "CX-LT2-2": ("CONSISTENT", ("PC3's geometry is sweep → break of the most recent opposing swing, which is exactly "
                                "'sell at the break of that low'. USDJPY has no data, so this is geometry only.")),
    "CX-LT2-1": ("NOT_DETERMINABLE", ("The source rejects the setup on timing (~22 minutes in), and PC3 has no rule "
                                      "that encodes Tom's discretionary 'too early' judgement; no data to test.")),
    "T3-VP1-A": ("CONSISTENT", ("The drawn ranging type 3 takes the range high, then the range low, then shifts: "
                                "PC3's sweep-then-break with a re-anchored trigger reproduces that ordering.")),
    "T3-VP1-B": ("CONSISTENT", ("The swept low is marked and extended as a level, then the reversal follows; PC3 "
                                "treats the sweep extreme as the stop reference and the opposing swing as the "
                                "trigger.")),
    "T3-VP2-HILO": ("CONSISTENT", ("The HILO lesson re-anchors its reference to the previous candle each candle, "
                                   "which is the evidence behind PC3's re-anchored trigger; the invalid example "
                                   "lacks the prior-candle break, which PC3 also rejects for lack of a confirmed "
                                   "opposing swing.")),
    "OE-GOOD-BAD": ("CONSISTENT", ("PC3 measures the deepest retracement against the whole active extension, so the "
                                   "'didn't correct 50% at all' chart passes and the 'on average correcting 50%' "
                                   "chart fails, matching the lesson.")),
    "V15-SEM-2026-05": ("NOT_DETERMINABLE", ("Illustrative CBR15 walkthrough with no stated entry; CBR15-PC3 is "
                                             "SPEC_ONLY and unscored (D30-3, D30-10).")),
}


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def load_set() -> dict:
    return json.loads(SET_MANIFEST.read_text())


# ------------------------------------------------------------------ freeze (D31-1, step 1-2)

def freeze() -> dict:
    if FREEZE_MANIFEST.exists():
        raise SystemExit(f"{FREEZE_MANIFEST.relative_to(ROOT)} exists: already frozen (a change needs a new run id)")
    if _git("status", "--porcelain"):
        raise SystemExit("uncommitted changes: commit the run code before freezing")
    got = {"pc3_spec": spec_hash_pc3(), "pc2_spec": spec_hash(), "parity_manifest": load_set()["manifest_hash"]}
    bad = {k: (v, got[k]) for k, v in EXPECTED_HASHES.items() if got[k] != v}
    if bad:
        raise SystemExit(f"STOP (D31-1): frozen hash changed before execution: {bad}")
    res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True, check=False)
    summary = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-400:]
    if res.returncode != 0:
        raise SystemExit(f"pre-execution suite failed: {summary}")
    lint = subprocess.run([str(ROOT / ".venv" / "bin" / "ruff"), "check", "src", "tests"], cwd=ROOT,
                          capture_output=True, text=True, check=False)
    data_hashes = {}
    for case in load_set()["cases"]:
        data_hashes.update(case["market_data_hashes"])
    rec = {"run_id": RUN_ID, "ruling": "D31", "frozen_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
           "git_commit": _git("rev-parse", "HEAD"), "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
           "expected_hashes": EXPECTED_HASHES, "verified_hashes": got,
           "files": {f: sha(f) for f in FROZEN_FILES}, "market_data_hashes": data_hashes,
           "pre_execution_tests": summary,
           "lint": lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else "clean"}
    FREEZE_MANIFEST.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def verify_freeze() -> dict:
    if not FREEZE_MANIFEST.exists():
        raise SystemExit("not frozen: run `freeze` first")
    rec = json.loads(FREEZE_MANIFEST.read_text())
    changed = [f for f, h in {**rec["files"], **rec["market_data_hashes"]}.items() if sha(f) != h]
    got = {"pc3_spec": spec_hash_pc3(), "pc2_spec": spec_hash(), "parity_manifest": load_set()["manifest_hash"]}
    if changed or got != rec["verified_hashes"]:
        raise SystemExit(f"STOP (D31-1): frozen inputs changed after the freeze: {changed or got}")
    return rec


# ------------------------------------------------------------------ engine execution

def _t(v):
    return None if v is None or (not isinstance(v, pd.Timestamp) and pd.isna(v)) else pd.Timestamp(v)


def run_hour(case: dict) -> dict:
    """Run PC3 variants A and B over the case hour; return candidates per variant (engine information only)."""
    a, b = (pd.Timestamp(x) for x in case["data_span_utc"])
    h0 = pd.Timestamp(case["start_time"])
    s1m, s5s = cb.load_structure(a, b, "1m"), cb.load_structure(a, b, "5s")
    out = {}
    for variant in ("A", "B"):
        p = load_cbr1h_pc3(variant)
        res = pc3.run_cbr1h_pc3(s1m, s5s, start=h0, end=h0 + H1, variant=variant, params=p)
        out[variant] = {"result": res, "params": p, "hash": pc3.result_hash(res)}
    return out


def eligible(cands: pd.DataFrame, variant: str) -> pd.DataFrame:
    if not len(cands):
        return cands
    c = cands[cands["variant"] == variant]
    return c[c["event_at_trigger"] == "ARMED_AT_TRIGGER"]


def p3_equivalent(shift, case_id: str, direction_ok: bool) -> bool:
    """M-7 / D25-P3: same direction, same 15m candle as the course entry, |Δt| <= 3 min."""
    if shift is None or case_id not in TOM_TIMES:
        return False
    lo, hi, q = (pd.Timestamp(x) for x in TOM_TIMES[case_id])
    dist = max(lo - shift, shift - hi, pd.Timedelta(0))
    return bool(direction_ok and shift.floor("15min") == q and dist <= pd.Timedelta(minutes=3))


def facts(row: pd.Series | None) -> dict | None:
    if row is None:
        return None
    keys = ["signal_id", "variant", "event", "event_at_trigger", "rules_failed", "rules_failed_at_trigger", "timestamp",
            "direction", "entry_model", "condition", "condition_fallback_applied", "cond_direction", "extension_state",
            "extension_activation_time", "extension_activation_reason", "oe_dir", "oe_duration_min", "oe_size",
            "oe_retracement_ratio", "ext_extreme_at_decision", "pos_oe_extreme", "q_break_by_q", "hvcs_rule_state",
            "hvcs_minutes", "hvcs_indecision_bars", "five_second_sweep_time", "five_second_shift_time",
            "five_second_shift_level", "five_second_shift_level_at_trigger", "trigger_reanchored",
            "structure_stop_anchor", "target_at_activation", "cancel_reason"]
    return js({k: row.get(k) for k in keys})


# ------------------------------------------------------------------ scoring

def score_entry_case(case: dict, runs: dict) -> dict:
    """Nine frozen dimensions (CBR-PROT-013C §2.1) plus the D31-12 selection report."""
    cid = case["case_id"]
    want_dir, want_ext = case["direction"], COURSE_EXTENSION_DIR[cid]
    per_variant, matching, all_elig, all_cands, sel_all = {}, [], [], [], []
    for variant in ("A", "B"):
        cands = runs[variant]["result"].candidates
        el = eligible(cands, variant)
        sel = parity.select_candidate(cands, variant, runs[variant]["params"])   # frozen rule, unmodified input
        by_id = {r["signal_id"]: r for _, r in el.iterrows()} if len(el) else {}
        selected = by_id.get(sel.get("selected"))
        if sel.get("selected"):
            sel_all.append(sel["selected"])
        if len(cands):
            all_cands += [r for _, r in cands[cands["variant"] == variant].iterrows()]
        for _, r in el.iterrows():
            all_elig.append(r)
            if p3_equivalent(_t(r["five_second_shift_time"]), cid, r["direction"] == want_dir):
                matching.append(r)
        per_variant[variant] = {
            "candidates": 0 if not len(cands) else int((cands["variant"] == variant).sum()),
            "eligible": len(el), "frozen_selection": sel.get("selected"),
            "frozen_selection_eligible": sel.get("selected") in by_id,
            "diagnostic_only": js(sel.get("diagnostic_only")), "selected_facts": facts(selected),
            "eligible_ids": [] if not len(el) else list(el["signal_id"]),
        }
    # Two readings, both reported (see the report's scoring-convention note):
    #   strict   — M-7/D31-12: the structural event exists only if a D25-P3-equivalent *eligible* candidate exists.
    #              This is what binds acceptance rule A-1's core-trigger hard dimension. Never relaxed.
    #   descriptive — dimensions 1-8 are read off the closest candidate whether or not it survived to eligibility, so
    #              the report says which rule actually rejected it instead of reporting every dimension as a mismatch.
    #              Dimension 9 is the eligibility dimension and is scored strictly.
    near = [r for r in all_cands if p3_equivalent(_t(r["five_second_shift_time"]), cid, r["direction"] == want_dir)]
    order = matching or near or [r for r in all_cands if r["signal_id"] in sel_all] or all_cands
    scored_row = min(order, key=parity.selection_key) if len(order) else None
    e = facts(scored_row)
    dims = []

    def add(n, name, engine, expected, ok, cls=None, note=None):
        dims.append({"n": n, "name": name, "engine": js(engine), "expected": js(expected),
                     "status": "MATCH" if ok else "MISMATCH", "class": None if ok else cls, "note": note})

    failed = [] if e is None else list(scored_row["rules_failed_at_trigger"])
    add(1, "model_family", None if e is None else e["entry_model"], "CBR1H", e is not None,
        "CANON_MISMATCH", "no CBR1H candidate at all in the hour" if e is None else None)
    add(2, "direction", None if e is None else e["direction"], want_dir, e is not None and e["direction"] == want_dir,
        "CANON_MISMATCH")
    cond_ok = e is not None and any(e["condition"] == a["condition"] and ("direction" not in a or a["direction"] == e["cond_direction"])
                                    for a in ACCEPTED_CONDITIONS[cid])
    add(3, "condition", None if e is None else {"condition": e["condition"], "cond_direction": e["cond_direction"],
                                                "fallback_applied": e["condition_fallback_applied"]},
        ACCEPTED_CONDITIONS[cid], cond_ok, "CANON_MISMATCH",
        "M-2: PC3 follows the approved OQ-46 correction (D29-14) while D25-P6 names the accepted set"
        if (e is not None and e["condition_fallback_applied"]) else None)
    add(4, "extension_direction", None if e is None else e["oe_dir"], want_ext, e is not None and e["oe_dir"] == want_ext,
        "CANON_MISMATCH")
    add(5, "extension_activation", None if e is None else {"state": e["extension_state"],
                                                           "activation_time": e["extension_activation_time"]},
        "EXTENSION_ACTIVE", e is not None and e["extension_state"] == "EXTENSION_ACTIVE", "CANON_MISMATCH")
    loc_rules = [r for r in failed if r.startswith(("M1H-LOC-", "M1H-6A-2", "M1H-6A-3"))]
    add(6, "location_or_previous_candle_event",
        None if e is None else {"q_break_by_q": e["q_break_by_q"], "pos_oe_extreme": e["pos_oe_extreme"],
                                "failed_rules": loc_rules},
        "location and previous-15m rules pass", e is not None and not loc_rules, "CANON_MISMATCH")
    add(7, "hvcs_state", None if e is None else {"state": e["hvcs_rule_state"], "minutes": e["hvcs_minutes"],
                                                 "indecision": e["hvcs_indecision_bars"],
                                                 "failed_rules": [r for r in failed if "HVCS" in r]},
        "valid at the shift for variant A; not applicable for variant B",
        e is not None and (e["variant"] == "B" or e["hvcs_rule_state"] is True), "CANON_MISMATCH")
    shift = None if e is None else _t(scored_row["five_second_shift_time"])
    equiv = e is not None and p3_equivalent(shift, cid, e["direction"] == want_dir)
    add(8, "type3_5s_structural_trigger", None if e is None else {"shift_time": e["five_second_shift_time"],
                                                                  "trigger_at_decision": e["five_second_shift_level"],
                                                                  "trigger_at_break": e["five_second_shift_level_at_trigger"],
                                                                  "reanchored": e["trigger_reanchored"]},
        {"tom_interval": TOM_TIMES[cid][:2], "rule": "D25-P3 equivalence"}, equiv, "CANON_MISMATCH",
        "descriptive reading: the candidate carrying this shift was not eligible" if (equiv and not matching) else None)
    add(9, "eligible_candidate", None if e is None else {"event_at_trigger": e["event_at_trigger"],
                                                         "rules_failed_at_trigger": failed},
        "ARMED_AT_TRIGGER", e is not None and e["event_at_trigger"] == "ARMED_AT_TRIGGER", "CANON_MISMATCH")
    sel_ids = [v["frozen_selection"] for v in per_variant.values() if v["frozen_selection"]]
    selection = {"structural_event_exists": bool(matching),          # M-7, strict: eligible + D25-P3-equivalent
                 "matching_ids": [r["signal_id"] for r in matching],
                 "p3_equivalent_candidates_any_eligibility": [r["signal_id"] for r in near],
                 "frozen_selection_ids": sel_ids,
                 "classification": SELECTION_MISMATCH if (matching and sel_ids
                                                          and not set(sel_ids) & {r["signal_id"] for r in matching})
                 else None}
    # A-1's core-trigger hard dimension uses the strict M-7 reading; the other three read the scored candidate.
    hard = {"model_family": dims[0]["status"] == "MATCH", "direction": dims[1]["status"] == "MATCH",
            "extension_direction": dims[3]["status"] == "MATCH", "core_structural_trigger": bool(matching)}
    return {"case_id": cid, "scoring_level": "ENTRY_LEVEL", "positive_or_negative": case["positive_or_negative"],
            "scored_candidate": e, "scored_candidate_eligible": bool(matching),
            "dimensions": dims, "hard_dimensions": hard, "selection": selection, "per_variant": per_variant}


def score_negative_case(case: dict, runs: dict) -> dict:
    lo, hi = (pd.Timestamp(x) for x in case["stated"]["rejected_window_utc"])
    signals, in_window = [], []
    for variant in ("A", "B"):
        el = eligible(runs[variant]["result"].candidates, variant)
        for _, r in el.iterrows():
            t = _t(r["five_second_shift_time"])
            if t is not None and lo <= t < hi:
                signals.append(facts(r))
        cands = runs[variant]["result"].candidates
        if len(cands):
            for _, r in cands[cands["variant"] == variant].iterrows():
                t = _t(r["five_second_shift_time"])
                if t is not None and lo <= t < hi:
                    in_window.append({"signal_id": r["signal_id"], "event_at_trigger": r["event_at_trigger"],
                                      "shift": str(t), "rules_failed_at_trigger": list(r["rules_failed_at_trigger"])})
    return {"case_id": case["case_id"], "scoring_level": "ENTRY_LEVEL", "positive_or_negative": "NEGATIVE",
            "window_utc": [str(lo), str(hi)],
            "result": "NO_ELIGIBLE_CANONICAL_SIGNAL" if not signals else "ELIGIBLE_CANONICAL_SIGNAL_PRODUCED",
            "eligible_signals": signals, "candidates_with_shift_in_window": in_window}


def score_hour_case(case: dict, runs: dict) -> dict:
    """Only source-supported fields (D31-7, mappings M-3/M-4/M-5/M-6)."""
    stated = case["stated"]
    fields, elig_all, rows, selections, diag = [], [], [], {}, []
    for variant in ("A", "B"):
        cands = runs[variant]["result"].candidates
        el = eligible(cands, variant)
        elig_all += [] if not len(el) else list(el["signal_id"])
        rows += [r for _, r in el.iterrows()]
        selections[variant] = parity.select_candidate(cands, variant, runs[variant]["params"]).get("selected")
        if len(cands):
            diag += [{"signal_id": r["signal_id"], "direction": r["direction"],
                      "event_at_trigger": r["event_at_trigger"],
                      "shift": str(_t(r["five_second_shift_time"])),
                      "rules_failed_at_trigger": list(r["rules_failed_at_trigger"])}
                     for _, r in cands[cands["variant"] == variant].iterrows()]
    by_id = {r["signal_id"]: r for r in rows}
    frozen = [by_id[s] for s in selections.values() if s in by_id]
    chosen = frozen[0] if frozen else (min(rows, key=parity.selection_key) if rows else None)
    e = facts(chosen)

    def add(name, engine, expected, ok, scored=True, note=None):
        fields.append({"field": name, "engine": js(engine), "expected": js(expected),
                       "status": ("MATCH" if ok else "MISMATCH") if scored else "NOT_SCORED", "note": note})

    add("setup_exists_in_hour", e is not None, True, e is not None)
    add("direction", None if e is None else e["direction"], case["direction"],
        e is not None and e["direction"] == case["direction"])
    add("model_family", None if e is None else "CBR1H", "CBR1H (M-3: journal labels are not scored as subtypes)",
        e is not None, True, f"journal MTF label: {stated['mtf_model']} (recorded, not scored)")
    allowed = JOURNAL_CONDITION.get(stated["condition"])
    add("condition", None if e is None else e["condition"], allowed if allowed else f"{stated['condition']} (M-4: not scored)",
        bool(allowed) and e is not None and e["condition"] in allowed, scored=bool(allowed))
    bucket = TIMING_BUCKET.get(stated["cb_hour"])
    minute = None
    if e is not None and e["five_second_shift_time"]:
        minute = (pd.Timestamp(e["five_second_shift_time"]) - pd.Timestamp(case["start_time"])) / M1
    add("timing_bucket", minute, f"CB {stated['cb_hour']} -> [{bucket[0]}, {bucket[1]}) minutes" if bucket else None,
        bucket is not None and minute is not None and bucket[0] <= minute < bucket[1], scored=bucket is not None)
    scored_fields = [f for f in fields if f["status"] != "NOT_SCORED"]
    match = all(f["status"] == "MATCH" for f in scored_fields)
    return {"case_id": case["case_id"], "scoring_level": "HOUR_LEVEL", "positive_or_negative": "POSITIVE",
            "verdict": "HOUR_MATCH" if match else "HOUR_MISMATCH", "fields": fields,
            "scored_candidate": e, "eligible_ids": elig_all, "frozen_selection": js(selections),
            "all_candidates": js(diag), "journal": stated}


# ------------------------------------------------------------------ complete run

def run_complete(repeat: int) -> dict:
    rec = verify_freeze()
    cases = {c["case_id"]: c for c in load_set()["cases"]}
    results, engine_hashes = {}, {}
    order = ["CX-LT1-1", "CX-TE1-1", "CX-LT3-2", "CX-LT3-1", "JM-2025-10-16", "JM-2025-10-17", "JM-2025-10-29"]
    cache: dict[str, dict] = {}
    for cid in order:
        case = cases[cid]
        key = f"{case['start_time']}|{case['data_span_utc']}"
        if key not in cache:
            cache[key] = run_hour(case)
        runs = cache[key]
        engine_hashes.update({f"{cid}|{v}": runs[v]["hash"] for v in ("A", "B")})
        if case["scoring_level"] == "HOUR_LEVEL":
            results[cid] = score_hour_case(case, runs)
        elif case["positive_or_negative"] == "NEGATIVE":
            results[cid] = score_negative_case(case, runs)
        else:
            results[cid] = score_entry_case(case, runs)
    payload = {"run_id": RUN_ID, "freeze_commit": rec["git_commit"], "pc3_spec_hash": spec_hash_pc3(),
               "pc2_spec_hash": spec_hash(), "parity_manifest_hash": load_set()["manifest_hash"],
               "cases": results, "engine_result_hashes": engine_hashes}
    out = {"repeat": repeat, "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
           "result_hash": payload_hash(payload), "payload": js(payload)}
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / f"run-{repeat}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out


def verdict(run1: dict, run2: dict) -> dict:
    """D31-16, applied verbatim."""
    pl = run1["payload"]
    fails, concerns = [], []
    if run1["result_hash"] != run2["result_hash"]:
        fails.append("determinism: the repeat run differs")
    entry = [pl["cases"][c] for c in ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2")]
    hard_counts = {k: sum(1 for c in entry if c["hard_dimensions"][k]) for k in
                   ("model_family", "direction", "extension_direction", "core_structural_trigger")}
    for k, n in hard_counts.items():
        if n < 3:
            failing = [c["case_id"] for c in entry if not c["hard_dimensions"][k]]
            fails.append(f"entry-level hard dimension {k}: {n}/3 ({', '.join(failing)})")
    for c in entry:
        for d in c["dimensions"]:
            if d["status"] == "MISMATCH":
                concerns.append(f"{c['case_id']} dim {d['n']} {d['name']}: {d['class']}"
                                + (f" — {d['note']}" if d.get("note") else ""))
        if c["selection"]["classification"]:
            concerns.append(f"{c['case_id']}: {SELECTION_MISMATCH}")
    neg = pl["cases"]["CX-LT3-1"]
    if neg["result"] != "NO_ELIGIBLE_CANONICAL_SIGNAL":
        fails.append("negative control CX-LT3-1 produced an eligible canonical signal")
    hours = [pl["cases"][c] for c in ("JM-2025-10-16", "JM-2025-10-17", "JM-2025-10-29")]
    hour_matches = sum(1 for c in hours if c["verdict"] == "HOUR_MATCH")
    if hour_matches <= 1:
        fails.append(f"hour-level: {hour_matches}/3 HOUR_MATCH (D31-8: 0/3 or 1/3 is a FAIL)")
    elif hour_matches == 2:
        concerns.append("hour-level: 2/3 HOUR_MATCH (D31-8 caps the verdict at PASS WITH CONCERNS)")
    for c in hours:
        for f in c["fields"]:
            if f["status"] == "MISMATCH":
                concerns.append(f"{c['case_id']} {f['field']}: engine {f['engine']} vs source {f['expected']}")
    if fails:
        v = "FAIL"
    elif concerns:
        v = "PASS WITH CONCERNS"
    else:
        v = "PASS"
    return {"verdict": v, "fail_reasons": fails, "concerns": concerns,
            "entry_hard_counts": hard_counts, "hour_matches": f"{hour_matches}/3",
            "negative_control": neg["result"], "deterministic": run1["result_hash"] == run2["result_hash"],
            "result_hashes": [run1["result_hash"], run2["result_hash"]]}


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "freeze":
        r = freeze()
        print(json.dumps({"run_id": r["run_id"], "commit": r["git_commit"], "tests": r["pre_execution_tests"],
                          "hashes_verified": r["verified_hashes"]}, indent=2))
    elif cmd == "run":
        out = run_complete(int(args[1]))
        print(json.dumps({"repeat": out["repeat"], "result_hash": out["result_hash"]}, indent=2))
    elif cmd == "report":
        from cbr.engine.phase13c_report import write_reports
        print(json.dumps(write_reports(), indent=2))
    else:
        raise SystemExit("usage: python -m cbr.engine.phase13c_run [freeze|run N|report]")


if __name__ == "__main__":
    main()
