from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_baseline", ROOT / "scripts" / "build_baseline.py")
baseline = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(baseline)


def test_empty_baseline_is_insufficient() -> None:
    result = baseline.build([], domain="airports", min_months=24, min_events=50)
    assert result["status"] == "insufficient"
    assert result["n_events"] == 0


def test_baseline_requires_months_and_events() -> None:
    rows = []
    for i in range(72):
        index = i // 3
        month = index % 12 + 1
        year = 2024 + index // 12
        rows.append({
            "event_id": f"E{i}", "event_date": f"{year}-{month:02d}-01",
            "published_at": f"{year}-{month:02d}-02", "airport": "TEST",
            "country": "ES", "event_type": "bomb", "source_url": "https://example.org",
            "source_type": "news", "independent_group": "g1" if i % 2 else "g2",
            "status": "DOCUMENTADO", "notes": "",
        })
    result = baseline.build(rows, domain="airports", min_months=24, min_events=50)
    assert result["status"] == "ready"
    assert result["n_events"] == 72
    assert result["months_covered"] == 24


def test_duplicate_event_ids_are_not_counted_twice() -> None:
    row = {
        "event_id": "SAME", "event_date": "2026-01-01", "published_at": "2026-01-02",
        "airport": "TEST", "country": "ES", "event_type": "bomb",
        "source_url": "https://example.org", "source_type": "news",
        "independent_group": "g1", "status": "DOCUMENTADO", "notes": "",
    }
    result = baseline.build([row, row], domain="airports", min_months=1, min_events=1)
    assert result["n_events"] == 1


def test_candidate_rows_do_not_enter_baseline() -> None:
    row = {
        "event_id": "C1", "event_date": "2026-01-01", "published_at": "2026-01-02",
        "airport": "", "country": "", "event_type": "bomb",
        "source_url": "https://example.org", "source_type": "news",
        "independent_group": "example.org", "status": "CANDIDATO", "notes": "",
    }
    result = baseline.build([row], domain="airports", min_months=1, min_events=1)
    assert result["n_events"] == 0
