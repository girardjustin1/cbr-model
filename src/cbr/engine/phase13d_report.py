"""Phase 13D report writer (CBR-PROT-013D §8). Presentation only: it reads the two frozen run files and applies the
frozen verdict rules in `phase13d_run.verdict`. It computes no new scores and may not be used to change any."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from cbr.engine.phase13d_run import (
    ENTRY_POSITIVES,
    FREEZE_MANIFEST,
    HOUR_CASE,
    NEGATIVE,
    REPORTS,
    RUN_DIR,
    RUN_ID,
    load_set,
    verdict,
)

TAXONOMY = ["DATA_LIMITATION", "FEED_DIFFERENCE", "FEED_DEPENDENT_SIGNAL_DIFFERENCE", "EXECUTION_DEPENDENT",
            "OWNER_BASELINE_CHOICE", "UNRESOLVED_SPEC_AMBIGUITY", "IMPLEMENTATION_BUG", "CANON_MISMATCH",
            "CANDIDATE_SELECTION_MISMATCH", "PARITY_SET_CORRECTION"]


def write_reports() -> dict:
    freeze = json.loads(FREEZE_MANIFEST.read_text())
    r1 = json.loads((RUN_DIR / "run-1.json").read_text())
    r2 = json.loads((RUN_DIR / "run-2.json").read_text())
    v = verdict(r1, r2)
    cases = r1["payload"]["cases"]
    register = []
    for cid in ENTRY_POSITIVES:
        c = cases[cid]
        for d in c["dimensions"]:
            if d["status"] == "MISMATCH":
                register.append({"case": cid, "dimension": f"{d['n']} {d['name']}", "hard": d["hard"],
                                 "class": d["class"], "engine": d["engine"], "expected": d["expected"],
                                 "note": d["note"]})
        if c["selection"]["classification"]:
            register.append({"case": cid, "dimension": "candidate selection", "hard": False,
                             "class": c["selection"]["classification"],
                             "engine": c["selection"]["c_frozen_selection"],
                             "expected": c["selection"]["matching_ids"], "note": "never a trigger failure (D35 §6)"})
    for f in cases[HOUR_CASE]["fields"]:
        if f["status"] == "MISMATCH":
            register.append({"case": HOUR_CASE, "dimension": f["field"], "hard": False,
                             "class": "CANON_MISMATCH", "engine": f["engine"], "expected": f["expected"],
                             "note": "hour-level: reported, classified and retained as a concern (D35 §5)"})
    payload = {"run_id": RUN_ID, "protocol": "CBR-PROT-013D v1.1", "ruling": "D35",
               "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
               "freeze": freeze, "verdict": v, "cases": cases, "mismatch_register": register,
               "result_hashes": {"run_1": r1["result_hash"], "run_2": r2["result_hash"]}}
    (REPORTS / "phase13d-parity.json").write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13d-run-manifest.json").write_text(json.dumps(
        {"run_id": RUN_ID, "protocol_hash": freeze["files"]["docs/governance/phase13d-pc4-parity-protocol.md"],
         "ruling_hash": freeze["files"]["docs/governance/d35-pc4-scored-parity-authorization.md"],
         "pc4_spec_hash": r1["payload"]["pc4_spec"], "pc3_spec_hash": r1["payload"]["pc3_spec"],
         "pc2_spec_hash": r1["payload"]["pc2_spec"], "parity_manifest_hash": r1["payload"]["parity_manifest_v2"],
         "git_commit": freeze["git_commit"], "market_data_hashes": freeze["market_data_hashes"],
         "evidence_hashes": freeze["evidence_hashes"],
         "engine_result_hashes": r1["payload"]["engine_result_hashes"],
         "result_hashes": {"run_1": r1["result_hash"], "run_2": r2["result_hash"]},
         "deterministic": v["deterministic"], "verdict": v["verdict"]}, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13d-parity.md").write_text(markdown(payload))
    return {"verdict": v["verdict"], "entry_hard": v["entry_hard_counts"], "hour_level": v["hour_level"],
            "negative_control": v["negative_control"], "deterministic": v["deterministic"],
            "mismatches": len(register)}


def _yn(b) -> str:
    return "yes" if b else "**no**"


def markdown(p: dict) -> str:
    v, cases = p["verdict"], p["cases"]
    counts = load_set()["counts"]
    L = [f"# Phase 13D — PC4 Scored Behavioural Parity ({p['run_id']})", "",
         (f"**Protocol:** {p['protocol']} · **Authorization:** owner ruling {p['ruling']} · "
          f"**Generated:** {p['generated_utc']}"), "",
         f"## Verdict: {v['verdict']}", ""]
    if v["fail_reasons"]:
        L += ["**Failing requirements**", ""] + [f"- {x}" for x in v["fail_reasons"]] + [""]
    L += ["| Gate | Result |", "|---|---|",
          "| Entry-level hard dimensions (D-1) | " +
          ", ".join(f"{k} {n}/3" for k, n in v["entry_hard_counts"].items()) + " |",
          f"| Hour-level (D-3, E-2 threshold) | {v['hour_level']} |",
          f"| Negative control {NEGATIVE} (D-4) | {v['negative_control']} |",
          f"| Determinism (D-5) | {_yn(v['deterministic'])} — `{p['result_hashes']['run_1'][:16]}…` |",
          (f"| Frozen hashes | PC4 `{p['freeze']['verified_hashes']['pc4_spec'][:12]}…`, manifest "
           f"`{p['freeze']['verified_hashes']['parity_manifest_v2'][:12]}…`, PC3 "
           f"`{p['freeze']['verified_hashes']['pc3_spec'][:12]}…`, PC2 "
           f"`{p['freeze']['verified_hashes']['pc2_spec'][:12]}…` (all unchanged) |"),
          f"| Pre-execution suite | {p['freeze']['pre_execution_tests']} |",
          f"| Pre-freeze real-case smoke run (D35 §8) | {p['freeze']['pre_freeze_real_case_smoke_run']} |", ""]
    L += ["## Strict and descriptive views (pre-declared, D35 §6)", "",
          ("**STRICT** scores only eligible candidates and is the only view that touches acceptance. "
           "**DESCRIPTIVE** shows the closest structurally relevant candidate so the report can name the rule that "
           "blocked it; it can never satisfy acceptance. Each case below states which view its scored row came from."),
          ""]
    for cid in (*ENTRY_POSITIVES, NEGATIVE):
        c = cases[cid]
        L += [f"## {cid} ({c['positive_or_negative'].lower()}, ENTRY_LEVEL) — view: {c['view']}", ""]
        if c["positive_or_negative"] == "NEGATIVE":
            L += [f"Window {c['window_utc'][0]} → {c['window_utc'][1]}. **{c['result']}**.", "",
                  "| Candidate | Shift | Trigger verdict | Failing rules at trigger |", "|---|---|---|---|"]
            L += [f"| `{x['signal_id'].split('/')[-1]}` | {x['shift']} | {x['event_at_trigger']} | "
                  f"{', '.join(x['rules_failed_at_trigger']) or '—'} |" for x in c["candidates_with_shift_in_window"]]
            if not c["candidates_with_shift_in_window"]:
                L.append("| — | — | — | no candidate of any kind had a 5s shift in the rejected window |")
            L.append("")
            continue
        sc = c["scored_candidate"]
        L += [(f"Scored candidate: `{sc['signal_id']}` (eligible: {_yn(c['scored_candidate_eligible'])})" if sc
               else "**No candidate of any kind in the hour.**"), "",
              "| # | Dimension | Hard | Engine | Source | Status | Class |", "|---|---|---|---|---|---|---|"]
        for d in c["dimensions"]:
            L.append(f"| {d['n']} | {d['name']} | {'yes' if d['hard'] else 'no'} | "
                     f"`{json.dumps(d['engine'])[:100]}` | `{json.dumps(d['expected'])[:60]}` | {d['status']} | "
                     f"{d['class'] or '—'} |")
        sel = c["selection"]
        L += ["", (f"**Selection (D35 §6).** A — expected structural event exists: "
                   f"{_yn(sel['a_structural_event_exists'])}. B — eligible expected event exists: "
                   f"{_yn(sel['b_eligible_expected_event_exists'])}. C — frozen selector chose: "
                   f"{', '.join(x.split('/')[-1] for x in sel['c_frozen_selection']) or 'none'}. "
                   f"Classification: {sel['classification'] or '—'}."), "",
              "| Variant | Candidates | Eligible | Frozen selection | Selection eligible |",
              "|---|---|---|---|---|"]
        for var, pv in c["per_variant"].items():
            L.append(f"| {var} | {pv['candidates']} | {pv['eligible']} | "
                     f"`{(pv['frozen_selection'] or '—').split('/')[-1]}` | {_yn(pv['frozen_selection_eligible'])} |")
        L.append("")
    c = cases[HOUR_CASE]
    j = c["journal"]
    L += [f"## {HOUR_CASE} (HOUR_LEVEL) — **{c['verdict']}**", "",
          (f"Journal row: {j['journal_time_local']} · {j['mtf_model']} · {j['condition']} · CB {j['cb_hour']} · "
           f"{j['shifts']}. Source level L1_FRAME_JOURNAL_TABLE, model_scope CONFIRMED_CBR1H."), "",
          "| Field | Engine | Source | Status |", "|---|---|---|---|"]
    for f in c["fields"]:
        L.append(f"| {f['field']} | `{json.dumps(f['engine'])[:80]}` | `{json.dumps(f['expected'])[:60]}` | "
                 f"{f['status']} |")
    L += ["", (f"Eligible candidates in the hour: "
               f"{', '.join(x.split('/')[-1] for x in c['eligible_ids']) or 'none'}."), "",
          "| Candidate | Dir | Shift | Trigger verdict | Failing rules at trigger |", "|---|---|---|---|---|"]
    for x in c["all_candidates"]:
        L.append(f"| `{x['signal_id'].split('/')[-1]}` | {x['direction']} | {x['shift']} | {x['event_at_trigger']} | "
                 f"{', '.join(x['rules_failed_at_trigger']) or '—'} |")
    L += ["", "## Mismatch register", ""]
    if p["mismatch_register"]:
        L += ["| Case | Dimension | Hard | Class | Engine | Source |", "|---|---|---|---|---|---|"]
        L += [f"| {m['case']} | {m['dimension']} | {'yes' if m['hard'] else 'no'} | {m['class']} | "
              f"`{json.dumps(m['engine'])[:70]}` | `{json.dumps(m['expected'])[:50]}` |"
              for m in p["mismatch_register"]]
        L += ["", "Taxonomy order: " + " → ".join(TAXONOMY) + ".",
              "Every mismatch has exactly one primary classification; none is unclassified."]
    else:
        L.append("No mismatches.")
    L += ["", "## Concerns", ""] + ([f"- {x}" for x in v["concerns"]] or ["- none"])
    L += ["", "## Limits of this run (CBR-PROT-013D §11)", "",
          (f"- Binding machine set: {counts['binding_entry_level']} ENTRY_LEVEL + "
           f"{counts['binding_hour_level']} HOUR_LEVEL — XAUUSD only, CBR1H only."),
          "- The hour-level evidence is a **single** case, weaker than the three D31 used.",
          "- CBR15-PC4 is SPEC_ONLY and unscored; FS/IFS contexts are not implemented.",
          "- `k = 3` is fixed; CX-LT3-2's trigger is known to disappear at `k = 4`.",
          ("- PC4 carries the OQ-48 anchor/counting/unit, minute-7 activation, the Q1 qualifier, k = 3, the "
           "tradable-time window, the extension origin and the F-10 Q interpretation as **assumptions**. A PASS does "
           "not promote any of them into CANON."),
          "- No P&L, fills or trade outcomes were read at any point.", "",
          "## Stop", "",
          ("Phase 13D is complete and execution stops here. PC4 is unchanged since the freeze, no corrective run was "
           "launched, and Phase 14 is not started."), ""]
    return "\n".join(L)
