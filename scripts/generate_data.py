"""
Generate the synthetic dataset for the exercise.

Everything here is fabricated from a fixed seed. No production, client, or
marketplace-API data is used or reproduced.

Outputs (all local, created by `make setup`):
  data/generated/fact_sales/     parquet, ~2M rows
  data/generated/dim_brand/      parquet, 200 rows
  data/drops/day_{1..7}.json     daily JSON drops for Part 2
"""
import json
import os
import random
import shutil
from datetime import date, timedelta

SEED = 20260827
FACT_ROWS = 6_000_000
N_BRANDS = 200
N_ITEMS = 40_000
START = date(2026, 1, 1)
DAYS = 240

MARKETPLACES = ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2", "A1AM78C64UM0Y8",
                "A1F83G8C2ARO7P", "A1PA6795UKMFR9"]
# Deliberate skew: first marketplace is ~60% of rows.
MP_WEIGHTS = [0.60, 0.13, 0.11, 0.09, 0.07]

CATEGORIES = ["Grocery", "Home", "Beauty", "Pet Supplies", "Tools",
              "Electronics", "Sports", "Baby", "Office", "Automotive"]
TIERS = ["enterprise", "mid_market", "smb"]

OUT = os.path.join(os.path.dirname(__file__), "..", "data")


def _write_parquet(rows, schema, path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    table = pa.Table.from_pydict(
        {name: [r[i] for r in rows] for i, (name, _) in enumerate(schema)},
        schema=pa.schema([(n, t) for n, t in schema]),
    )
    os.makedirs(path, exist_ok=True)
    pq.write_table(table, os.path.join(path, "part-00000.parquet"))


def gen_dim(rng):
    import pyarrow as pa
    rows = []
    for bid in range(1, N_BRANDS + 1):
        rows.append((
            bid,
            f"Brand {bid:03d}",
            CATEGORIES[bid % len(CATEGORIES)],
            TIERS[bid % len(TIERS)],
            round(rng.uniform(0.05, 0.35), 4),
        ))
    _write_parquet(rows, [
        ("brand_id", pa.int32()),
        ("brand_name", pa.string()),
        ("category", pa.string()),
        ("tier", pa.string()),
        ("commission_rate", pa.float64()),
    ], os.path.join(OUT, "generated", "dim_brand"))
    return rows


def gen_fact(rng):
    """Written in chunks so peak memory stays flat regardless of FACT_ROWS."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    schema = pa.schema([
        ("event_date", pa.string()),
        ("marketplace_id", pa.string()),
        ("item_id", pa.string()),
        ("brand_id", pa.int32()),
        ("sessions", pa.int32()),
        ("page_views", pa.int32()),
        ("units_ordered", pa.int32()),
        ("ordered_revenue_cents", pa.int64()),
    ])
    path = os.path.join(OUT, "generated", "fact_sales")
    os.makedirs(path, exist_ok=True)

    chunk = 250_000
    written = 0
    writer = pq.ParquetWriter(os.path.join(path, "part-00000.parquet"), schema)
    try:
        while written < FACT_ROWS:
            n = min(chunk, FACT_ROWS - written)
            dates, mps, items, brands = [], [], [], []
            sess, views, units_l, rev = [], [], [], []
            for _ in range(n):
                d = START + timedelta(days=rng.randrange(DAYS))
                mp = rng.choices(MARKETPLACES, weights=MP_WEIGHTS, k=1)[0]
                sessions = rng.randint(0, 4000)
                units = int(sessions * rng.uniform(0.0, 0.09))
                dates.append(d.isoformat())
                mps.append(mp)
                items.append(f"ITEM{rng.randrange(N_ITEMS):06d}")
                brands.append(rng.randint(1, N_BRANDS))
                sess.append(sessions)
                views.append(sessions + rng.randint(0, 2500))
                units_l.append(units)
                rev.append(units * rng.randint(499, 12999))
            writer.write_table(pa.Table.from_pydict({
                "event_date": dates, "marketplace_id": mps, "item_id": items,
                "brand_id": brands, "sessions": sess, "page_views": views,
                "units_ordered": units_l, "ordered_revenue_cents": rev,
            }, schema=schema))
            written += n
            print(f"  fact_sales   : {written:,}/{FACT_ROWS:,}", end="\r", flush=True)
    finally:
        writer.close()
    print(" " * 40, end="\r")


def gen_drops(rng):
    """
    Seven daily drops with the warts named in the README:
      - restatements    day 6 revises metrics for day 2
      - late arrivals   day 6 carries day 2 rows
      - duplicates      exact dupes inside a single file
      - schema drift    buy_box_pct first appears in day 4
      - key skew        marketplace weighting above
    """
    base = date(2026, 8, 1)
    drops_dir = os.path.join(OUT, "drops")
    os.makedirs(drops_dir, exist_ok=True)

    day2_keys = []

    for day in range(1, 8):
        report_date = base + timedelta(days=day - 1)
        records = []

        for _ in range(4000):
            mp = rng.choices(MARKETPLACES, weights=MP_WEIGHTS, k=1)[0]
            item = f"ITEM{rng.randrange(N_ITEMS):06d}"
            rec = {
                "report_date": report_date.isoformat(),
                "marketplace_id": mp,
                "item_id": item,
                "sessions": rng.randint(0, 3000),
                "units_ordered": rng.randint(0, 200),
                "ordered_revenue_cents": rng.randint(0, 900000),
                "ingested_at": f"{report_date.isoformat()}T0{day}:15:00Z",
            }
            if day >= 4:
                rec["buy_box_pct"] = round(rng.uniform(0.0, 100.0), 2)
            records.append(rec)
            if day == 2:
                day2_keys.append((report_date.isoformat(), mp, item))

        # exact duplicates inside the file
        for _ in range(120):
            records.append(dict(rng.choice(records)))

        # day 6: late-arriving AND restated day-2 rows
        if day == 6 and day2_keys:
            for rd, mp, item in rng.sample(day2_keys, 350):
                records.append({
                    "report_date": rd,
                    "marketplace_id": mp,
                    "item_id": item,
                    "sessions": rng.randint(0, 3000),
                    "units_ordered": rng.randint(0, 200),
                    "ordered_revenue_cents": rng.randint(0, 900000),
                    "ingested_at": f"{(base + timedelta(days=5)).isoformat()}T06:15:00Z",
                    "buy_box_pct": round(rng.uniform(0.0, 100.0), 2),
                })

        rng.shuffle(records)
        with open(os.path.join(drops_dir, f"day_{day}.json"), "w") as fh:
            for rec in records:
                fh.write(json.dumps(rec) + "\n")


def main():
    rng = random.Random(SEED)
    gen = os.path.join(OUT, "generated")
    if os.path.isdir(gen):
        shutil.rmtree(gen)
    drops = os.path.join(OUT, "drops")
    if os.path.isdir(drops):
        shutil.rmtree(drops)

    gen_dim(rng)
    print("dim_brand      : 200 rows")
    gen_fact(rng)
    print(f"fact_sales     : {FACT_ROWS:,} rows")
    gen_drops(rng)
    print("drops          : day_1..day_7.json")


if __name__ == "__main__":
    main()
