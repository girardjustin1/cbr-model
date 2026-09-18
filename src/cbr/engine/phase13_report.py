"""Phase 13 reports (CBR-PROT-013B §8, D25-R). Presentation only: reads the two complete-run files written by
`phase13_behavioral run`, checks their result hashes, applies the frozen verdict function and renders Markdown / JSON.
No measurement, selection or classification happens here."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from cbr.engine import phase13_behavioral as pb

OUT = {"feed": "phase13-feed-comparison", "htf": "phase13-higher-timeframe-fidelity", "parity": "phase13-behavioral-parity",
       "manifest": "phase13-run-manifest"}


def _fmt(v, nd=4):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    if isinstance(v, list):
        return ", ".join(_fmt(x, nd) for x in v)
    return str(v)


def _rate(r: dict) -> str:
    if not r or r.get("n") in (None, 0):
        return "— (n = 0)"
    lo, hi = r["wilson95"]
    return f"{r['rate'] * 100:.1f}% ({r['agree']}/{r['n']}; 95% CI {lo * 100:.1f}-{hi * 100:.1f}%)"


def load_runs() -> tuple[dict, dict]:
    runs = []
    for n in (1, 2):
        path = pb.RUN_DIR / f"run-{n}.json"
        if not path.exists():
            raise SystemExit(f"{path.relative_to(pb.ROOT)} missing: run `phase13_behavioral run {n}` first")
        runs.append(json.loads(path.read_text()))
    return runs[0], runs[1]


def write_reports() -> dict:
    freeze = pb.verify_freeze()
    spec = pb.load_spec()
    r1, r2 = load_runs()
    v = pb.verdict(r1, r2, spec)
    pl = r1["payload"]
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    head = {"run_id": spec["run_id"], "generated_utc": now, "ruling": "D25", "freeze_commit": freeze["git_commit"]}
    feed = {**head, **pl["recent_feed_comparison"]}
    htf = {**head, "examples": pl["higher_timeframe"]}
    parity_json = {**head, "verdict": v, "examples": pl["examples"], "negative_control": pl["negative_control"],
                   "engine_run_determinism": pl["engine_run_determinism"]}
    manifest = {**head, "protocol_sha256": freeze["files"]["docs/governance/phase13-behavioral-parity-protocol.md"],
                "run_spec_sha256": freeze["files"]["config/phase13_behavioral_run.yaml"],
                "ruling_sha256": freeze["files"]["docs/governance/d25-phase13-run-approval.md"],
                "frozen_files": freeze["files"], "pc2": freeze["pc2"], "forexcom_exports": freeze["forexcom_exports"],
                "pre_execution_tests": freeze["pre_execution_tests"], "lint": freeze.get("lint"), "frozen_utc": freeze["frozen_utc"],
                "data_hashes": pl["data_hashes"], "result_hashes": {"run-1": r1["result_hash"], "run-2": r2["result_hash"]},
                "run_generated_utc": {"run-1": r1["generated_utc"], "run-2": r2["generated_utc"]},
                "deterministic_rerun": r1["result_hash"] == r2["result_hash"], "verdict": v["verdict"]}
    for key, obj in (("feed", feed), ("htf", htf), ("parity", parity_json), ("manifest", manifest)):
        (pb.REPORTS / f"{OUT[key]}.json").write_text(json.dumps(obj, indent=1, sort_keys=False, default=str) + "\n")
    (pb.REPORTS / f"{OUT['feed']}.md").write_text(render_feed(feed, spec))
    (pb.REPORTS / f"{OUT['htf']}.md").write_text(render_htf(htf))
    (pb.REPORTS / f"{OUT['parity']}.md").write_text(render_parity(parity_json, manifest, feed, spec))
    return {"verdict": v["verdict"], "deterministic_rerun": manifest["deterministic_rerun"],
            "result_hashes": manifest["result_hashes"]}


# ------------------------------------------------------------------ feed comparison

def render_feed(f: dict, spec: dict) -> str:
    a, o, b = f["alignment"], f["offsets"], f["feed_band"]
    L = ["# Phase 13: Recent FOREXCOM vs Dukascopy Feed Comparison", "",
         f"Run `{f['run_id']}` · generated {f['generated_utc']} · freeze commit `{f['freeze_commit'][:10]}` · owner ruling D25.",
         "Supporting evidence (CBR-PROT-013B §7.1). Days: " + ", ".join(spec["recent_feed_comparison"]["days"])
         + f" (from {spec['recent_feed_comparison']['start_utc']}). Nothing here changed a parameter.", "",
         "## Data validation (Dukascopy ticks for the D25-P2 days)", "",
         "| Day | Ready | Tick rows | Vendor-gap minutes | STRUCTURE 1m rebuild = stored | Problems |", "|---|---|---|---|---|---|"]
    for d, x in f["data_validation"].items():
        L.append(f"| {d} | {x['ready']} | {x.get('ticks', {}).get('rows', '—')} | {x.get('vendor_gap_minutes')} | "
                 f"{x.get('structure_1m', {}).get('deterministic_rebuild')} | {'; '.join(x['problems']) or 'none'} |")
    L += ["", "## Timestamp alignment and offsets", "", "| Measure | Value |", "|---|---|",
          f"| Comparison minutes (scheduled open) | {a['comparison_minutes']} |",
          f"| Matched minutes | {a['matched_minutes']} (missing FOREXCOM {a['missing_forexcom']}, missing Dukascopy {a['missing_dukascopy']}) |",
          f"| Best lag of 1m close returns (minutes) | {a['best_lag_minutes']} (zero lag confirmed: {a['zero_lag_confirmed']}) |",
          "| Lag correlations | " + ", ".join(f"{k}: {v:.4f}" for k, v in a["lag_correlations"].items()) + " |",
          f"| Median close offset δ (FOREXCOM − Dukascopy) | {o['delta_median_close_offset']:.4f} |",
          "| Per-field median offsets | " + ", ".join(f"{k} {v:.4f}" for k, v in o["per_field_median_offset"].items()) + " |",
          "| Per-day median close offsets | " + ", ".join(f"{k} {v:.4f}" for k, v in o["per_day_median_close_offset"].items()) + " |",
          "| HLC residual after δ: p50 / p75 / p90 / p95 / p99 | " + " / ".join(f"{v:.4f}" for v in o["residual_quantiles_hlc_after_delta"].values()) + " |",
          f"| Max HLC residual after δ | {o['residual_max_hlc_after_delta']:.4f} |",
          "", "## Feed band (D25-P4)", "",
          (f"τ = max($0.02, p95 {b['p95_residual']:.4f}) rounded up to $0.05 = **${b['tau_usd']:.2f}** · p99 residual "
          f"{b['p99_residual']:.4f}. Descriptive; used only in the materiality test."), "",
          "## Agreement", "", "| Concept | Agreement |", "|---|---|"]
    rows = [("Bar direction 1m", f["bar_direction"]["1m"]), ("Bar direction 5m", f["bar_direction"]["5m"]),
            ("Bar direction 15m", f["bar_direction"]["15m"]), ("**LTF 1m swing membership**", f["swings"]["ltf_1m"]),
            ("**MTF 5m swing membership**", f["swings"]["mtf_5m"]), ("**15m previous-candle takes (pooled)**", f["takes_15m"].get("pooled")),
            ("15m take of previous high", f["takes_15m"].get("high")), ("15m take of previous low", f["takes_15m"].get("low")),
            ("**Hourly extension direction**", f["hour_extension"].get("direction")),
            ("Extension extreme time ±1 min (same direction)", f["hour_extension"].get("extreme_time_within_1m_given_same_direction")),
            ("Extension duration ≥ 20 min flag", f["hour_extension"].get("duration_ge_min")),
            ("Extension no-pullback flag", f["hour_extension"].get("no_pullback")),
            ("Extension two-sided flag", f["hour_extension"].get("two_sided")),
            ("**Condition class at the hour open**", f["condition_at_hour_open"].get("condition")),
            ("Condition direction at the hour open", f["condition_at_hour_open"].get("cond_direction")),
            ("**1m type 3 events**", f["type3_1m"]), ("1m HILO events", f["hilo_1m"]),
            ("**Hour-level CBR1H setup membership (min 25/35/45)**", f["hour_level_state"]["membership"]),
            ("Full hour-level rule vector (same direction)", f["hour_level_state"]["full_rule_vector_given_same_direction"])]
    L += [f"| {name} | {_rate(r)} |" for name, r in rows]
    L += ["", "Bold = criterion 9 core concept (D25 O-1). 5s structure: DATA_LIMITATION (no FOREXCOM 5s).", "",
          "### Per-rule agreement (hour-level state, same extension direction)", "", "| Rule | Agreement |", "|---|---|"]
    L += [f"| {k} | {_rate(r)} |" for k, r in f["hour_level_state"]["per_rule_given_same_direction"].items()]
    sw = f["swings"]
    L += ["", "### Swing and event details", "", "| Tier | Matched | FOREXCOM only | Dukascopy only | Median Δt (s) | Exact time share | Matched price |Δ − δ| median / p95 |",
          "|---|---|---|---|---|---|---|"]
    for tier in ("ltf_1m", "mtf_5m"):
        s = sw[tier]
        px = s.get("matched_price_difference_after_delta", {})
        L.append(f"| {tier} | {s['matched']} | {s['forexcom_only']} | {s['dukascopy_only']} | "
                 f"{_fmt(s['matched_time_difference_s']['median'], 1)} | {_fmt(s['matched_time_difference_s']['exact_share'], 3)} | "
                 f"{_fmt(px.get('median_abs'))} / {_fmt(px.get('p95_abs'))} |")
    for name in ("type3_1m", "hilo_1m"):
        s = f[name]
        L.append(f"| {name} | {s['matched']} | {s['forexcom_only']} | {s['dukascopy_only']} | "
                 f"{_fmt(s['matched_time_difference_s']['median'], 1)} | {_fmt(s['matched_time_difference_s']['exact_share'], 3)} | — |")
    t = f["takes_15m"]
    L += ["", (f"15m takes: {t.get('disagreements')} disagreements, {t.get('disagreements_with_abs_dukascopy_margin_le_tau')} "
          f"with |Dukascopy margin| ≤ τ. Hourly evaluations: {f['hour_extension'].get('evaluations')} over "
          f"{f['hour_extension'].get('hours')} hours; hours excluded: {f['hours_excluded']}. Hour-level members: FOREXCOM "
          f"{f['hour_level_state']['members_forexcom']}, Dukascopy {f['hour_level_state']['members_dukascopy']}."),
          f"Exports vs 1m roll-ups: {f['export_vs_1m_rollup']}.", "",
          "## Criterion 9 (D25 O-1 reading, frozen before the study)", ""]
    c9 = f["criterion_9"]
    L += [(f"**{c9['status']}** · FAIL evidence if any core rate < {c9['fail_evidence_if_rate_below']:.2f}; concern if < "
          f"{c9['concern_if_rate_below']:.2f}."), "", "| Core concept | Agreement |", "|---|---|"]
    L += [f"| {k} | {_rate(r)} |" for k, r in c9["concepts"].items()]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ higher timeframe

def render_htf(h: dict) -> str:
    L = ["# Phase 13: Higher-Timeframe Fidelity (FOREXCOM 1h / 4h / 1D vs Dukascopy)", "",
         (f"Run `{h['run_id']}` · generated {h['generated_utc']} · owner ruling D25. Supporting evidence (CBR-PROT-013B §7.2). "
         "Offsets are FOREXCOM − Dukascopy STRUCTURE tick-mid roll-ups; bars without full Dukascopy coverage are DATA_LIMITATION."), ""]
    for ex_id, ex in h["examples"].items():
        L += [f"## {ex_id} (hour {ex['hour_utc']})", "", f"Hour offset δ_h (mean of open and close offsets): **{_fmt(ex['delta_h'])}**", "",
              "### 1h bars (H ± 3 h)", "", "| Bar | Open Δ | High Δ | Low Δ | Close Δ | Direction agree | Side extended FX / DK | DK high / low time |",
              "|---|---|---|---|---|---|---|---|"]
        for r in ex["1h"]:
            if "offsets" not in r:
                L.append(f"| {r['bar']} | {r.get('class')} (coverage {_fmt(r.get('coverage'), 3)}) | | | | | | |")
                continue
            o = r["offsets"]
            L.append(f"| {r['bar']} | {o['open']:+.3f} | {o['high']:+.3f} | {o['low']:+.3f} | {o['close']:+.3f} | {r['direction_agree']} | "
                     f"{r['side_extended_fx']} / {r['side_extended_dk']} | {r['dk_high_time'][11:16]} / {r['dk_low_time'][11:16]} |")
        for tf in ("4h", "1D"):
            L += ["", f"### {tf} bars", "", "| Bar | End | Contains H | Open Δ | High Δ | Low Δ | Close Δ | Direction agree | Side extended agree | Extreme hours agree |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for r in ex[tf]:
                if "offsets" not in r:
                    L.append(f"| {r['bar']} | {r['end']} | {r['contains_course_hour']} | {r.get('class')} (coverage {_fmt(r.get('coverage'), 3)}) | | | | | | |")
                    continue
                o = r["offsets"]
                L.append(f"| {r['bar']} | {r['end']} | {r['contains_course_hour']} | {o['open']:+.3f} | {o['high']:+.3f} | {o['low']:+.3f} | "
                         f"{o['close']:+.3f} | {r['direction_agree']} | {r['side_extended_agree']} | {r.get('extreme_hours_agree', '—')} |")
        L += ["", "### TVC:DXY 1h vs Dukascopy DXY CFD (open/close; descriptive)", "",
              "| Bar | TVC dir | CFD dir | Agree | Open Δ | Close Δ |", "|---|---|---|---|---|---|"]
        for r in ex["dxy_1h"]:
            L.append(f"| {r['bar']} | {r.get('tvc_direction', '—')} | {r.get('cfd_direction', r.get('class', '—'))} | "
                     f"{r.get('direction_agree', '—')} | {_fmt(r.get('open_offset'))} | {_fmt(r.get('close_offset'))} |")
        L.append("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ behavioral parity (main report)

def _dim_rows(dims: list[dict]) -> list[str]:
    L = ["| # | Dimension | Engine | Course | Status | Class | Evidence / notes |", "|---|---|---|---|---|---|---|"]
    for d in dims:
        k = d.get("classification") or {}
        note = []
        if k:
            note.append("; ".join(f"{a}: {b}" for a, b in k.get("evidence", {}).items()))
            if k.get("secondary"):
                note.append(f"secondary {k['secondary']}")
            if k.get("tags"):
                note.append(f"tags {k['tags']}")
        for extra in ("margin_usd", "tom_minus_engine", "adjusted_minus_engine"):
            if d.get(extra) is not None:
                note.append(f"{extra} {d[extra]:+.3f}")
        if d.get("p3"):
            note.append(f"P-3 {d['p3']}")
        eng = json.dumps(d["engine"], default=str) if isinstance(d["engine"], (dict, list)) else _fmt(d["engine"])
        crs = json.dumps(d["course"], default=str) if isinstance(d["course"], (dict, list)) else _fmt(d["course"])
        L.append(f"| {d['dim']} | {d['name']}{' (descriptive)' if d.get('descriptive') else ''} | {eng.replace('|', '/')} | "
                 f"{crs.replace('|', '/')} | {d['status']} | **{d['class']}** | {' · '.join(n for n in note if n).replace('|', '/')} |")
    return L


def render_parity(p: dict, m: dict, feed: dict, spec: dict) -> str:
    v = p["verdict"]
    L = ["# Phase 13: Strategy Fidelity and Behavioral Parity Report", "",
         (f"Run `{p['run_id']}` · generated {p['generated_utc']} · protocol CBR-PROT-013B (approved D25) · spec under test "
         "CBR1H_BASELINE_V1-PC2 · signal state only: no fills, outcomes, P&L or optimization."), "",
         f"## Verdict: **{v['verdict']}**", ""]
    if v["fail_reasons"]:
        L += ["FAIL conditions:", *[f"- {r}" for r in v["fail_reasons"]], ""]
    if v["owner_determination"]:
        L += ["Owner determination required:", *[f"- {r}" for r in v["owner_determination"]], ""]
    L += ["| D25-P5 criterion | Result |", "|---|---|", *[f"| {k} | {val} |" for k, val in v["criteria"].items()], ""]
    if v["concerns"]:
        L += ["Concerns (each classified below):", *[f"- {c}" for c in v["concerns"]], ""]
    L += [("Criterion 7 and 8 are structural: every CANON_MISMATCH carries cited evidence and every non-match has one primary "
          "class. D25 O-1…O-8 (criterion 9 reading, control window, variants, trigger, approved explanations, concerns, "
          "negative-control classification, DXY) are Research Engineer operationalizations frozen before the run."), "",
          "## 1-3. Frozen inputs and hashes", "", "| Item | SHA-256 |", "|---|---|",
          f"| Protocol CBR-PROT-013B | `{m['protocol_sha256']}` |", f"| Run specification {p['run_id']} | `{m['run_spec_sha256']}` |",
          f"| Ruling D25 | `{m['ruling_sha256']}` |", f"| PC2 spec hash (CBR1H) | `{m['pc2']['spec_hash']}` |",
          f"| Freeze commit | `{m['freeze_commit']}` (frozen {m['frozen_utc']}) |", "",
          (f"Pre-execution tests at the freeze: {m['pre_execution_tests']}; lint at the freeze: {m.get('lint')}. All frozen files: "
          "`reports/phase13-run-manifest.json`. Superseded run CBR-RUN-013B-1 stopped before any result "
          "(`docs/governance/phase13-run-incident-1.md`). Research Engineer post-run review: `reports/phase13-post-run-review.md`."), "",
          "| Data | Files | Hash check |", "|---|---|---|"]
    dh = m["data_hashes"]
    L += [(f"| Course STRUCTURE bars | {len(dh['course_structure_bars'])} | all match canonical manifest: "
          f"{all(x['manifest_match'] for x in dh['course_structure_bars'].values())} |"),
          (f"| Recent ticks / STRUCTURE bars | {len(dh['recent_ticks'])} / {len(dh['recent_structure_bars'])} | "
          f"all present: {all(dh['recent_ticks'].values()) and all(dh['recent_structure_bars'].values())} |"),
          f"| DXY CFD candles | {len(dh['dxy_candles'])} | all present: {all(dh['dxy_candles'].values())} |",
          f"| FOREXCOM / TVC exports | {len(m['forexcom_exports'])} | unchanged since the freeze |", ""]
    c9 = feed["criterion_9"]
    L += ["## 4. Recent feed comparison (summary; full: `reports/phase13-feed-comparison.md`)", "",
          (f"Zero lag: {feed['alignment']['zero_lag_confirmed']} · δ = {feed['offsets']['delta_median_close_offset']:.4f} · p95 residual "
          f"{feed['feed_band']['p95_residual']:.4f} · **τ = ${feed['feed_band']['tau_usd']:.2f}** · criterion 9: **{c9['status']}**"), "",
          "| Core concept | Agreement |", "|---|---|", *[f"| {k} | {_rate(r)} |" for k, r in c9["concepts"].items()], "",
          "## 5. Higher-timeframe fidelity: see `reports/phase13-higher-timeframe-fidelity.md`", ""]
    L += ["## 6. Behavioral parity per positive example", ""]
    L += ["| Example | Scored variant | Model family | Direction | Extension direction | Core trigger | Example verdict |", "|---|---|---|---|---|---|---|"]
    for ex_id, ex in p["examples"].items():
        h = ex["hard_met"]
        cell = lambda k, h=h: ("✓ " if h[k]["met"] else "✗ ") + h[k]["class"]
        L.append(f"| {ex_id} | {ex['scored_variant']} | {cell('model_family')} | {cell('direction')} | "
                 f"{cell('extension_direction')} | {cell('core_structural_trigger')} | **{ex['example_verdict']}** |")
    L.append("")
    for ex_id, ex in p["examples"].items():
        L += [f"### {ex_id} · hour {ex['hour_utc']} · {ex['direction']}", ""]
        for variant, vv in ex["variants"].items():
            e = vv["engine"] or {}
            L += [(f"#### Variant {variant} · BASELINE_SPEC · {vv['how_selected']} · candidates in hour {vv['candidates_in_hour']} "
                  f"(ARMED {vv['armed_in_hour']})"), ""]
            if e:
                L.append(f"Candidate `{e.get('signal_id')}` · event **{e.get('event')}** · decision {e.get('timestamp')} · shift "
                         f"{e.get('five_second_shift_time')} at {_fmt(e.get('five_second_shift_level'))} · cancel {e.get('cancel_reason')} · "
                         f"example verdict **{vv['example_verdict']}**")
                L.append("")
            L += _dim_rows(vv["dimensions"])
            fr = vv["acceptance"]["failed_rules"]
            if fr:
                L += ["", "| Failed rule | Primary class | Secondary | Tags | Dukascopy margin | Evidence |", "|---|---|---|---|---|---|"]
                for a in fr:
                    k = a["classification"]
                    L.append(f"| {a['rule']} | **{k['primary']}** | {k['secondary']} | {k['tags']} | {_fmt(k.get('margin_usd'))} | "
                             + "; ".join(f"{x}: {y}" for x, y in k["evidence"].items()).replace("|", "/") + " |")
            L += ["", "STRICT_COURSE (one pre-registered alternative per run; never merged with the baseline):", "",
                  "| View | Selected | Event | Shift | Model | Direction | Extension | Core trigger |", "|---|---|---|---|---|---|---|---|"]
            for lab, st in vv["strict_course"].items():
                se = st["engine"] or {}
                hh = st["hard"]
                L.append(f"| {lab} | {st['how']} | {se.get('event')} | {se.get('five_second_shift_time')} | "
                         + " | ".join(("✓" if hh[k]["met"] else "✗ " + hh[k]["class"]) for k in pb.HARD) + " |")
            c = vv["causality"]
            L += ["", f"Causality spot checks (truncation + future mutation at mid-minute cuts): {c.get('all_identical')} · {json.dumps({k: c[k] for k in c if k not in ('checked', 'all_identical')}, default=str)}", ""]
    n = p["negative_control"]
    L += ["## 7. Negative control CX-LT3-1", "",
          f"Window {n['window_utc'][0]} → {n['window_utc'][1]} (D25 O-2) · expected {n['expected']} · result **{n['result']}**", ""]
    if n["all_candidates_with_shift_in_window"]:
        L += ["| Variant | Candidate | Event | Shift | Level | Failed rules |", "|---|---|---|---|---|---|"]
        L += [f"| {c['variant']} | {c['signal_id']} | {c['event']} | {c['shift_time']} | {_fmt(c['shift_level'])} | {', '.join(c['rules_failed'])} |"
              for c in n["all_candidates_with_shift_in_window"]]
        L.append("")
    for s in n["eligible_signals"]:
        k = s["classification"]
        L += [(f"- Eligible signal `{s['signal_id']}`: **{k['primary']}** (secondary {k['secondary']}, tags {k['tags']}); "
              f"absent under {[g['view'] for g in s['absent_under']]}; Tom's reasons not in PC2: {s['rule_differences']}")]
    L += ["", "## 8. Mismatch register (scored variants, BASELINE_SPEC)", "", "| Example | Item | Primary class | Secondary | Tags |", "|---|---|---|---|---|"]
    for ex_id, ex in p["examples"].items():
        vv = ex["variants"][ex["scored_variant"]]
        for d in vv["dimensions"]:
            if d["class"] not in (pb.BM, pb.NA):
                k = d.get("classification") or {}
                L.append(f"| {ex_id} | dim {d['dim']} {d['name']}{' (descriptive)' if d.get('descriptive') else ''} | {d['class']} | "
                         f"{k.get('secondary', '')} | {k.get('tags', '')} |")
        for a in vv["acceptance"]["failed_rules"]:
            k = a["classification"]
            L.append(f"| {ex_id} | rule {a['rule']} | {k['primary']} | {k['secondary']} | {k['tags']} |")
    det = p["engine_run_determinism"]
    L += ["", "## 9. Deterministic rerun", "",
          (f"Complete-run result hashes: run 1 `{m['result_hashes']['run-1']}`, run 2 `{m['result_hashes']['run-2']}` → identical: "
          f"**{m['deterministic_rerun']}**. Engine runs repeated within each complete run: {len(det)}, all identical: "
          f"{all(x['identical'] for x in det.values())}."), "",
          "## 10. Causality status", "",
          (f"Pre-execution suite (truncation / future-mutation / guard / determinism tests included): {m['pre_execution_tests']}. "
          "Per-example spot checks above. PC2 hash unchanged before and after the run (verified by the report step)."), "",
          "## 11. Unresolved concerns", ""]
    L += [f"- {c}" for c in v["concerns"]] or ["- none"]
    L += ["", "## 12. Verdict", "", f"**{v['verdict']}** (pending owner review; Phase 14 not started).", ""]
    return "\n".join(L) + "\n"
