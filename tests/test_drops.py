"""
One example test so `make test` works out of the box. It asserts the drop
files actually contain the warts the README describes -- useful as a sanity
check that `make setup` produced what you expect.

Part 2 asks for at least one meaningful test of your own; add it here or in a
new file.
"""
import json
import os
import pathlib

DROPS = pathlib.Path(__file__).resolve().parents[1] / "data" / "drops"

pytestmark = __import__("pytest").mark.skipif(
    not DROPS.exists(), reason="run `make setup` first")


def _load(day):
    with open(DROPS / f"day_{day}.json") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_all_seven_days_present():
    assert sorted(p.name for p in DROPS.glob("day_*.json")) == [
        f"day_{i}.json" for i in range(1, 8)]


def test_schema_drift_starts_at_day_four():
    assert all("buy_box_pct" not in r for r in _load(3))
    assert any("buy_box_pct" in r for r in _load(4))


def test_day_six_carries_late_day_two_rows():
    late = [r for r in _load(6) if r["report_date"] == "2026-08-02"]
    assert late, "expected late-arriving day-2 records inside day 6"


def test_files_contain_exact_duplicates():
    rows = _load(1)
    keyed = [json.dumps(r, sort_keys=True) for r in rows]
    assert len(keyed) != len(set(keyed)), "expected duplicate records"
