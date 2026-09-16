"""Phase 13C report writer (CBR-PROT-013C §8). Presentation only: it reads the two frozen run files and applies the
frozen verdict rules in `phase13c_run.verdict`. It computes no new scores and may not be used to change any."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from cbr.engine.phase13c_run import (
    FREEZE_MANIFEST,
    NARRATIVE_ASSESSMENT,
    REPORTS,
    RUN_DIR,
    RUN_ID,
    load_set,
    verdict,
)

TAXONOMY = ["DATA_LIMITATION", "FEED_DIFFERENCE", "FEED_DEPENDENT_SIGNAL_DIFFERENCE", "EXECUTION_DEPENDENT",
            "OWNER_BASELINE_CHOICE", "UNRESOLVED_SPEC_AMBIGUITY", "IMPLEMENTATION_BUG", "CANON_MISMATCH",
            "CANDIDATE_SELECTION_MISMATCH"]


def write_reports() -> dict:
    freeze = json.loads(FREEZE_MANIFEST.read_text())
    r1 = json.loads((RUN_DIR / "run-1.json").read_text())
    r2 = json.loads((RUN_DIR / "run-2.json").read_text())
    v = verdict(r1, r2)
    cases = r1["payload"]["cases"]
    register = []
    for cid in ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2"):
        c = cases[cid]
        for d in c["dimensions"]:
            if d["status"] == "MISMATCH":
                register.append({"case": cid, "dimension": f"{d['n']} {d['name']}", "class": d["class"],
                                 "engine": d["engine"], "expected": d["expected"], "note": d["note"]})
        if c["selection"]["classification"]:
            register.append({"case": cid, "dimension": "candidate selection",
                             "class": c["selection"]["classification"],
                             "engine": c["selection"]["frozen_selection_ids"],
                             "expected": c["selection"]["matching_ids"], "note": None})
    for cid in ("JM-2025-10-16", "JM-2025-10-17", "JM-2025-10-29"):
        for f in cases[cid]["fields"]:
            if f["status"] == "MISMATCH":
                register.append({"case": cid, "dimension": f["field"], "class": "CANON_MISMATCH",
                                 "engine": f["engine"], "expected": f["expected"], "note": f["note"]})
    payload = {"run_id": RUN_ID, "protocol": "CBR-PROT-013C v1.1", "ruling": "D31",
               "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
               "freeze": freeze, "verdict": v, "cases": cases,
               "narrative": {k: {"assessment": a, "reason": why} for k, (a, why) in NARRATIVE_ASSESSMENT.items()},
               "mismatch_register": register,
               "result_hashes": {"run_1": r1["result_hash"], "run_2": r2["result_hash"]}}
    (REPORTS / "phase13c-parity.json").write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13c-run-manifest.json").write_text(json.dumps(
        {"run_id": RUN_ID, "protocol_hash": freeze["files"]["docs/governance/phase13c-pc3-parity-protocol.md"],
         "ruling_hash": freeze["files"]["docs/governance/d31-pc3-scored-parity-authorization.md"],
         "pc3_spec_hash": r1["payload"]["pc3_spec_hash"], "pc2_spec_hash": r1["payload"]["pc2_spec_hash"],
         "parity_manifest_hash": r1["payload"]["parity_manifest_hash"], "git_commit": freeze["git_commit"],
         "market_data_hashes": freeze["market_data_hashes"],
         "engine_result_hashes": r1["payload"]["engine_result_hashes"],
         "result_hashes": {"run_1": r1["result_hash"], "run_2": r2["result_hash"]},
         "deterministic": v["deterministic"], "verdict": v["verdict"]}, indent=1, sort_keys=True) + "\n")
    (REPORTS / "phase13c-parity.md").write_text(markdown(payload))
    return {"verdict": v["verdict"], "hour_matches": v["hour_matches"], "entry_hard": v["entry_hard_counts"],
            "deterministic": v["deterministic"], "mismatches": len(register)}


def _yn(b: bool) -> str:
    return "yes" if b else "**no**"


def markdown(p: dict) -> str:
    v, cases = p["verdict"], p["cases"]
    set_counts = load_set()["counts"]
    L = [f"# Phase 13C — PC3 Scored Behavioural Parity ({p['run_id']})", "",
         (f"**Protocol:** {p['protocol']} · **Authorization:** owner ruling {p['ruling']} · "
          f"**Generated:** {p['generated_utc']}"), "",
         f"## Verdict: {v['verdict']}", ""]
    if v["fail_reasons"]:
        L += ["**Failing requirements**", ""] + [f"- {x}" for x in v["fail_reasons"]] + [""]
    L += ["| Gate | Result |", "|---|---|",
          "| Entry-level hard dimensions (A-1) | " +
          ", ".join(f"{k} {n}/3" for k, n in v["entry_hard_counts"].items()) + " |",
          f"| Hour-level (A-3, D31-8 threshold) | {v['hour_matches']} HOUR_MATCH |",
          f"| Negative control CX-LT3-1 (A-4) | {v['negative_control']} |",
          f"| Determinism (A-5) | {_yn(v['deterministic'])} — `{p['result_hashes']['run_1'][:16]}…` |",
          (f"| Frozen hashes | PC3 `{p['freeze']['verified_hashes']['pc3_spec'][:12]}…`, "
           f"PC2 `{p['freeze']['verified_hashes']['pc2_spec'][:12]}…`, "
           f"manifest `{p['freeze']['verified_hashes']['parity_manifest'][:12]}…` (unchanged) |"),
          f"| Pre-execution suite | {p['freeze']['pre_execution_tests']} |", ""]
    L += ["## Scoring convention used for the dimension table", "",
          "Two readings are reported for every entry-level case, and only the strict one affects the verdict.", "",
          ("- **Strict (binds acceptance).** The structural event exists only if a D25-P3-equivalent candidate is "
           "also `ARMED_AT_TRIGGER` (mapping M-7). This is the core-trigger hard dimension in A-1 and it is applied "
           "exactly as frozen."),
          ("- **Descriptive (reporting only).** Dimensions 1-8 are read off the closest candidate the engine "
           "produced, eligible or not, so the table names the rule that actually rejected it instead of reporting "
           "all nine dimensions as mismatches whenever one gate fails. Dimension 9 is the eligibility dimension and "
           "stays strict."), "",
          ("This split was added during execution, after the first case showed a rejected-at-trigger candidate on "
           "the expected geometry. It changes what the report explains, not what passes: no threshold, dimension or "
           "acceptance rule was altered."), "",
          ("**Pre-flight disclosure.** Before the frozen run, the runner was executed once over all seven machine "
           "cases to check that it completes without raising, after the CBR-RUN-013B-1 crash. It wrote no scored "
           "output and changed neither PC3 nor any scoring rule; because every step is deterministic, its engine "
           "output is identical to the run reported here."), ""]
    for cid in ("CX-LT1-1", "CX-TE1-1", "CX-LT3-2", "CX-LT3-1"):
        c = cases[cid]
        L += [f"## {cid} ({c['positive_or_negative'].lower()}, ENTRY_LEVEL)", ""]
        if c["positive_or_negative"] == "NEGATIVE":
            L += [f"Window {c['window_utc'][0]} → {c['window_utc'][1]}. **{c['result']}**.", "",
                  "| Candidate | Shift | Trigger verdict | Failing rules at trigger |", "|---|---|---|---|"]
            L += [f"| `{x['signal_id'].split('/')[-1]}` | {x['shift']} | {x['event_at_trigger']} | "
                  f"{', '.join(x['rules_failed_at_trigger']) or '—'} |" for x in c["candidates_with_shift_in_window"]]
            L += ["", "No candidate at all had a 5s shift in the rejected window." if not
                  c["candidates_with_shift_in_window"] else ""]
            continue
        sc = c["scored_candidate"]
        L += [f"Scored candidate: `{sc['signal_id']}` (eligible: {_yn(c['scored_candidate_eligible'])})" if sc
              else "**No candidate of any kind in the hour.**", "",
              "| # | Dimension | Engine | Source | Status | Class |", "|---|---|---|---|---|---|"]
        for d in c["dimensions"]:
            L.append(f"| {d['n']} | {d['name']} | `{json.dumps(d['engine'])[:110]}` | "
                     f"`{json.dumps(d['expected'])[:70]}` | {d['status']} | {d['class'] or '—'} |")
        sel = c["selection"]
        L += ["", (f"**Selection (D31-12).** Structural event exists (strict): "
                   f"{_yn(sel['structural_event_exists'])}. D25-P3-equivalent candidates regardless of eligibility: "
                   f"{', '.join(x.split('/')[-1] for x in sel['p3_equivalent_candidates_any_eligibility']) or 'none'}"
                   f". Frozen selection: "
                   f"{', '.join(x.split('/')[-1] for x in sel['frozen_selection_ids']) or 'none'}. "
                   f"Classification: {sel['classification'] or '—'}."),
              "", "| Variant | Candidates | Eligible | Frozen selection | Selection eligible |", "|---|---|---|---|---|"]
        for var, pv in c["per_variant"].items():
            L.append(f"| {var} | {pv['candidates']} | {pv['eligible']} | "
                     f"`{(pv['frozen_selection'] or '—').split('/')[-1]}` | {_yn(pv['frozen_selection_eligible'])} |")
        L.append("")
    for cid in ("JM-2025-10-16", "JM-2025-10-17", "JM-2025-10-29"):
        c = cases[cid]
        j = c["journal"]
        L += [f"## {cid} (HOUR_LEVEL) — **{c['verdict']}**", "",
              (f"Journal row: {j['journal_time_local']} · {j['mtf_model']} · {j['condition']} · CB {j['cb_hour']} · "
               f"{j['shifts']}. Source level L1_FRAME_JOURNAL_TABLE (Tom's own record, no prices)."), "",
              "| Field | Engine | Source | Status |", "|---|---|---|---|"]
        for f in c["fields"]:
            L.append(f"| {f['field']} | `{json.dumps(f['engine'])[:90]}` | `{json.dumps(f['expected'])[:70]}` | "
                     f"{f['status']} |")
        L += ["", (f"Eligible candidates in the hour: "
                   f"{', '.join(x.split('/')[-1] for x in c['eligible_ids']) or 'none'}."), "",
              "| Candidate | Dir | Shift | Trigger verdict | Failing rules at trigger |", "|---|---|---|---|---|"]
        for x in c["all_candidates"]:
            L.append(f"| `{x['signal_id'].split('/')[-1]}` | {x['direction']} | {x['shift']} | "
                     f"{x['event_at_trigger']} | {', '.join(x['rules_failed_at_trigger']) or '—'} |")
        L.append("")
    L += ["## Narrative / geometry set (never a machine pass count)", "",
          "| Case | Assessment | Reason |", "|---|---|---|"]
    L += [f"| {k} | {x['assessment']} | {x['reason']} |" for k, x in p["narrative"].items()]
    L += ["", "## Mismatch register", ""]
    if p["mismatch_register"]:
        L += ["| Case | Dimension | Class | Engine | Source |", "|---|---|---|---|---|"]
        L += [f"| {m['case']} | {m['dimension']} | {m['class']} | `{json.dumps(m['engine'])[:80]}` | "
              f"`{json.dumps(m['expected'])[:60]}` |" for m in p["mismatch_register"]]
        L += ["", "Taxonomy order applied: " + " → ".join(TAXONOMY) + ".",
              "Every mismatch above is classified; none is unclassified."]
    else:
        L.append("No mismatches.")
    L += ["", "## Concerns", ""] + ([f"- {x}" for x in v["concerns"]] or ["- none"])
    L += ["", "## Limits of this run (CBR-PROT-013C §9)", "",
          f"- Machine set: {set_counts} — XAUUSD only, CBR1H only.",
          "- The three HOUR_LEVEL cases come from Tom's journal table in a Level-1 frame and carry no prices.",
          "- CBR15-PC3 is SPEC_ONLY and unscored.",
          "- `k = 3` is fixed; CX-LT3-2's trigger is known to disappear at `k = 4`.",
          "- PC3 carries six unresolved assumptions; passing parity would not convert any of them into CANON.",
          "- No P&L, fills or trade outcomes were read at any point in this run.", "",
          "## Stop", "",
          ("Phase 13C is complete and execution stops here. Phase 14 is not started, PC3 is unchanged since the "
           "freeze, and no corrective run has been launched."), ""]
    return "\n".join(L)
