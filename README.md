# Data Engineer II — take-home exercise

Three parts, about **three hours** total. Built from the role's actual first
project: moving Redshift ETL onto files in S3 without breaking the API that
reads from it.

Runs entirely in one Docker container on your laptop. **No AWS account, no
cloud spend, no access requests, nothing to sign up for.**

| | | |
|---|---|---|
| **Part A** | ~45 min | Make a slow Spark job fast. Correctness is checked automatically |
| **Part B** | ~90 min | Design the migration: a diagram, six decisions, a SQL sketch |
| **Part C** | ≤8 min | Record a Loom walking us through what you did and why |

---

## Ground rules

**Three hours.** If you run out, stop and write down what you'd have done
next — that gets read. An honest "here's where I stopped" scores better than a
rushed submission you never ran.

**Use AI freely.** Cursor, Claude Code, Copilot, whatever you normally use. We
use these tools heavily ourselves and we'd think it strange if you didn't.

One condition, and it's the whole deal: **in your Loom, explain why you made
each choice and what you rejected.** We don't care who typed it. We care
whether you can defend it. A submission whose author can't explain a decision
tells us less than one that's half-finished but understood.

**Part B has no right answer.** Several of the decisions we ask about are ones
we haven't settled internally. We'd rather hear you disagree with our plan for
a good reason than agree with it for none.

---

## Setup

Docker with Compose. One container, roughly 2GB of image, about a minute of
data generation.

```bash
make setup      # build, start, generate the dataset
make rollup     # run the Part A job -- time your baseline
make verify     # confirm the output is still correct
```

`make help` lists everything. `make clean` removes it all.

All data is synthetic, generated from a fixed seed in
`scripts/generate_data.py`. Nothing here comes from production or from any
marketplace API.

---

## Part A — Make a slow job fast (~45 min)

`jobs/daily_rollup.py` produces a correct daily rollup of sessions, page
views, units and revenue by date, category and tier. It is much slower than it
needs to be.

Make it fast.

- **Output must stay identical.** `make verify` checks the row count,
  per-column sums, and an ordered digest against
  `reference/expected_rollup.json`. If it fails, the submission fails —
  speed without correctness is worth nothing.
- **Record your own before/after times.** Absolute numbers depend on your
  machine, so measure your baseline first. We're looking at the ratio and at
  whether you can explain it.
- For **each** change, a sentence or two on what was slow and why your fix
  helps.

There are seven distinct problems. **Five found with clear explanations beats
seven found with none.**

The Spark UI is at http://localhost:4040 while a job runs. `.explain()` shows
you the physical plan.

> **Why we ask:** optimizing existing pipelines is the bulk of this job.
> Diagnosing someone else's slow code matters more to us than authoring new
> code from scratch.

---

## Part B — Design the migration (~90 min)

This is the part we weight most heavily.

The brief is in **[`DESIGN.md`](DESIGN.md)** — a real, unresolved problem:
daily marketplace data that gets restated after the fact, an API that has to
stay fast, and ETL currently fighting that API for the same cluster.

You'll produce:

- **An architecture diagram.** Any tool. Commit it.
- **Three failure modes annotated on it** — what breaks, how you'd know, what
  a client sees at 7am while it's broken.
- **A sequencing plan** to get there without a big-bang cutover.
- **A SQL sketch** for absorbing a restated record. It does not need to run.
- **Six decisions**, recorded in **[`DECISIONS.md`](DECISIONS.md)**.

Run `make drops` to see what the daily data actually looks like. It's messy on
purpose — restatements, late arrivals, duplicates, a column that appears
partway through, and one marketplace carrying most of the volume. Design
against what's there, not against a clean version of it.

No code has to run in Part B. No AWS, no Terraform, no deployment.

> **Why we ask:** we're making this decision right now, and the reasoning
> matters more than the diagram. This is also the part we can't train quickly.

---

## Part C — Record a Loom (≤8 min)

Walk us through your submission. Screen share, talk over it.

Cover:

1. **Part A** — what was slow, what you changed, your before/after numbers.
2. **Your diagram** — the shape of it, and one failure mode you're worried
   about.
3. **Two of your six decisions** — your pick, ideally the two you found
   hardest. Why this choice, what you rejected.
4. **What you'd do with another week.**

**Eight minutes is a cap, and keeping to it is part of what we're assessing.**
Being able to explain a technical decision concisely to someone who wasn't
there is most of this job. Don't script it or re-record for polish — we'd
rather hear you think.

Any recorder is fine (Loom, a plain screen recording, an unlisted YouTube
link). Include the link in your README.

---

## What to send back

- A git repo or zip — **with your commit history**, if you used git.
- `README.md` — your before/after timings, your Part A changes with reasoning,
  the Loom link, and what you'd do with another four hours.
- `DESIGN.md` and `DECISIONS.md`, filled in.
- Your diagram, committed.
- Anything you tried that **didn't** work. Genuinely useful, not a trap.

### Explicitly not required

No AWS deployment. No CI. No dashboard or UI. No Terraform or CDK. No
exhaustive test coverage. No working code in Part B. If you find yourself
building any of these, stop — you've left the exercise.

---

## Layout

```
jobs/daily_rollup.py       Part A -- the slow job (edit this)
DESIGN.md                  Part B -- the brief and your write-up
DECISIONS.md               Part B -- your six decisions
scripts/generate_data.py   synthetic data generator
scripts/session.py         shared Spark session
scripts/verify.py          Part A correctness oracle (don't edit)
reference/                 expected Part A fingerprint
tests/                     example tests -- add your own if useful
```

Questions about the exercise are welcome and won't count against you. Ask.
