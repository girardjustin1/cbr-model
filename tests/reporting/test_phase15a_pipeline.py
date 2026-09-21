"""Phase 15A construction tests (owner ruling D42 §4-13).

Synthetic fixtures only. No 2022 data is read, no historical CBR outcome is produced, and every "trade" below is a
fabricated ledger row written by the test itself.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date

import pandas as pd
import pytest

from cbr.engine import historical_runner as hr
from cbr.engine import phase15a_protocol as protocol
from cbr.execution import ledger as el
from cbr.execution import orchestrator as orch
from cbr.reporting import phase15a_metrics as pm
from cbr.reporting import phase15a_package as pkg
from cbr.reporting import rerun_harness as rh


# ─── fixtures ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _bars():
    from cbr.data import price_series as psm
    from tests.test_feed_comparison import _walk
    # Inside the development window on purpose: the period guard stays fully active in these tests.
    s5 = _walk("2019-01-08 00:00", 2 * 24 * 720, seed=31)
    s1 = psm.rollup_structure(s5, "1min")[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]
    return {"1m": s1, "5s": s5}


@pytest.fixture(scope="module")
def fixture_ledger():
    """A real PC4 signal ledger over synthetic bars: the runner is exercised, the strategy is not measured."""
    return hr.run("2019-01-09", "2019-01-09", variants=("A",), bars=_bars(), fixture=True)


def _signal(sid: str, when: str, *, variant="A", direction="SHORT") -> dict:
    """A frozen-shape PC4 signal, hand-built. The package writer reads exactly these fields (D42 §8)."""
    return {
        "signal_id": sid, "model": "CBR1H_BASELINE_V1-PC4", "variant": variant, "direction": direction,
        "timestamp": when, "entry_trigger_time": when, "entry_reference_price": 1990.0, "target_price": 1980.0,
        "context_state": {"condition": "RANGE", "hvcs_minutes": 6},
        "extension": {"state": "UP", "activation_time": when},
        "stop_rule": {"extension_extreme": 1996.0, "structure_stop_anchor": 1994.5},
        "data_confidence": {"level": "FULL", "reason_codes": []},
    }


def _synthetic_ledger(n: int = 6, *, span=("2022-01-01", "2022-12-31")) -> hr.SignalLedger:
    """A synthetic signal ledger for the writer and metric tests. No real signal, no real outcome."""
    times = [f"2022-03-{8 + i:02d}T{10 + i}:30:00+00:00" for i in range(n)]
    led = hr.SignalLedger(
        span=span, variants=["A", "B"],
        signals=[_signal(f"SYN-{i:03d}", t, variant="A" if i % 2 else "B") for i, t in enumerate(times)])
    led.provenance = {
        "runner_version": hr.RUNNER_VERSION, "runner_hash": hr.runner_hash(),
        "pc4_spec_hash": protocol.FROZEN_PC4_SPEC_HASH, "protocol_hash": protocol.protocol_hash(),
        "execution_config_hash": protocol.execution_config_hash(),
        "mode": "FIXTURE_NON_PERFORMANCE", "source_hashes": {"structure_1m/2022-03-08.parquet": "b" * 64},
        "completeness_manifest_hash": "r" * 64, "gate_verdict": "COMPLETE",
        "signal_ledger_hash": led.ledger_hash(),
    }
    return led


def _record(sid, *, status=el.CLOSED, exit_reason=el.TARGET, net_r=1.0, gross_r=None, variant="A",
            direction="SHORT", fill="2022-03-08T10:00:00+00:00", exit_t="2022-03-08T11:00:00+00:00",
            reason_code=None):
    return el.ExecutionRecord(
        signal_id=sid, model="CBR1H_BASELINE_V1-PC4", variant=variant, direction=direction,
        signal_time="2022-03-08T09:50:00+00:00", activation_time="2022-03-08T09:55:00+00:00",
        trigger_price=1990.0, execution_status=status, reason_code=reason_code,
        fill_time=fill if status in (el.CLOSED, el.FILLED) else None,
        fill_price=1990.0 if status in (el.CLOSED, el.FILLED) else None,
        entry_gap=0.1, fill_spread=0.3, final_execution_stop=1995.0, target_price=1980.0, initial_risk=5.0,
        fill_time_stop_anchor=1994.5, stop_gap=0.0,
        exit_time=exit_t if status == el.CLOSED else None,
        exit_price=1980.0 if status == el.CLOSED else None,
        exit_reason=exit_reason if status == el.CLOSED else None,
        gross_r=(net_r if gross_r is None else gross_r) if status == el.CLOSED else None,
        net_r=net_r if status == el.CLOSED else None,
        tick_resolved=True, data_confidence={"level": "FULL"}, source_hashes={"ticks/2022-03-08.parquet": "a" * 64})


@dataclass
class FakeExecLedger:
    records: list = field(default_factory=list)
    provenance: dict = field(default_factory=dict)

    def frame(self):
        return pd.DataFrame([r.as_dict() for r in self.records])

    def execution_ledger_hash(self):
        return orch.ExecutionLedger(records=self.records).execution_ledger_hash()


def _exec_ledger(records, signal_ledger=None):
    out = orch.ExecutionLedger(records=records)
    out.provenance = {
        "orchestrator_version": orch.ORCHESTRATOR_VERSION, "orchestrator_hash": orch.orchestrator_hash(),
        "simulator_version": el.SIMULATOR_VERSION, "execution_config_hash": "e" * 64,
        "source_hashes": {"ticks/2022-03-08.parquet": "a" * 64},
        "signal_ledger_hash": (signal_ledger.provenance.get("signal_ledger_hash") if signal_ledger else "s" * 64),
    }
    out.provenance["execution_ledger_hash"] = out.execution_ledger_hash()
    return out


# ─── the runner and its refusals (D42 §4-5) ───────────────────────────────────────────────────────────────────────
def test_the_runner_generates_a_deterministic_signal_ledger(fixture_ledger):
    again = hr.run("2019-01-09", "2019-01-09", variants=("A",), bars=_bars(), fixture=True)
    assert fixture_ledger.ledger_hash() == again.ledger_hash()
    assert fixture_ledger.provenance["mode"] == "FIXTURE_NON_PERFORMANCE"
    assert fixture_ledger.provenance["pc4_spec_hash"] == protocol.FROZEN_PC4_SPEC_HASH


def test_every_signal_id_is_preserved_and_unique(fixture_ledger):
    ids = [s["signal_id"] for s in fixture_ledger.signals]
    assert len(ids) == len(set(ids))
    assert all(s["model"].startswith("CBR1H_BASELINE_V1") for s in fixture_ledger.signals)


def test_candidate_and_rejection_information_is_emitted(fixture_ledger):
    """The frozen ledger's rejection view must survive the runner, or a rejected hour becomes invisible."""
    d = fixture_ledger.decisions
    assert len(d) > 0
    assert "rules_failed" in d.columns
    assert fixture_ledger.provenance["candidate_count"] == len(d)


