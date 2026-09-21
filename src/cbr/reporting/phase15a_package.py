"""Phase 15A review-package writer (owner ruling D42 §7-9, §13-14).

Writes the eight artefacts the Astra review package requires, plus the run manifest that carries complete
provenance. Astra's task is to **audit**, so every file is built to be recomputed from: each R value is present per
trade, every statistic carries its denominator, and each row traces back to its `signal_id` and source hashes.

    reports/phase15a/
      phase15a_report.md      run_manifest.json     signals.csv        trades.csv
      monthly_metrics.csv     equity_curve.csv      drawdowns.csv      execution_quality.csv

**No result may be presented without complete provenance** (D42 §13): the writer refuses to emit a package whose
manifest is missing any required hash. In fixture mode the artefacts are written to a caller-supplied directory and
the report states plainly that it holds no real CBR outcome.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from cbr.data import dukascopy_fetch as dk
from cbr.engine import baseline_v1
from cbr.engine import phase15a_protocol as protocol
from cbr.reporting import phase15a_metrics as pm

PACKAGE_VERSION = "15A.1"
OUT = dk.ROOT / "reports" / "phase15a"

FILES = ("phase15a_report.md", "run_manifest.json", "signals.csv", "trades.csv", "monthly_metrics.csv",
         "equity_curve.csv", "drawdowns.csv", "execution_quality.csv")

# D42 §13: a manifest missing any of these is not a publishable result.
REQUIRED_PROVENANCE = (
    "pc4_spec_hash", "protocol_hash", "execution_config_hash", "simulator_version", "runner_version",
    "runner_hash", "orchestrator_version", "orchestrator_hash", "metrics_version", "metrics_hash",
    "completeness_manifest_hash", "source_hashes", "signal_ledger_hash", "execution_ledger_hash",
    "result_hash", "git_commit",
)

SIGNAL_COLUMNS = (
    "signal_id", "timestamp", "model", "variant", "direction", "condition", "extension_activation",
    "extension_direction", "extension_extreme", "hvcs_state", "trigger_time", "trigger_price", "stop_anchor",
    "target_price", "execution_status", "rejection_or_reason_code", "data_confidence", "source_hashes")

TRADE_COLUMNS = (
    "signal_id", "direction", "variant", "activation_time", "trigger_price", "fill_time", "fill_price",
    "fill_spread", "entry_gap", "stop_anchor", "final_stop", "target", "initial_risk", "exit_time", "exit_price",
    "exit_reason", "stop_gap", "planned_rr", "gross_r", "net_r", "administrative_exit", "data_confidence")


class IncompleteProvenance(RuntimeError):
    """The package was refused because its manifest could not fully account for the result."""


@dataclass
class Package:
    directory: Path
    manifest: dict
    files: dict


def _git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=dk.ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None


def _sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def signals_frame(signal_ledger, execution_ledger) -> pd.DataFrame:
    """D42 §8. One row per frozen PC4 signal, joined to what execution did with it."""
    ex = {r.signal_id: r for r in execution_ledger.records}
    rows = []
    for s in signal_ledger.signals:
        r = ex.get(s["signal_id"])
        ctx = s.get("context_state", {})
        ext = s.get("extension", {})
        stop = s.get("stop_rule", {})
        rows.append({
            "signal_id": s["signal_id"],
            "timestamp": s.get("timestamp"),
            "model": s.get("model"),
            "variant": s.get("variant"),
            "direction": s.get("direction"),
            "condition": ctx.get("condition"),
            "extension_activation": ext.get("activation_time"),
            "extension_direction": ext.get("state"),
            "extension_extreme": stop.get("extension_extreme"),
            "hvcs_state": ctx.get("hvcs_minutes"),
            "trigger_time": s.get("entry_trigger_time"),
            "trigger_price": s.get("entry_reference_price"),
            "stop_anchor": stop.get("structure_stop_anchor"),
            "target_price": s.get("target_price"),
            "execution_status": None if r is None else r.execution_status,
            "rejection_or_reason_code": None if r is None else (r.reason_code or r.exit_reason),
            "data_confidence": json.dumps(s.get("data_confidence", {}), sort_keys=True),
            "source_hashes": json.dumps({} if r is None else r.source_hashes, sort_keys=True),
        })
    return pd.DataFrame(rows, columns=list(SIGNAL_COLUMNS))


def trades_frame(execution_ledger) -> pd.DataFrame:
    """D42 §9. Every row Astra needs to reconstruct a reported trade, including administrative exits."""
    frame = execution_ledger.frame()
    if not len(frame):
        return pd.DataFrame(columns=list(TRADE_COLUMNS))
    f = frame[frame["fill_time"].notna()].copy()
    if not len(f):
        return pd.DataFrame(columns=list(TRADE_COLUMNS))
    f["planned_rr"] = pm._planned_rr(f)
    f["administrative_exit"] = f["exit_reason"].isin(["ROLLOVER_EXIT", "DATASET_END_EXIT"])
    out = pd.DataFrame({
        "signal_id": f["signal_id"], "direction": f["direction"], "variant": f["variant"],
        "activation_time": f["activation_time"], "trigger_price": f["trigger_price"],
        "fill_time": f["fill_time"], "fill_price": f["fill_price"], "fill_spread": f["fill_spread"],
        "entry_gap": f["entry_gap"], "stop_anchor": f["fill_time_stop_anchor"],
        "final_stop": f["final_execution_stop"], "target": f["target_price"], "initial_risk": f["initial_risk"],
        "exit_time": f["exit_time"], "exit_price": f["exit_price"], "exit_reason": f["exit_reason"],
        "stop_gap": f["stop_gap"], "planned_rr": f["planned_rr"], "gross_r": f["gross_r"], "net_r": f["net_r"],
        "administrative_exit": f["administrative_exit"],
        "data_confidence": f["data_confidence"].map(lambda d: json.dumps(d, sort_keys=True, default=str)),
    })
    return out[list(TRADE_COLUMNS)].sort_values("fill_time").reset_index(drop=True)


def _monthly(metrics: pm.Metrics) -> pd.DataFrame:
    month = metrics.breakdowns.get("month", {})
    if not month:
        return pd.DataFrame(columns=["month", "trade_count", "wins", "losses", "win_rate", "net_r",
                                     "net_expectancy_r", "profit_factor", "max_drawdown_r"])
    rows = [{"month": k, **{c: v.get(c) for c in ("trade_count", "wins", "losses", "win_rate", "net_r",
                                                  "net_expectancy_r", "profit_factor", "max_drawdown_r")}}
            for k, v in sorted(month.items())]
    return pd.DataFrame(rows)


def _equity(metrics: pm.Metrics) -> pd.DataFrame:
    curve = metrics.values.get("equity_curve") or []
    return pd.DataFrame(curve, columns=["exit_time", "cumulative_net_r"])


def _execution_quality(metrics: pm.Metrics) -> pd.DataFrame:
    rows = []
    for key, val in metrics.execution_quality.items():
        if isinstance(val, dict):
            for stat, v in val.items():
                rows.append({"measure": key, "statistic": stat, "value": v})
        else:
            rows.append({"measure": key, "statistic": "value", "value": val})
    return pd.DataFrame(rows, columns=["measure", "statistic", "value"])


def _report_md(manifest: dict, metrics: pm.Metrics, fixture: bool) -> str:
    m = metrics.values
    v = manifest.get("verdict", "NOT_ASSESSED")
    head = "# Phase 15A — 2022 development pilot\n\n"
    if fixture:
        head += ("> **FIXTURE RUN — NOT A RESULT.** This package was produced from synthetic data during "
                 "construction. It contains no real CBR outcome and must not be read as performance.\n\n")
    lines = [
        head,
        (f"**Doc:** CBR-RPT-015A · **Ruling:** D42 · **Span:** {manifest.get('span')} · "
         "**Status:** DEVELOPMENT PILOT — not a full development baseline, not validation, not holdout, "
         "and never a validated edge.\n"),
        "## Verdict\n", f"### {v}\n",
        "## Primary metric\n",
        (f"**Net expectancy in R per executed canonical trade: {m.get('net_expectancy_r')}** over "
         f"{m.get('trade_count')} canonical completed trades. "
         "Win rate is secondary and was not optimized for.\n"),
        "## Signal funnel\n",
        "| Stage | Count |\n|---|---|",
    ]
    for k, val in metrics.funnel.items():
        if isinstance(val, (int, float)):
            lines.append(f"| {k} | {val} |")
    lines += ["\n## Trade metrics (canonical completed trades only)\n", "| Metric | Value |\n|---|---|"]
    for k in ("trade_count", "wins", "losses", "win_rate", "planned_rr_mean", "planned_rr_median", "gross_r",
              "net_r", "average_winner", "average_loser", "median_r", "net_expectancy_r", "profit_factor",
              "max_drawdown_r", "longest_losing_streak", "total_net_r"):
        lines.append(f"| {k} | {m.get(k)} |")
    lines += [
        (f"\nDenominator for every row above: **{m.get('denominator')}** canonical completed trades "
         "(`TARGET` or `STOP` only). Administrative exits and unprovable outcomes are excluded and reported "
         "separately in `execution_quality.csv`.\n"),
        "## Descriptive breakdowns\n",
        ("`monthly_metrics.csv` holds the month breakdown; direction, variant and session buckets are in "
         "`run_manifest.json`. **These are descriptive only** — no rule, parameter or filter may be selected "
         "from them.\n"),
        "## Provenance\n", "| Field | Value |\n|---|---|",
    ]
    for k in REQUIRED_PROVENANCE:
        val = manifest.get(k)
        if isinstance(val, dict):
            val = f"{len(val)} entries"
        lines.append(f"| {k} | `{val}` |")
    lines += [
        ("\nThe baseline provenance below is carried unchanged from D37 and continues to state the parity "
         "verdict **FAIL** with its five documented fidelity concerns.\n"),
        "```json", json.dumps(manifest.get("baseline_provenance", {}), indent=1), "```\n",
        "## For the auditor\n",
        ("Every R value appears per trade in `trades.csv`; expectancy is the mean of `net_r` over rows where "
         "`administrative_exit` is false and `exit_reason` is `TARGET` or `STOP`. Win rate is the share of those "
         "rows with `net_r > 0`. Each row carries its `signal_id`, and `signals.csv` carries the source hashes "
         "for the data the signal was derived from.\n"),
    ]
    return "\n".join(lines) + "\n"


def write(signal_ledger, execution_ledger, metrics: pm.Metrics, *, directory: Path | None = None,
          fixture: bool = False, gate: dict | None = None, verdict: str = "NOT_ASSESSED",
          require_provenance: bool = True) -> Package:
    """Write the eight artefacts and the manifest. Refuses to write an under-provenanced result."""
    out = Path(directory) if directory else OUT
    out.mkdir(parents=True, exist_ok=True)

    sp = signal_ledger.provenance
    xp = execution_ledger.provenance
    manifest = {
        "package_version": PACKAGE_VERSION,
        "ruling": "D42",
        "status": "FIXTURE_NON_PERFORMANCE" if fixture else "DEVELOPMENT_PILOT",
        "span": list(signal_ledger.span),
        "variants": signal_ledger.variants,
        "verdict": verdict,
        "permitted_verdicts": ["PROMISING", "INCONCLUSIVE", "NEGATIVE"],
        "generated_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "pc4_spec_hash": sp.get("pc4_spec_hash"),
        "protocol_hash": sp.get("protocol_hash") or protocol.protocol_hash(),
        "execution_config_hash": xp.get("execution_config_hash"),
        "simulator_version": xp.get("simulator_version"),
        "runner_version": sp.get("runner_version"),
        "runner_hash": sp.get("runner_hash"),
        "orchestrator_version": xp.get("orchestrator_version"),
        "orchestrator_hash": xp.get("orchestrator_hash"),
        "metrics_version": pm.METRICS_VERSION,
        "metrics_hash": metrics.metrics_hash(),
        "completeness_manifest_hash": (gate or {}).get("gap_registry_hash") or sp.get("completeness_manifest_hash"),
        "completeness_verdict": (gate or {}).get("verdict") or sp.get("gate_verdict"),
        "source_hashes": sp.get("source_hashes") or xp.get("source_hashes") or {},
        "signal_ledger_hash": sp.get("signal_ledger_hash"),
        "execution_ledger_hash": xp.get("execution_ledger_hash"),
        "git_commit": _git_commit(),
        "primary_metric": pm.PRIMARY_METRIC,
        "metrics": metrics.as_dict(),
        "signal_provenance": sp,
        "execution_provenance": {k: v for k, v in xp.items() if k != "sessions"},
        "sessions": xp.get("sessions", []),
        "baseline_provenance": baseline_v1.provenance(),
    }
    manifest["result_hash"] = hashlib.sha256(json.dumps(
        {"signals": manifest["signal_ledger_hash"], "execution": manifest["execution_ledger_hash"],
         "metrics": manifest["metrics_hash"]}, sort_keys=True).encode()).hexdigest()

    if require_provenance:
        missing = [k for k in REQUIRED_PROVENANCE if not manifest.get(k)]
        if missing:
            raise IncompleteProvenance(
                f"the package is missing required provenance: {', '.join(missing)}. "
                "No result may be presented without complete provenance (D42 §13).")

    frames = {
        "signals.csv": signals_frame(signal_ledger, execution_ledger),
        "trades.csv": trades_frame(execution_ledger),
        "monthly_metrics.csv": _monthly(metrics),
        "equity_curve.csv": _equity(metrics),
        "drawdowns.csv": pm.drawdowns(execution_ledger),
        "execution_quality.csv": _execution_quality(metrics),
    }
    for name, frame in frames.items():
        frame.to_csv(out / name, index=False)
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=1, default=str) + "\n")
    (out / "phase15a_report.md").write_text(_report_md(manifest, metrics, fixture))

    files = {name: _sha_file(out / name) for name in FILES}
    manifest["package_files"] = files
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=1, default=str) + "\n")
    return Package(directory=out, manifest=manifest, files=files)
