# Design (Part B)

A page or so of prose plus a diagram. Delete this scaffolding as you go.

---

## The situation

We pull sales-and-traffic data for tens of thousands of marketplace items
daily and land it in Redshift. Analysts and a customer-facing API both read
from that same cluster.

Three things are true:

1. **The upstream data isn't final when it arrives.** Yesterday's numbers get
   restated for days afterwards. Some records arrive late, some arrive twice,
   and occasionally a new field turns up.
2. **The API has a tight latency budget** — tens of milliseconds, not seconds.
3. **ETL and the API compete for the same cluster.** Heavy transforms hold
   locks on the cluster the API reads from, and that's caused customer-visible
   timeouts more than once.

We want to move transforms onto files in S3 and keep the API fast. We haven't
decided how, and we're open to being told our thinking is wrong.

`data/drops/day_*.json` (created by `make setup`) is representative of what
lands each day — worth a look before designing against it, since the mess in
there is real.

---

## 1. Your architecture

Diagram it however you like — draw.io, Excalidraw, Mermaid, a photo of paper.
Commit it and reference it here.

Where raw data lands, where transforms run, what the API reads, and how a
restatement propagates through.

## 2. Where it breaks

Mark a few places this falls over. For each: what breaks, how you'd find out,
and what a client sees while it's broken.

This is the part we read most closely.

## 3. Sequencing

We can't stop serving customers while this happens. How would you get from
today to your architecture? What ships first, and what would you want to see
before shipping the next thing?

## 4. The restatement merge

The SQL (or Spark) that absorbs a restated record correctly. It doesn't need
to run, and our exact schema isn't important — we're interested in what makes
it correct.

```sql
-- your sketch here
```

Then a line on what happens if it runs twice for the same day.

## 5. Catching a silent 2% row loss

A transform quietly starts dropping 2% of rows. Nothing errors. How does
anyone find out before a client does?

---

## Your six decisions

In [`DECISIONS.md`](DECISIONS.md).
