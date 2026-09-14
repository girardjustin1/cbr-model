"""Decoder and bar-building tests for the Dukascopy pipeline, on synthetic bi5 payloads with known answers."""

import lzma
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import pytest

from cbr.data import dukascopy_fetch as dk


def _bi5(records, dtype) -> bytes:
    return lzma.compress(np.array(records, dtype=dtype).tobytes(), format=lzma.FORMAT_ALONE)


def test_tick_decoder_scales_prices_and_offsets_times(monkeypatch):
    hour = datetime(2025, 11, 10, 1, tzinfo=UTC)
    payload = _bi5([(62, 4012225, 4011665, 0.12, 0.12), (1500, 4012300, 4011700, 0.5, 0.4)], dk.TICK_DTYPE)
    monkeypatch.setattr(dk, "_hour_file", lambda inst, h: payload if h == hour else b"")
    ticks = dk._decode_hours("xauusd", [hour, datetime(2025, 11, 10, 2, tzinfo=UTC)])
    assert list(ticks["ts"]) == [pd.Timestamp("2025-11-10 01:00:00.062", tz="UTC"),
                                 pd.Timestamp("2025-11-10 01:00:01.500", tz="UTC")]
    assert ticks["ask"].iloc[0] == pytest.approx(4012.225) and ticks["bid"].iloc[0] == pytest.approx(4011.665)


def test_candle_decoder_field_order_and_scale():
    payload = _bi5([(0, 4000000, 4002000, 3999000, 4003000, 1.5), (60, 4002000, 4001000, 4000500, 4002500, 0.0)],
                   dk.CANDLE_DTYPE)
    c = dk._decode_candles("xauusd", date(2025, 10, 21), payload)
    first = c.iloc[0]
    assert c.index[0] == pd.Timestamp("2025-10-21 00:00", tz="UTC") and c.index[1] == pd.Timestamp("2025-10-21 00:01", tz="UTC")
    assert (first["open"], first["close"], first["low"], first["high"]) == (4000.0, 4002.0, 3999.0, 4003.0)
    assert first["vol"] == pytest.approx(1.5) and c.iloc[1]["vol"] == 0


def test_bars_are_mid_based_gap_explicit_and_deterministic():
    ts = pd.to_datetime(["2025-10-21 01:00:01", "2025-10-21 01:00:03", "2025-10-21 01:00:20"], utc=True)
    ticks = pd.DataFrame({"ts": ts, "bid": [100.0, 101.0, 99.0], "ask": [100.2, 101.2, 99.4],
                          "bid_vol": 1.0, "ask_vol": 1.0})
    b5 = dk._bars(ticks, "5s")
    assert list(b5.index) == [pd.Timestamp("2025-10-21 01:00:00", tz="UTC"), pd.Timestamp("2025-10-21 01:00:20", tz="UTC")]
    first = b5.iloc[0]
    assert (first["open"], first["high"], first["low"], first["close"]) == pytest.approx((100.1, 101.1, 100.1, 101.1))
    assert first["tick_count"] == 2 and first["spread_max"] == pytest.approx(0.2)
    assert b5.iloc[1]["spread_mean"] == pytest.approx(0.4)
    pd.testing.assert_frame_equal(b5, dk._bars(ticks, "5s"))          # identical rebuild