def test_the_runner_refuses_a_partial_span():
    """D42 §5, §10: quarterly and month-by-month performance must be impossible, not merely discouraged."""
    with pytest.raises(hr.PartialSpanRefused):
        hr.run("2022-01-01", "2022-03-31")
    with pytest.raises(hr.PartialSpanRefused):
        hr.run("2022-06-01", "2022-06-30")


def test_the_runner_refuses_an_incomplete_span():
    """The hard completeness test required by D42 §5."""
    incomplete = {"verdict": "INCOMPLETE", "unresolved_failures": 12, "days_missing_tick_file": ["2022-05-02"],
                  "gaps_resolved": True, "blocks_complete": 11}
    with pytest.raises(hr.SpanIncomplete):
        hr.run("2022-01-01", "2022-12-31", gate_result=incomplete)


def test_a_complete_gate_passes_the_completeness_guard():
    complete = {"verdict": "COMPLETE", "unresolved_failures": 0, "days_missing_tick_file": [],
                "gaps_resolved": True, "blocks_complete": 12, "gap_registry_hash": "r" * 64}
    assert hr.check_complete(complete)["verdict"] == "COMPLETE"


def test_the_runner_refuses_validation_and_holdout_without_authorization():
    with pytest.raises(hr.RestrictedPeriod):
        hr.run("2023-01-01", "2023-12-31")
    with pytest.raises(hr.RestrictedPeriod):
        hr.run("2025-01-01", "2025-12-31")
    # The token is the only way through, and it is recorded rather than assumed.
    assert hr.check_period(date(2023, 1, 1), date(2023, 12, 31), hr.AUTHORIZATION_TOKEN) == "VALIDATION"
    assert hr.check_period(date(2025, 1, 1), date(2025, 12, 31), hr.AUTHORIZATION_TOKEN) == "HOLDOUT"


