"""
Correctness oracle for Part 1.

Compares the job's output against reference/expected_rollup.json:
  - row count
  - per-column checksum (order-independent)
  - full ordered digest

Exit 0 = pass. Any mismatch prints the offending column and exits 1.
"""
import json
import os
import sys

from pyspark.sql import functions as F

sys.path.insert(0, "/work")
from scripts.session import build  # noqa: E402

OUT = "/work/out/daily_rollup"
REF = os.path.join(os.path.dirname(__file__), "..", "reference", "expected_rollup.json")

NUMERIC = ["sessions", "page_views", "units_ordered",
           "ordered_revenue_cents", "distinct_items"]
KEYS = ["event_date", "category", "tier"]


def fingerprint(df):
    fp = {"row_count": df.count()}
    sums = df.agg(*[F.sum(c).alias(c) for c in NUMERIC]).collect()[0].asDict()
    fp["column_sums"] = {k: int(v) for k, v in sums.items()}
    fp["revenue_per_session_sum"] = round(
        float(df.agg(F.sum("revenue_per_session")).collect()[0][0]), 4)
    ordered = (df.orderBy(*KEYS)
                 .select(F.concat_ws("|", *KEYS, *NUMERIC).alias("r"))
                 .agg(F.md5(F.concat_ws("\n", F.collect_list("r"))).alias("d"))
                 .collect()[0]["d"])
    fp["ordered_digest"] = ordered
    return fp


def main():
    write_mode = "--write-reference" in sys.argv
    spark = build("verify")
    spark.sparkContext.setLogLevel("ERROR")
    got = fingerprint(spark.read.parquet(OUT))

    if write_mode:
        os.makedirs(os.path.dirname(REF), exist_ok=True)
        with open(REF, "w") as fh:
            json.dump(got, fh, indent=2, sort_keys=True)
        print("reference written:")
        print(json.dumps(got, indent=2, sort_keys=True))
        spark.stop()
        return 0

    with open(REF) as fh:
        want = json.load(fh)

    failures = []
    if got["row_count"] != want["row_count"]:
        failures.append(f"row_count: got {got['row_count']}, want {want['row_count']}")
    for col, val in want["column_sums"].items():
        if got["column_sums"].get(col) != val:
            failures.append(f"column_sums[{col}]: got {got['column_sums'].get(col)}, want {val}")
    if got["revenue_per_session_sum"] != want["revenue_per_session_sum"]:
        failures.append("revenue_per_session_sum: got "
                        f"{got['revenue_per_session_sum']}, want {want['revenue_per_session_sum']}")
    if got["ordered_digest"] != want["ordered_digest"]:
        failures.append("ordered_digest mismatch -- values or ordering differ")

    spark.stop()
    if failures:
        print("VERIFY FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print(f"VERIFY PASSED  ({got['row_count']} rows, digest {got['ordered_digest'][:12]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
