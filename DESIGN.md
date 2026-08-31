# Design (Part B)

Roughly a page of prose plus a diagram. Delete this scaffolding as you go.

---

## The situation

We pull sales-and-traffic data for tens of thousands of marketplace items
every day and land it in Redshift. Analysts and a customer-facing API both
read from that same cluster.

Three things are true:

1. **The upstream data is not final when it arrives.** Yesterday's numbers get
   restated for days afterwards. Some records arrive late. Some arrive twice.
   Occasionally a new field appears.
2. **The API has to stay fast.** It serves customers, and its latency budget
   is tens of milliseconds, not seconds.
3. **ETL and the API are fighting each other.** Heavy transform jobs hold
   locks on the cluster the API reads from. This has caused customer-visible
   timeouts more than once.

We want to move transforms onto files in S3 and keep the API fast. That's the
project. We have not decided how, and we are genuinely open to being told our
plan is wrong.

`data/drops/day_*.json` (created by `make setup`) is a representative sample
of what lands each day. Look at it before you design against it — the mess in
there is real, not decorative.

---

## 1. Your architecture

Diagram it. Any tool — draw.io, Excalidraw, Mermaid, a photo of paper. Commit
it to the repo as an image or `.md`, and reference it here.

Show: where raw data lands, where transforms run, what the API reads, and how
a restatement propagates through.

## 2. Failure modes, annotated on the diagram

Mark at least **three** places this breaks. For each, in one line: what breaks,
how you'd know, and what a client sees at 7am while it's broken.

This is the part we read most carefully. An architecture nobody has thought
about failing is a diagram, not a design.

## 3. Sequencing

We can't stop serving customers while this happens. How do you get from today
to your architecture without a big-bang cutover? What's the first thing you'd
ship, and what would you check before shipping the second?

## 4. The restatement merge — SQL sketch

Write the SQL (or Spark) that absorbs a restated record correctly. **It does
not need to run**, and you don't need our schema exactly right. We want to see
that you know what makes it correct — and what makes it wrong.

```sql
-- your sketch here
```

Then one line: what happens if this runs twice for the same day?

## 5. Detecting a silent 2% row loss

A transform quietly starts dropping 2% of rows. Nothing errors. How does
anyone find out before a client does?

---

## Your six decisions

Filled in separately in [`DECISIONS.md`](DECISIONS.md).