def test_the_runner_refuses_when_a_frozen_spec_has_drifted(monkeypatch):
    monkeypatch.setattr(protocol, "FROZEN_PROTOCOL_HASH", "0" * 64)
    with pytest.raises(hr.FrozenSpecDrift):
        hr.run("2019-01-09", "2019-01-09", bars=_bars(), fixture=True)


def test_fixture_mode_never_reads_the_canonical_store():
    with pytest.raises(hr.RunnerRefusal):
        hr.run("2019-01-09", "2019-01-09", fixture=True)


# ─── the orchestrator (D42 §6) ────────────────────────────────────────────────────────────────────────────────────
def test_sessions_are_grouped_at_the_new_york_rollover():
    """A signal after 17:00 New York belongs to the next session, so one position cannot appear in two chunks."""
    assert orch.session_day(pd.Timestamp("2022-03-08T21:00:00Z")) == date(2022, 3, 8)   # 16:00 New York
    assert orch.session_day(pd.Timestamp("2022-03-08T23:30:00Z")) == date(2022, 3, 9)   # 18:30 New York
    start, end = orch.session_window(date(2022, 3, 9))
    assert start < pd.Timestamp("2022-03-08T23:30:00Z") < end


def test_every_signal_yields_exactly_one_execution_record():
    led = _synthetic_ledger(6)
    seen = []

    def fake_replay(signals, start, end, *, instrument, params):
        seen.append((start, end, len(signals)))
        recs = [_record(s["signal_id"], variant=s["variant"], direction=s["direction"]) for s in signals]
        return type("R", (), {"records": recs, "provenance": {"tick_count": 10, "source_hashes": {},
                                                              "classified_intervals": {"VALID_SPARSE_QUOTES": 60},
                                                              "result_hash": "h"}})()

    ex = orch.orchestrate(led, replay_fn=fake_replay)
    assert ex.provenance["records_out"] == len(led.signals)
    assert ex.provenance["every_signal_recorded"] is True
    assert len(seen) == ex.provenance["session_count"] >= 1


def test_a_signal_without_a_time_is_recorded_not_dropped():
    ledger = hr.SignalLedger(span=("2022-01-01", "2022-12-31"), variants=["A"],
                             signals=[{"signal_id": "X1", "model": "m", "variant": "A", "direction": "SHORT"}])
    ex = orch.orchestrate(ledger, replay_fn=lambda *a, **k: None)
    assert len(ex.records) == 1
    assert ex.records[0].execution_status == el.NOT_EXECUTED
    assert ex.records[0].data_confidence["orchestrator"] == "NO_ACTIVATION_TIME"


# ─── metrics (D42 §10-11) ─────────────────────────────────────────────────────────────────────────────────────────
def test_only_canonical_completed_trades_reach_expectancy():
    """Administrative exits and unprovable outcomes never enter the win/loss or expectancy statistics."""
    recs = [
        _record("A1", net_r=2.0),
        _record("A2", exit_reason=el.STOP, net_r=-1.0),
        _record("A3", exit_reason=el.ROLLOVER_EXIT, net_r=9.9),          # administrative: excluded
        _record("A4", status=el.UNPROVABLE, reason_code=el.TRADE_OUTCOME_UNPROVABLE_DATA_GAP, fill=None),
        _record("A5", status=el.NOT_EXECUTED, reason_code=el.ENTRY_NOT_TRIGGERED, fill=None),
    ]
    m = pm.compute(_exec_ledger(recs))
    assert m.values["trade_count"] == 2
    assert m.values["net_expectancy_r"] == pytest.approx(0.5)            # (2.0 + -1.0) / 2, the 9.9 excluded
    assert m.values["win_rate"] == pytest.approx(0.5)
    assert m.values["denominator"] == 2
    assert m.funnel["administrative_exits"] == 1
    assert m.funnel["unprovable"] == 1
    assert m.funnel["every_signal_accounted"] is True
    assert m.execution_quality["administrative_r"]["net_r"] == pytest.approx(9.9)


