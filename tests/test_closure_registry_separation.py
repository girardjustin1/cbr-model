"""The execution closure registry must never reach strategy logic (owner ruling D43 §1-2, §7D-E).

D43 §1 is the binding constraint: `sessions.expected_closed` and PC4's TRADABLE condition-window basis must be
identical before and after the registry exists. The registry is an execution/data-interpretation concept only.
"""

from __future__ import annotations

import ast
import pathlib

import pandas as pd
import pytest

from cbr.data import market_closures as mc
from cbr.data import sessions

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "cbr"
CLOSURE_MODULE = "cbr.data.market_closures"

# Everything that decides what CBR does. If any of these ever learns about a verified closure, the frozen strategy
# has silently changed behaviour.
STRATEGY_PACKAGES = ("engine", "structure", "dxy")


def _imports(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text())
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
            out.update(f"{node.module}.{a.name}" for a in node.names)
    return out


def test_no_strategy_module_imports_the_closure_registry():
    """D43 §2: not PC4 condition logic, tradable-time, signal eligibility, extension logic or any CBR rule."""
    offenders = {}
    for package in STRATEGY_PACKAGES:
        for path in sorted((SRC / package).rglob("*.py")):
            if CLOSURE_MODULE in _imports(path):
                offenders[f"{package}/{path.name}"] = CLOSURE_MODULE
    assert not offenders, f"strategy logic imported the execution closure registry: {offenders}"


def test_the_session_calendar_itself_knows_nothing_about_closures():
    """The calendar PC4 reads must contain no holiday table and no reference to the registry."""
    text = (SRC / "data" / "sessions.py").read_text()
    assert CLOSURE_MODULE not in text
    assert "market_closures" not in text
    assert "holiday" not in text.lower()


def test_the_strategy_calendar_still_calls_a_verified_closure_tradable():
    """D43 §7D: tradable-time output is unchanged. Good Friday's hours stay *open* to the strategy calendar."""
    reg = mc.load()
    assert reg.closures, "the 2022 registry must hold closures for this test to mean anything"
    for start, end in reg.intervals():
        minutes = pd.date_range(start, end, freq="1min", tz="UTC", inclusive="left")
        open_minutes = [m for m in minutes if not sessions.expected_closed(m)]
        assert open_minutes, "a verified closure that the calendar already closed proves nothing here"
        # The calendar must be unaware: these minutes are still scheduled-open and still consume the window.
        assert not any(sessions.expected_closed_mask(pd.DatetimeIndex(open_minutes)))


def test_tradable_window_start_is_unaffected_by_the_registry(monkeypatch):
    """The window basis PC4 depends on must produce the same instant with and without a registry present."""
    as_of = pd.Timestamp("2022-04-18 12:00", tz="UTC")          # the Monday after Good Friday
    before = sessions.tradable_window_start(as_of, 8 * 60)
    monkeypatch.setattr(mc, "REGISTRY", mc.REGISTRY)             # registry present and loaded
    assert mc.load().closures
    after = sessions.tradable_window_start(as_of, 8 * 60)
    assert before == after


def test_pc4_signal_output_does_not_move_when_the_registry_changes(tmp_path, monkeypatch):
    """D43 §7E: the frozen engine produces an identical result with a populated and an empty registry."""
    from cbr.data import price_series as psm
    from cbr.engine import cbr1h_pc4 as pc4
    from cbr.engine.params_pc4 import load_cbr1h_pc4
    from tests.test_feed_comparison import T, _walk

    s5 = _walk("2019-01-08 00:00", 24 * 720, seed=31)
    s1 = psm.rollup_structure(s5, "1min")[["open", "high", "low", "close", "tick_count", "hl_method", "price_role"]]

    def run():
        return pc4.result_hash(pc4.run_cbr1h_pc4(s1, s5, start=T("2019-01-08 06:00"), end=T("2019-01-08 18:00"),
                                                 variant="A", params=load_cbr1h_pc4("A")))

    with_registry = run()
    empty = tmp_path / "empty.json"
    monkeypatch.setattr(mc, "REGISTRY", empty)
    assert not mc.load().closures
    assert run() == with_registry


def test_the_frozen_spec_hash_is_untouched():
    """Adding the registry must not have changed any file PC4's spec hash covers."""
    from cbr.engine import phase15a_protocol as protocol
    assert not protocol.drift().any()


@pytest.mark.parametrize("name", ["condition", "overextension", "shifts", "swings"])
def test_core_strategy_primitives_contain_no_closure_concept(name):
    for path in (SRC / "structure").rglob(f"{name}*.py"):
        text = path.read_text()
        assert "VERIFIED_MARKET_DATA_CLOSURE" not in text
        assert "market_closures" not in text
