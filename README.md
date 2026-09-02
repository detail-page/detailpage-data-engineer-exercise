# Data Engineer II — take-home exercise

Three parts, roughly three hours. It's drawn from the first real project for
this role: moving our Redshift ETL onto files in S3 without breaking the API
that reads from it.

Everything runs in one Docker container locally. No AWS account, nothing to
sign up for.

---

## Before you start

**Use AI however you normally would** — Cursor, Claude Code, Copilot, any of
it. We use these tools heavily and would find it odd if you didn't. The only
thing we'd ask is that you can talk through your choices in Part C, because
that conversation is the useful part for both of us.

**Part B has no correct answer.** Several of the decisions we ask about are
ones we haven't settled internally. If you think our plan is wrong, say so —
that's a more interesting submission than one that agrees with us.

Three hours is our estimate of a reasonable effort, not a stopwatch. Spend
what the problem's worth to you.

---

## Setup

Docker with Compose. About a minute of data generation.

```bash
make setup
make rollup     # runs the Part A job
make verify     # checks the output still matches
```

`make help` lists the rest. `make clean` tears it down.

The data is synthetic, generated from a fixed seed in
`scripts/generate_data.py`. None of it comes from production or any
marketplace API.

---

## Part A — Make a slow job fast

`jobs/daily_rollup.py` produces a correct daily rollup of sessions, page
views, units and revenue by date, category and tier. It's a good deal slower
than it needs to be, for several different reasons.

Make it faster, and keep the output the same. `make verify` compares row
counts, per-column sums and an ordered digest against a committed fingerprint,
so you can check yourself as you go.

Worth including in your notes: your before/after timings, and a line on each
change explaining what was actually slow. The reasoning is what we read.

The Spark UI is on http://localhost:4040 while a job runs, and `.explain()`
will show you the physical plan.

> **Why we ask:** most of this job is making existing pipelines faster.
> Reading someone else's slow code is closer to the day-to-day than writing
> new code from scratch.

---

## Part B — Design the migration

This is the part we're most interested in.

The brief is in **[`DESIGN.md`](DESIGN.md)**: daily marketplace data that gets
restated after the fact, an API with a tight latency budget, and ETL that
currently competes with that API for the same cluster.

We're after a diagram, a sense of where it breaks, how you'd sequence the
migration without a hard cutover, and a SQL sketch for absorbing a restated
record. Nothing needs to run.

Six decisions go in **[`DECISIONS.md`](DECISIONS.md)** — the ones where we
genuinely want to know what you'd pick and what you'd rule out.

`make drops` shows what the daily data actually looks like. It's messy on
purpose — restatements, late arrivals, duplicates, a column that turns up
partway through, and one marketplace carrying most of the volume.

> **Why we ask:** we're making this call right now, and we'd rather hire
> someone whose reasoning we can follow than someone who picked the same
> tools we did.

---

## Part C — Walk us through it

Record a short screen share — ten minutes is plenty. Talk through Part A,
your diagram and a couple of the decisions you found hardest, and where you'd
take it next.

No need to script or re-record. We'd rather hear you think than watch a
polished demo.

Loom, a plain screen recording, an unlisted YouTube link — whatever's easy.
Drop the link in your README.

---

## What to send

A repo or a zip, with commit history if you used git. Alongside the code:

- Your Part A timings and what you changed
- `DESIGN.md` and `DECISIONS.md`
- Your diagram
- The recording link

Anything you tried that didn't work is genuinely interesting to us, if you
feel like including it.

**Not needed:** AWS deployment, CI, a UI, Terraform or CDK, or test coverage
beyond whatever you find useful. Part B doesn't need working code.

---

## Layout

```
jobs/daily_rollup.py       Part A — the slow job
DESIGN.md                  Part B — the brief and your write-up
DECISIONS.md               Part B — your six decisions
scripts/generate_data.py   synthetic data generator
scripts/session.py         shared Spark session
scripts/verify.py          Part A output check
reference/                 expected Part A fingerprint
tests/                     a couple of example tests
```

Anything unclear, just ask.