def test_no_win_or_loss_is_inferred_for_an_unprovable_outcome():
    recs = [_record("U1", status=el.UNPROVABLE, reason_code=el.EXECUTION_UNPROVABLE_INTRABAR, fill=None)]
    m = pm.compute(_exec_ledger(recs))
    assert m.values["trade_count"] == 0
    assert m.values["wins"] is None and m.values["losses"] is None
    assert m.funnel["unprovable_rate"] == pytest.approx(1.0)


def test_the_primary_metric_is_unchanged_and_breakdowns_are_marked_descriptive():
    recs = [_record("A1", net_r=1.5), _record("B1", variant="B", direction="LONG", exit_reason=el.STOP, net_r=-1.0)]
    m = pm.compute(_exec_ledger(recs))
    assert pm.PRIMARY_METRIC == "net_expectancy_r"
    assert m.as_dict()["primary_metric"] == "net_expectancy_r"
    assert set(m.breakdowns) >= {"month", "direction", "variant", "session_bucket"}
    assert "DESCRIPTIVE ONLY" in m.breakdowns["_note"]
    assert m.breakdowns["variant"]["A"]["trade_count"] == 1
    assert m.breakdowns["variant"]["B"]["trade_count"] == 1


def test_profit_factor_and_drawdown_are_computed_from_trade_level_r():
    recs = [_record(f"T{i}", exit_reason=el.TARGET if r > 0 else el.STOP, net_r=r,
                    exit_t=f"2022-03-0{i + 1}T11:00:00+00:00")
            for i, r in enumerate([2.0, -1.0, -1.0, 3.0])]
    m = pm.compute(_exec_ledger(recs))
    assert m.values["profit_factor"] == pytest.approx(5.0 / 2.0)
    assert m.values["max_drawdown_r"] == pytest.approx(-2.0)
    assert m.values["longest_losing_streak"] == 2
    dd = pm.drawdowns(_exec_ledger(recs))
    assert len(dd) == 1 and dd.iloc[0]["depth_r"] == pytest.approx(-2.0)


def test_metrics_are_deterministic():
    recs = [_record("A1", net_r=2.0), _record("A2", exit_reason=el.STOP, net_r=-1.0)]
    assert pm.compute(_exec_ledger(recs)).metrics_hash() == pm.compute(_exec_ledger(recs)).metrics_hash()


# ─── the review package (D42 §7-9, §13-14) ────────────────────────────────────────────────────────────────────────
def _package(tmp_path, ledger=None, verdict="NOT_ASSESSED"):
    led = ledger or _synthetic_ledger(6)
    recs = [_record(s["signal_id"], variant=s["variant"], direction=s["direction"],
                    net_r=1.0 if i % 2 else -1.0, exit_reason=el.TARGET if i % 2 else el.STOP)
            for i, s in enumerate(led.signals)]
    ex = _exec_ledger(recs, led)
    m = pm.compute(ex)
    return pkg.write(led, ex, m, directory=tmp_path, fixture=True, verdict=verdict,
                     gate={"gap_registry_hash": "r" * 64, "verdict": "COMPLETE"}), ex, m


def test_the_package_writes_all_eight_artefacts(tmp_path):
    p, _ex, _m = _package(tmp_path)
    for name in pkg.FILES:
        assert (tmp_path / name).exists(), name
    assert set(p.files) == set(pkg.FILES)


def test_signals_csv_carries_every_required_column(tmp_path):
    led = _synthetic_ledger(6)
    _package(tmp_path, led)
    df = pd.read_csv(tmp_path / "signals.csv")
    assert list(df.columns) == list(pkg.SIGNAL_COLUMNS)
    assert len(df) == len(led.signals)


