"""Phase 13D scored parity run of PC4 (CBR-PROT-013D v1.1, owner ruling D35). Run id CBR-RUN-013D-1.

    .venv/bin/python -m cbr.engine.phase13d_run freeze     # verify frozen hashes + full suite -> reports/phase13d-freeze-manifest.json
    .venv/bin/python -m cbr.engine.phase13d_run run 1      # complete binding machine run -> data/phase13d/run-1.json
    .venv/bin/python -m cbr.engine.phase13d_run run 2      # deterministic repeat from the same frozen inputs
    .venv/bin/python -m cbr.engine.phase13d_run report     # determinism check, verdict, reports/phase13d-*

Signal state only: no fills, outcomes or P&L. PC4, the corrected manifest and the scoring fields are never modified
during the run, and no alternative setting is tested (D35 §13).

Scoring reuses the frozen Phase 13C helpers so the dimensions mean exactly what they meant for PC3: the same
D25-P3 equivalence, the same accepted-condition sets, the same journal mappings. Only the candidate engine, the
binding set and the D35 acceptance rules differ.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.engine import cbr1h_pc4 as pc4
from cbr.engine import parity
from cbr.engine.params import ROOT, spec_hash
from cbr.engine.params_pc3 import spec_hash_pc3
from cbr.engine.params_pc4 import load_cbr1h_pc4, spec_hash_pc4
from cbr.engine.parity_set_v2 import MANIFEST_V2
from cbr.engine.phase13_behavioral import js, payload_hash
from cbr.engine.phase13c_run import (
    ACCEPTED_CONDITIONS,
    COURSE_EXTENSION_DIR,
    JOURNAL_CONDITION,
    SELECTION_MISMATCH,
    TIMING_BUCKET,
    TOM_TIMES,
    facts,
    p3_equivalent,
)

RUN_ID = "CBR-RUN-013D-1"
FREEZE_MANIFEST = ROOT / "reports" / "phase13d-freeze-manifest.json"
RUN_DIR = ROOT / "data" / "phase13d"
REPORTS = ROOT / "reports"
H1, M1, S5 = pd.Timedelta(hours=1), pd.Timedelta(minutes=1), pd.Timedelta(seconds=5)
EXPECTED_HASHES = {                                            # D35 §1
    "pc4_spec": "62a2310e43d7cf57a6fafe318a4d1d7ed094d2d629e7f5ea8b20098db8e4d0b7",
    "parity_manifest_v2": "e12f3882f01b8ac4655520f00d5cd19829da989a371a1feb15b070d1a718804e",
    "pc3_spec": "7032f400688ada1d5e9691d79a19f7ce78f6d830ad3124f588975f41b7c5d453",
    "pc2_spec": "4dadc8b99cc4134888e5778704c0863d269d6f43ef9a5e47b1ba07fcb1b663b2",
}
FROZEN_FILES = [
    "docs/governance/phase13d-pc4-parity-protocol.md", "docs/governance/d35-pc4-scored-parity-authorization.md",
    "docs/governance/d34-pc4-authorization.md", "docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC4.yaml",
    "docs/strategy/parity-candidates/CBR1H_BASELINE_V1-PC3.yaml", "research/examples/parity_set_manifest_v2.json",
    "config/strategy.yaml", "config/strategy_pc3.yaml", "config/strategy_pc4.yaml",
    "src/cbr/engine/cbr1h_pc4.py", "src/cbr/engine/params_pc4.py", "src/cbr/engine/parity.py",
    "src/cbr/engine/parity_set_v2.py", "src/cbr/engine/phase13d_run.py", "src/cbr/structure/shifts_pc4.py",
    "src/cbr/structure/shifts_pc3.py", "src/cbr/structure/overextension_pc3.py",
    "src/cbr/structure/condition_pc3.py",
]
ENTRY_POSITIVES = ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2")
NEGATIVE, HOUR_CASE = "CX-LT3-1", "JM-2025-10-16"
BINDING = (*ENTRY_POSITIVES, NEGATIVE, HOUR_CASE)
# D35 §3: the hard dimensions, frozen before execution. Dimension 3 (condition) is scored but is not hard.
HARD = ("model_family", "direction", "extension_direction", "extension_activation",
        "location_or_previous_candle_event", "hvcs_state", "type3_5s_structural_trigger", "eligible_candidate")


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def load_set() -> dict:
    return json.loads(MANIFEST_V2.read_text())


def live_hashes() -> dict:
    return {"pc4_spec": spec_hash_pc4(), "parity_manifest_v2": load_set()["manifest_hash"],
            "pc3_spec": spec_hash_pc3(), "pc2_spec": spec_hash()}


def _t(v):
    return None if v is None or (not isinstance(v, pd.Timestamp) and pd.isna(v)) else pd.Timestamp(v)


# ------------------------------------------------------------------ freeze (D35 §1, STEP 1-2)

def freeze() -> dict:
    if FREEZE_MANIFEST.exists():
        raise SystemExit(f"{FREEZE_MANIFEST.relative_to(ROOT)} exists: already frozen (a change needs a new run id)")
    if _git("status", "--porcelain"):
        raise SystemExit("uncommitted changes: commit the run code before freezing")
    got = live_hashes()
    bad = {k: (v, got[k]) for k, v in EXPECTED_HASHES.items() if got[k] != v}
    if bad:
        raise SystemExit(f"STOP (D35 §1): frozen hash differs; nothing is regenerated automatically: {bad}")
    res = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True, check=False)
    summary = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-400:]
    if res.returncode != 0:
        raise SystemExit(f"pre-execution suite failed: {summary}")
    lint = subprocess.run([str(ROOT / ".venv" / "bin" / "ruff"), "check", "src", "tests"], cwd=ROOT,
                          capture_output=True, text=True, check=False)
    data_hashes, evidence_hashes = {}, {}
    for case in load_set()["cases"]:
        if case["case_id"] in BINDING:
            data_hashes.update(case["market_data_hashes"])
            evidence_hashes.update(case["evidence_hashes"])
    rec = {"run_id": RUN_ID, "ruling": "D35", "protocol": "CBR-PROT-013D v1.1",
           "frozen_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
           "git_commit": _git("rev-parse", "HEAD"), "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
           "expected_hashes": EXPECTED_HASHES, "verified_hashes": got,
           "files": {f: sha(f) for f in FROZEN_FILES}, "market_data_hashes": data_hashes,
           "evidence_hashes": evidence_hashes, "binding_cases": list(BINDING),
           "pre_execution_tests": summary,
           "lint": lint.stdout.strip().splitlines()[-1] if lint.stdout.strip() else "clean",
           "pre_freeze_real_case_smoke_run": "NONE — every PC4 invocation before this freeze is in "
                                             "tests/engine/test_cbr1h_pc4.py against a synthetic random walk (D35 §8)"}
    FREEZE_MANIFEST.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def verify_freeze() -> dict:
    if not FREEZE_MANIFEST.exists():
        raise SystemExit("not frozen: run `freeze` first")
    rec = json.loads(FREEZE_MANIFEST.read_text())
    pinned = {**rec["files"], **rec["market_data_hashes"], **rec["evidence_hashes"]}
    changed = [f for f, h in pinned.items() if sha(f) != h]
    got = live_hashes()
    if changed or got != rec["verified_hashes"]:
        raise SystemExit(f"STOP (D35 §1): frozen inputs changed after the freeze: {changed or got}")
    return rec


# ------------------------------------------------------------------ engine execution

def run_hour(case: dict) -> dict:
    a, b = (pd.Timestamp(x) for x in case["data_span_utc"])
    h0 = pd.Timestamp(case["start_time"])
    s1m, s5s = cb.load_structure(a, b, "1m"), cb.load_structure(a, b, "5s")
    out = {}
    for variant in ("A", "B"):
        p = load_cbr1h_pc4(variant)
        res = pc4.run_cbr1h_pc4(s1m, s5s, start=h0, end=h0 + H1, variant=variant, params=p)
        out[variant] = {"result": res, "params": p, "hash": pc4.result_hash(res)}
    return out


def eligible(cands: pd.DataFrame, variant: str) -> pd.DataFrame:
    if not len(cands):
        return cands
    c = cands[cands["variant"] == variant]
    return c[c["event_at_trigger"] == "ARMED_AT_TRIGGER"]


# ------------------------------------------------------------------ scoring

def score_entry_case(case: dict, runs: dict) -> dict:
    """The nine frozen dimensions; eight are hard (D35 §3). Strict and descriptive views are both reported."""
    cid = case["case_id"]
    want_dir, want_ext = case["direction"], COURSE_EXTENSION_DIR[cid]
    per_variant, matching, all_cands, sel_all = {}, [], [], []
    for variant in ("A", "B"):
        cands = runs[variant]["result"].candidates
        el = eligible(cands, variant)
        sel = parity.select_candidate(cands, variant, runs[variant]["params"])
        by_id = {r["signal_id"]: r for _, r in el.iterrows()} if len(el) else {}
        if sel.get("selected"):
            sel_all.append(sel["selected"])
        if len(cands):
            all_cands += [r for _, r in cands[cands["variant"] == variant].iterrows()]
        for _, r in el.iterrows():
            if p3_equivalent(_t(r["five_second_shift_time"]), cid, r["direction"] == want_dir):
                matching.append(r)
        per_variant[variant] = {
            "candidates": 0 if not len(cands) else int((cands["variant"] == variant).sum()),
            "eligible": len(el), "frozen_selection": sel.get("selected"),
            "frozen_selection_eligible": sel.get("selected") in by_id,
            "eligible_ids": [] if not len(el) else list(el["signal_id"]),
        }
    near = [r for r in all_cands if p3_equivalent(_t(r["five_second_shift_time"]), cid, r["direction"] == want_dir)]
    # STRICT scores the eligible D25-P3-equivalent candidate. DESCRIPTIVE falls back to the closest candidate so the
    # report can name the blocking rule; it can never satisfy acceptance (D35 §6).
    strict_row = matching[0] if matching else None
    order = matching or near or [r for r in all_cands if r["signal_id"] in sel_all] or all_cands
    scored_row = min(order, key=parity.selection_key) if len(order) else None
    view = "STRICT" if strict_row is not None else "DESCRIPTIVE"
    e = facts(scored_row)
    failed = [] if e is None else list(scored_row["rules_failed_at_trigger"])
    dims = []

    def add(n, name, engine, expected, ok, cls=None, note=None):
        dims.append({"n": n, "name": name, "engine": js(engine), "expected": js(expected),
                     "status": "MATCH" if ok else "MISMATCH", "class": None if ok else cls, "note": note,
                     "hard": name in HARD})

    add(1, "model_family", None if e is None else e["entry_model"], "CBR1H", e is not None, "CANON_MISMATCH")
    add(2, "direction", None if e is None else e["direction"], want_dir, e is not None and e["direction"] == want_dir,
        "CANON_MISMATCH")
    cond_ok = e is not None and any(e["condition"] == a["condition"]
                                    and ("direction" not in a or a["direction"] == e["cond_direction"])
                                    for a in ACCEPTED_CONDITIONS[cid])
    add(3, "condition", None if e is None else {"condition": e["condition"], "cond_direction": e["cond_direction"],
                                                "fallback_applied": e["condition_fallback_applied"]},
        ACCEPTED_CONDITIONS[cid], cond_ok, "OWNER_BASELINE_CHOICE",
        "PC4 keeps PC3's approved OQ-46 correction; D25-P6 named the accepted set" if
        (e is not None and e["condition_fallback_applied"]) else None)
    add(4, "extension_direction", None if e is None else e["oe_dir"], want_ext,
        e is not None and e["oe_dir"] == want_ext, "CANON_MISMATCH")
    add(5, "extension_activation", None if e is None else {"state": e["extension_state"],
                                                           "activation_time": e["extension_activation_time"]},
        "EXTENSION_ACTIVE", e is not None and e["extension_state"] == "EXTENSION_ACTIVE", "CANON_MISMATCH")
    loc_rules = [r for r in failed if r.startswith(("M1H-LOC-", "M1H-6A-2", "M1H-6A-3"))]
    add(6, "location_or_previous_candle_event",
        None if e is None else {"q_break_by_q_at_trigger": e.get("q_break_by_q_at_trigger"),
                                "pos_oe_extreme": e["pos_oe_extreme"], "failed_rules": loc_rules},
        "location and previous-15m rules pass at the shift (F-9)", e is not None and not loc_rules, "CANON_MISMATCH")
    add(7, "hvcs_state", None if e is None else {"state": e["hvcs_rule_state"], "minutes": e["hvcs_minutes"],
                                                 "violations": e.get("hvcs_violations"),
                                                 "to_shift_diagnostic": e.get("hvcs_to_shift_minutes"),
                                                 "failed_rules": [r for r in failed if "HVCS" in r]},
        "valid at the shift for variant A; not applicable for variant B",
        e is not None and (e["variant"] == "B" or e["hvcs_rule_state"] is True), "CANON_MISMATCH")
    shift = None if e is None else _t(scored_row["five_second_shift_time"])
    equiv = e is not None and p3_equivalent(shift, cid, e["direction"] == want_dir)
    add(8, "type3_5s_structural_trigger",
        None if e is None else {"shift_time": e["five_second_shift_time"],
                                "trigger_at_decision": e["five_second_shift_level"],
                                "trigger_at_break": e["five_second_shift_level_at_trigger"],
                                "reanchored": e["trigger_reanchored"]},
        {"tom_interval": TOM_TIMES[cid][:2], "rule": "D25-P3 equivalence"}, equiv, "CANON_MISMATCH")
    add(9, "eligible_candidate", None if e is None else {"event_at_trigger": e["event_at_trigger"],
                                                         "rules_failed_at_trigger": failed},
        "ARMED_AT_TRIGGER", bool(matching), "CANON_MISMATCH",
        None if matching else "strict: no D25-P3-equivalent candidate reached ARMED_AT_TRIGGER")
    selection = {"a_structural_event_exists": bool(near),
                 "b_eligible_expected_event_exists": bool(matching),
                 "c_frozen_selection": sel_all,
                 "matching_ids": [r["signal_id"] for r in matching],
                 "classification": SELECTION_MISMATCH if (matching and sel_all
                                                          and not set(sel_all) & {r["signal_id"] for r in matching})
                 else None}
    hard = {d["name"]: d["status"] == "MATCH" for d in dims if d["hard"]}
    return {"case_id": cid, "scoring_level": "ENTRY_LEVEL", "positive_or_negative": case["positive_or_negative"],
            "view": view, "scored_candidate": e, "scored_candidate_eligible": bool(matching),
            "dimensions": dims, "hard_dimensions": hard, "selection": selection, "per_variant": per_variant}


def score_negative_case(case: dict, runs: dict) -> dict:
    lo, hi = (pd.Timestamp(x) for x in case["stated"]["rejected_window_utc"])
    signals, in_window = [], []
    for variant in ("A", "B"):
        for _, r in eligible(runs[variant]["result"].candidates, variant).iterrows():
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
            "view": "STRICT", "window_utc": [str(lo), str(hi)],
            "result": "NO_ELIGIBLE_CANONICAL_SIGNAL" if not signals else "ELIGIBLE_CANONICAL_SIGNAL_PRODUCED",
            "eligible_signals": signals, "candidates_with_shift_in_window": in_window}


def score_hour_case(case: dict, runs: dict) -> dict:
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
                      "event_at_trigger": r["event_at_trigger"], "shift": str(_t(r["five_second_shift_time"])),
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
    add("model_family", None if e is None else "CBR1H", "CBR1H (journal labels are not scored as subtypes)",
        e is not None, True, f"journal MTF label: {stated['mtf_model']} (recorded, not scored)")
    allowed = JOURNAL_CONDITION.get(stated["condition"])
    add("condition", None if e is None else e["condition"],
        allowed if allowed else f"{stated['condition']} (not scored)",
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
            "view": "STRICT", "verdict": "HOUR_MATCH" if match else "HOUR_MISMATCH", "fields": fields,
            "scored_candidate": e, "eligible_ids": elig_all, "frozen_selection": js(selections),
            "all_candidates": js(diag), "journal": stated}


# ------------------------------------------------------------------ complete run

def run_complete(repeat: int) -> dict:
    rec = verify_freeze()
    cases = {c["case_id"]: c for c in load_set()["cases"]}
    results, engine_hashes, cache = {}, {}, {}
    for cid in BINDING:
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
    payload = {"run_id": RUN_ID, "freeze_commit": rec["git_commit"], **live_hashes(),
               "cases": results, "engine_result_hashes": engine_hashes}
    out = {"repeat": repeat, "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
           "result_hash": payload_hash(payload), "payload": js(payload)}
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / f"run-{repeat}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out


def verdict(run1: dict, run2: dict) -> dict:
    """D35 §9, applied verbatim."""
    pl = run1["payload"]
    fails, concerns = [], []
    if run1["result_hash"] != run2["result_hash"]:
        fails.append("determinism: the repeat run differs")
    entry = [pl["cases"][c] for c in ENTRY_POSITIVES]
    counts = {k: sum(1 for c in entry if c["hard_dimensions"][k]) for k in HARD}
    for k, n in counts.items():
        if n < 3:
            failing = [c["case_id"] for c in entry if not c["hard_dimensions"][k]]
            fails.append(f"entry-level hard dimension {k}: {n}/3 ({', '.join(failing)})")
    for c in entry:
        for d in c["dimensions"]:
            if d["status"] == "MISMATCH" and not d["hard"]:
                concerns.append(f"{c['case_id']} dim {d['n']} {d['name']}: {d['class']}"
                                + (f" — {d['note']}" if d.get("note") else ""))
        if c["selection"]["classification"]:
            concerns.append(f"{c['case_id']}: {SELECTION_MISMATCH} (never a trigger failure, D35 §6)")
    neg = pl["cases"][NEGATIVE]
    if neg["result"] != "NO_ELIGIBLE_CANONICAL_SIGNAL":
        fails.append(f"negative control {NEGATIVE} admitted the rejected setup")
    hour = pl["cases"][HOUR_CASE]
    hour_match = hour["verdict"] == "HOUR_MATCH"
    if not hour_match:                                    # D35 §5: never an independent FAIL
        concerns.append(f"{HOUR_CASE}: HOUR_MISMATCH — caps the verdict at PASS WITH CONCERNS (E-2)")
        for f in hour["fields"]:
            if f["status"] == "MISMATCH":
                concerns.append(f"{HOUR_CASE} {f['field']}: engine {f['engine']} vs source {f['expected']}")
    if fails:
        v = "FAIL"
    elif concerns:
        v = "PASS WITH CONCERNS"
    else:
        v = "PASS"
    return {"verdict": v, "fail_reasons": fails, "concerns": concerns, "entry_hard_counts": counts,
            "hour_level": f"{int(hour_match)}/1 HOUR_MATCH", "negative_control": neg["result"],
            "deterministic": run1["result_hash"] == run2["result_hash"],
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
        from cbr.engine.phase13d_report import write_reports
        print(json.dumps(write_reports(), indent=2))
    else:
        raise SystemExit("usage: python -m cbr.engine.phase13d_run [freeze|run N|report]")


if __name__ == "__main__":
    main()
