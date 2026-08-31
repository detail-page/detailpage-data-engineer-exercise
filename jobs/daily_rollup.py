"""
Daily brand-category rollup.

This job is CORRECT and SLOW. Your task is to make it fast while keeping the
output identical -- `make verify` checks row counts, per-column sums and an
ordered digest against a committed reference.

Read it carefully before changing anything. Some of what makes it slow is
visible in the code; some of it only shows up once you look at the physical
plan or the Spark UI (http://localhost:4040 while a job is running).

Run:   make rollup
Check: make verify
"""
import sys
import time

from pyspark.sql import functions as F
from pyspark.sql.types import StringType

sys.path.insert(0, "/work")
from scripts.session import build  # noqa: E402

FACT = "/work/data/generated/fact_sales"
DIM = "/work/data/generated/dim_brand"
OUT = "/work/out/daily_rollup"

TARGET_TIERS = ["enterprise", "mid_market"]


def iso_month(d):
    """First of the month for an ISO date string."""
    if d is None:
        return None
    return d[:7] + "-01"


def main():
    spark = build("daily_rollup")
    spark.sparkContext.setLogLevel("WARN")

    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)

    started = time.time()

    fact = spark.read.parquet(FACT)
    dim = spark.read.parquet(DIM)

    month_udf = F.udf(iso_month, StringType())

    joined = (
        fact.join(dim, on="brand_id", how="inner")
            .withColumn("month", month_udf(F.col("event_date")))
            .where(F.col("tier").isin(TARGET_TIERS))
    )

    months = [r["month"] for r in
              joined.select("month").distinct().orderBy("month").collect()]
    print(f"months to process : {len(months)}")

    parts = []
    for m in months:
        chunk = joined.where(F.col("month") == m)
        if chunk.count() == 0:
            continue
        parts.append(
            chunk.groupBy("event_date", "month", "category", "tier")
               .agg(
                   F.sum("sessions").alias("sessions"),
                   F.sum("page_views").alias("page_views"),
                   F.sum("units_ordered").alias("units_ordered"),
                   F.sum("ordered_revenue_cents").alias("ordered_revenue_cents"),
                   F.countDistinct("item_id").alias("distinct_items"),
               )
        )

    result = parts[0]
    for extra in parts[1:]:
        result = result.unionByName(extra)

    result = result.withColumn(
        "revenue_per_session",
        F.when(F.col("sessions") > 0,
               F.round(F.col("ordered_revenue_cents") / F.col("sessions"), 4))
        .otherwise(F.lit(0.0)),
    )

    result.orderBy("event_date", "category", "tier") \
          .repartition(1) \
          .write.mode("overwrite").parquet(OUT)

    print(f"elapsed          : {time.time() - started:.1f}s")
    spark.stop()


if __name__ == "__main__":
    main()
