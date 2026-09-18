"""Phase 14A authoritative execution simulator (owner ruling D38).

Consumes frozen `CBR1H_BASELINE_V1` signals and decides only whether and at what price orders fill. No module in
this package may import a CBR strategy-rule module: signal generation and execution stay strictly separated
(D38 §1, §33), and `tests/execution/test_architecture_guard.py` enforces it.
"""