def test_trades_csv_lets_an_auditor_reconstruct_each_trade(tmp_path):
    _package(tmp_path)
    df = pd.read_csv(tmp_path / "trades.csv")
    assert list(df.columns) == list(pkg.TRADE_COLUMNS)
    assert len(df) > 0
    # Expectancy is recomputable from the file alone, which is the whole point of the package.
    canon = df[(~df["administrative_exit"]) & (df["exit_reason"].isin(["TARGET", "STOP"]))]
    manifest = json.loads((tmp_path / "run_manifest.json").read_text())
    assert canon["net_r"].mean() == pytest.approx(manifest["metrics"]["metrics"]["net_expectancy_r"])


def test_the_package_refuses_incomplete_provenance(tmp_path):
    """D42 §13: no result may be presented without complete provenance."""
    led = _synthetic_ledger(2)
    ex = _exec_ledger([_record("A1", net_r=1.0)], led)
    ex.provenance.pop("orchestrator_hash")
    with pytest.raises(pkg.IncompleteProvenance) as err:
        pkg.write(led, ex, pm.compute(ex), directory=tmp_path, fixture=True)
    assert "orchestrator_hash" in str(err.value)


def test_the_report_states_what_the_result_is_and_is_not(tmp_path):
    _package(tmp_path, verdict="INCONCLUSIVE")
    text = (tmp_path / "phase15a_report.md").read_text()
    assert "DEVELOPMENT PILOT" in text
    assert "VALIDATED EDGE" not in text.upper().replace("NEVER A VALIDATED EDGE", "")
    assert "FIXTURE RUN — NOT A RESULT" in text
    assert "net expectancy in r per executed canonical trade" in text.lower()
    manifest = json.loads((tmp_path / "run_manifest.json").read_text())
    assert manifest["permitted_verdicts"] == ["PROMISING", "INCONCLUSIVE", "NEGATIVE"]
    assert manifest["baseline_provenance"]["parity_verdict"] == "FAIL"


# ─── the deterministic rerun harness (D42 §12) ────────────────────────────────────────────────────────────────────
def test_two_identical_runs_pass(tmp_path):
    led = _synthetic_ledger(6)

    def pipeline(directory):
        p, ex, m = _package(directory, led)
        return {"signal_ledger_hash": led.ledger_hash(),
                "execution_ledger_hash": ex.execution_ledger_hash(),
                "metrics_hash": m.metrics_hash(), "result_hash": p.manifest["result_hash"]}

    cmp = rh.run_twice(pipeline, directories=(tmp_path / "a", tmp_path / "b"))
    assert cmp.verdict == "PASS", cmp.differences


def test_a_timestamp_alone_is_not_a_divergence(tmp_path):
    """The manifest and report carry a generation time; a semantic hash keeps that from faking a FAIL."""
    led = _synthetic_ledger(6)
    a, b = tmp_path / "a", tmp_path / "b"
    _package(a, led)
    _package(b, led)
    # Force the one difference two runs of identical inputs may legitimately have: when they were generated.
    for path, stamp in ((a / "run_manifest.json", "2026-09-20T10:00:00+00:00"),
                        (b / "run_manifest.json", "2027-01-01T23:59:59+00:00")):
        body = json.loads(path.read_text())
        body["generated_utc"] = stamp
        path.write_text(json.dumps(body, indent=1, default=str) + "\n")
    assert (a / "run_manifest.json").read_bytes() != (b / "run_manifest.json").read_bytes()
    assert rh.semantic_hash(a / "run_manifest.json") == rh.semantic_hash(b / "run_manifest.json")
    assert rh.semantic_hash(a / "phase15a_report.md") == rh.semantic_hash(b / "phase15a_report.md")
    # A real content change is still caught.
    body = json.loads((b / "run_manifest.json").read_text())
    body["metrics"]["metrics"]["net_expectancy_r"] = 99.0
    (b / "run_manifest.json").write_text(json.dumps(body, indent=1, default=str) + "\n")
    assert rh.semantic_hash(a / "run_manifest.json") != rh.semantic_hash(b / "run_manifest.json")


def test_any_substantive_divergence_is_a_fail():
    cmp = rh.compare({"signal_ledger_hash": "a", "metrics_hash": "m", "package": {"trades.csv": "1"}},
                     {"signal_ledger_hash": "a", "metrics_hash": "m2", "package": {"trades.csv": "2"}})
    assert cmp.verdict == "FAIL"
    fields = {d["field"] for d in cmp.differences}
    assert fields == {"metrics_hash", "package/trades.csv"}
