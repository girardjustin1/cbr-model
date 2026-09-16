"""Expanded CBR1H parity set: immutable manifest builder (owner ruling D30 §11).

Usage:
    .venv/bin/python -m cbr.engine.parity_set            # writes research/examples/parity_set_manifest.json (refuses to overwrite)

Every case carries what D30-11 requires: identity, source and evidence level, the scored window, the scoring level and
the exact fields that may be scored. Nothing here reads engine output: the manifest is built from course evidence and
stored market data only, so it can be frozen before PC3 is ever run against it (D30-4, D30-20).

Scoring levels (D30-11):
  ENTRY_LEVEL   the source states an entry time and price: the full dimension table applies.
  HOUR_LEVEL    the source states the hour, direction and labels but no entry price: only those fields may be scored.
  NARRATIVE_ONLY no market data or no dated entry: geometry consistency only, never a machine pass count.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import pandas as pd

from cbr.data import canonical_bars as cb
from cbr.engine.params import ROOT

MANIFEST = ROOT / "research" / "examples" / "parity_set_manifest.json"
COURSE = "research/examples/course_examples.jsonl"
JOURNAL_FRAME = "research/frames/V1H-defining_a_good_extension/slides/00-02-42.jpg"

ENTRY_FIELDS = ["model_family", "direction", "condition", "extension_direction", "extension_activation",
                "location_or_previous_candle_event", "hvcs_state", "type3_5s_trigger", "eligible_candidate",
                "trigger_time", "trigger_price", "stop_anchor_concept", "target_concept"]
HOUR_FIELDS = ["setup_exists_in_hour", "direction", "model_family_if_source_defined", "condition_if_source_defined",
               "timing_bucket_if_source_defined"]
NEGATIVE_FIELDS = ["no_eligible_candidate_for_the_rejected_geometry"]

CASES = [
    # ---------------------------------------------------------------- ENTRY_LEVEL (course videos)
    {"case_id": "CX-LT1-1", "source": COURSE, "source_detail": "V1H-live_trade_1_gold_win",
     "evidence_level": "L1_VIDEO", "instrument": "XAUUSD", "model": "CBR1H", "direction": "BUY",
     "positive_or_negative": "POSITIVE", "hour_utc": "2025-10-21T01:00:00+00:00",
     "data_span_utc": ["2025-10-20T00:00:00+00:00", "2025-10-21T03:00:00+00:00"],
     "scoring_level": "ENTRY_LEVEL", "stated": {"entry_time_utc": "2025-10-21T01:39:15+00:00", "entry": 4340.13,
                                                "stop": 4332.96, "target": 4351.59}},
    {"case_id": "CX-TE1-1", "source": COURSE, "source_detail": "V1H-trade_example_1", "evidence_level": "L1_VIDEO",
     "instrument": "XAUUSD", "model": "CBR1H", "direction": "BUY", "positive_or_negative": "POSITIVE",
     "hour_utc": "2025-10-24T04:00:00+00:00",
     "data_span_utc": ["2025-10-20T00:00:00+00:00", "2025-10-24T06:00:00+00:00"],
     "scoring_level": "ENTRY_LEVEL", "stated": {"entry_time_utc": ["2025-10-24T04:37:00+00:00",
                                                                  "2025-10-24T04:39:00+00:00"],
                                                "entry": 4105.58, "stop": 4102.80, "target": 4109.71}},
    {"case_id": "CX-LT3-2", "source": COURSE, "source_detail": "V1H-live_trade_3_gold_win", "evidence_level": "L1_VIDEO",
     "instrument": "XAUUSD", "model": "CBR1H", "direction": "SELL", "positive_or_negative": "POSITIVE",
     "hour_utc": "2025-11-10T01:00:00+00:00",
     "data_span_utc": ["2025-11-07T00:00:00+00:00", "2025-11-10T03:00:00+00:00"],
     "scoring_level": "ENTRY_LEVEL", "stated": {"entry_time_utc": "2025-11-10T01:40:00+00:00", "entry": 4050.71,
                                                "stop": 4053.30, "target": 4043.80}},
    {"case_id": "CX-LT3-1", "source": COURSE, "source_detail": "V1H-live_trade_3_gold_win", "evidence_level": "L1_VIDEO",
     "instrument": "XAUUSD", "model": "CBR1H", "direction": "SELL", "positive_or_negative": "NEGATIVE",
     "hour_utc": "2025-11-10T01:00:00+00:00",
     "data_span_utc": ["2025-11-07T00:00:00+00:00", "2025-11-10T03:00:00+00:00"],
     "scoring_level": "ENTRY_LEVEL",
     "stated": {"rejected_window_utc": ["2025-11-10T01:28:00+00:00", "2025-11-10T01:36:00+00:00"],
                "rejected_because": ["shift too small", "shift not clean", "pushing off a 5m/15m candle open",
                                     "gold spread and DXY moving together (out of scope, D7)"]}},
    # ---------------------------------------------------------------- HOUR_LEVEL (journal table in a Level-1 frame)
    {"case_id": "JM-2025-10-16", "source": JOURNAL_FRAME, "source_detail": "Journal Master 2025 row 'nice GS'",
     "evidence_level": "L1_FRAME_JOURNAL_TABLE", "instrument": "XAUUSD", "model": "CBR1H", "direction": "SELL",
     "positive_or_negative": "POSITIVE", "hour_utc": "2025-10-16T00:00:00+00:00",
     "data_span_utc": ["2025-10-15T00:00:00+00:00", "2025-10-16T02:00:00+00:00"],
     "scoring_level": "HOUR_LEVEL",
     "stated": {"journal_time_local": "2025-10-16 11:41 AM (UTC+11)", "mtf_model": "TRR CT", "condition": "Trending",
                "cb_hour": 37, "shifts": "LLTF (Seconds)", "reversal_label": "30m Reversal", "aoi": None}},
    {"case_id": "JM-2025-10-17", "source": JOURNAL_FRAME, "source_detail": "Journal Master 2025 row 'ok, dxy cor'",
     "evidence_level": "L1_FRAME_JOURNAL_TABLE", "instrument": "XAUUSD", "model": "CBR1H", "direction": "BUY",
     "positive_or_negative": "POSITIVE", "hour_utc": "2025-10-17T01:00:00+00:00",
     "data_span_utc": ["2025-10-16T00:00:00+00:00", "2025-10-17T03:00:00+00:00"],
     "scoring_level": "HOUR_LEVEL",
     "stated": {"journal_time_local": "2025-10-17 12:53 PM (UTC+11)", "mtf_model": "IFS", "condition": "Volume",
                "cb_hour": 52, "shifts": "LLTF (Seconds) + LTF (1m)", "reversal_label": "45m Reversal",
                "aoi": "1hr, 30m"}},
    {"case_id": "JM-2025-10-29", "source": JOURNAL_FRAME, "source_detail": "Journal Master 2025 row 'niceueeee'",
     "evidence_level": "L1_FRAME_JOURNAL_TABLE", "instrument": "XAUUSD", "model": "CBR1H", "direction": "BUY",
     "positive_or_negative": "POSITIVE", "hour_utc": "2025-10-29T08:00:00+00:00",
     "data_span_utc": ["2025-10-28T00:00:00+00:00", "2025-10-29T10:00:00+00:00"],
     "scoring_level": "HOUR_LEVEL",
     "stated": {"journal_time_local": "2025-10-29 7:14 PM (UTC+11)", "mtf_model": "TRR PT", "condition": "Trending",
                "cb_hour": 37, "shifts": "LLTF (Seconds)", "reversal_label": "30m Reversal", "aoi": "4h"}},
    # ---------------------------------------------------------------- NARRATIVE_ONLY
    {"case_id": "CX-LT2-2", "source": COURSE, "source_detail": "V1H-live_trade_2_uj_loss", "evidence_level": "L1_VIDEO",
     "instrument": "USDJPY", "model": "CBR1H", "direction": "SELL", "positive_or_negative": "POSITIVE",
     "hour_utc": "2025-10-23T01:00:00+00:00", "data_span_utc": None, "scoring_level": "NARRATIVE_ONLY",
     "stated": {"entry": 152.402, "stop": 152.457, "geometry": "sell at the break of that low"},
     "why_narrative": "USDJPY is outside backtest research scope (D7, D29-21): no market data is acquired"},
    {"case_id": "CX-LT2-1", "source": COURSE, "source_detail": "V1H-live_trade_2_uj_loss", "evidence_level": "L1_VIDEO",
     "instrument": "USDJPY", "model": "CBR1H", "direction": "SELL", "positive_or_negative": "NEGATIVE",
     "hour_utc": "2025-10-23T01:00:00+00:00", "data_span_utc": None, "scoring_level": "NARRATIVE_ONLY",
     "stated": {"rejected_because": ["~22 minutes into the hour is too early", "better late than early"]},
     "why_narrative": "same instrument scope limit; the stated rejection is about timing, not geometry"},
    {"case_id": "T3-VP1-A", "source": "research/frames/VP1-1_4_shifts_type_3_choch/slides/00-03-04.jpg",
     "source_detail": "VP1-1_4_shifts_type_3_choch 00:03:04", "evidence_level": "L1_FRAME", "instrument": "XAUUSD",
     "model": "TYPE3_LESSON", "direction": None, "positive_or_negative": "POSITIVE",
     "hour_utc": None, "data_span_utc": None, "scoring_level": "NARRATIVE_ONLY",
     "stated": {"geometry": "ranging type 3: take the range high, then the range low, then shift"},
     "why_narrative": "chart date ~2025-01-20/21; no stored data and no stated entry"},
    {"case_id": "T3-VP1-B", "source": "research/frames/VP1-1_4_shifts_type_3_choch/slides/00-03-38.jpg",
     "source_detail": "VP1-1_4_shifts_type_3_choch 00:03:38", "evidence_level": "L1_FRAME", "instrument": "XAUUSD",
     "model": "TYPE3_LESSON", "direction": "BUY", "positive_or_negative": "POSITIVE", "hour_utc": None,
     "data_span_utc": None, "scoring_level": "NARRATIVE_ONLY",
     "stated": {"geometry": "swept low marked and extended as a level, then the reversal"},
     "why_narrative": "same lesson chart; no stored data"},
    {"case_id": "T3-VP2-HILO", "source": "research/transcripts/phase2/VP2-1m_hilo_entries.json",
     "source_detail": "VP2-1m_hilo_entries 00:02:44-00:05:25", "evidence_level": "L1_VIDEO", "instrument": "XAUUSD",
     "model": "HILO", "direction": None, "positive_or_negative": "BOTH", "hour_utc": None, "data_span_utc": None,
     "scoring_level": "NARRATIVE_ONLY",
     "stated": {"geometry": "valid vs invalid HILO; reference levels re-anchor to the previous candle each candle"},
     "why_narrative": "teaching sequence, no dated entry"},
    {"case_id": "OE-GOOD-BAD", "source": "research/transcripts/hourly/V1H-defining_a_good_extension.json",
     "source_detail": "V1H-defining_a_good_extension 00:03:19, 00:05:03, 00:05:16", "evidence_level": "L1_VIDEO",
     "instrument": "XAUUSD", "model": "CBR1H_EXTENSION", "direction": None, "positive_or_negative": "BOTH",
     "hour_utc": None, "data_span_utc": None, "scoring_level": "NARRATIVE_ONLY",
     "stated": {"geometry": "'didn't correct 50% at all' (good) vs 'on average correcting 50% of the previous move' (bad)"},
     "why_narrative": "illustrative charts, no dated entries; direct OE-2 geometry check"},
    {"case_id": "V15-SEM-2026-05", "source": "research/frames/V15-seconds_entry_model/slides/00-00-22.jpg",
     "source_detail": "V15-seconds_entry_model", "evidence_level": "L1_FRAME", "instrument": "XAUUSD",
     "model": "CBR15", "direction": None, "positive_or_negative": "INSTRUCTIONAL", "hour_utc": None,
     "data_span_utc": None, "scoring_level": "NARRATIVE_ONLY",
     "stated": {"chart_date": "~2026-05-01 (5s, FOREX.com)", "note": "illustrative walkthrough, no stated entry"},
     "why_narrative": "D30-10: no entry-level metadata; CBR15 PC3 stays unscored"},
]


def _sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def session_of(hour_utc: str | None) -> str | None:
    """Coarse session label from the UTC hour (reporting only; no rule depends on it)."""
    if hour_utc is None:
        return None
    h = pd.Timestamp(hour_utc).hour
    if 22 <= h or h < 7:
        return "ASIA"
    if 7 <= h < 12:
        return "LONDON"
    if 12 <= h < 17:
        return "LONDON_NY_OVERLAP"
    return "NEW_YORK"


def market_data_hashes(span) -> dict:
    if not span:
        return {}
    a, b = (pd.Timestamp(x) for x in span)
    out = {}
    for day in pd.date_range(a.floor("D"), b, freq="D", inclusive="left"):
        for tag in ("1m", "5s"):
            p = cb.OUT / f"structure_{tag}" / f"{day.date().isoformat()}.parquet"
            if p.exists():
                out[str(p.relative_to(ROOT))] = _sha(str(p.relative_to(ROOT)))
    return out


def fields_for(case: dict) -> list[str]:
    if case["scoring_level"] == "NARRATIVE_ONLY":
        return ["geometry_consistency_only"]
    if case["positive_or_negative"] == "NEGATIVE":
        return NEGATIVE_FIELDS
    return ENTRY_FIELDS if case["scoring_level"] == "ENTRY_LEVEL" else HOUR_FIELDS


def build() -> dict:
    cases = []
    for c in CASES:
        span = c["data_span_utc"]
        mdh = market_data_hashes(span)
        cases.append({
            "case_id": c["case_id"], "source": c["source"], "source_detail": c["source_detail"],
            "evidence_level": c["evidence_level"], "instrument": c["instrument"], "model": c["model"],
            "direction": c["direction"], "positive_or_negative": c["positive_or_negative"],
            "session": session_of(c["hour_utc"]), "start_time": c["hour_utc"],
            "end_time": None if c["hour_utc"] is None else str(pd.Timestamp(c["hour_utc"]) + pd.Timedelta(hours=1)),
            "data_span_utc": span, "scoring_level": c["scoring_level"], "stated": c["stated"],
            "source_hashes": {c["source"]: _sha(c["source"])},
            "market_data_hashes": mdh,
            "market_data_status": "COMPLETE" if mdh else ("NOT_REQUIRED" if c["scoring_level"] == "NARRATIVE_ONLY"
                                                          else "DATA_LIMITATION"),
            "fields_allowed_for_scoring": fields_for(c),
            **({"why_narrative": c["why_narrative"]} if "why_narrative" in c else {}),
        })
    payload = {
        "manifest_version": "CBR-SET-001 v1.0", "ruling": "D30", "generated_utc":
            datetime.now(UTC).replace(microsecond=0).isoformat(),
        "scope": "CBR1H parity preparation; CBR15 PC3 is SPEC_ONLY and unscored (D30-3)",
        "counts": {lvl: sum(1 for c in cases if c["scoring_level"] == lvl)
                   for lvl in ("ENTRY_LEVEL", "HOUR_LEVEL", "NARRATIVE_ONLY")},
        "cases": cases,
    }
    payload["manifest_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in payload.items() if k != "generated_utc"}, sort_keys=True).encode()).hexdigest()
    return payload


def main() -> None:
    if MANIFEST.exists():
        raise SystemExit(f"{MANIFEST.relative_to(ROOT)} exists: the parity set is frozen; create a new version instead")
    m = build()
    MANIFEST.write_text(json.dumps(m, indent=1) + "\n")
    print(json.dumps({"manifest_hash": m["manifest_hash"], "counts": m["counts"]}, indent=2))


if __name__ == "__main__":
    main()
