# Decisions (Part B)

Six calls we'd like your read on. There's no answer key — we're interested in
what you'd pick and what you'd rule out, not whether you match us.

A couple of sentences each is fine. If something depends on a number you'd
want to measure first, say what you'd measure.

---

### 1. Table format for the lake

Iceberg? Delta? Plain Parquet plus a catalog? Something else?

**Choice:**

**Reasoning, and what you'd rule out:**

---

### 2. Partition key and grain

What you'd partition on — and anything you'd deliberately avoid partitioning
on.

**Choice:**

**Reasoning, and what you'd rule out:**

---

### 3. Restatements

Yesterday's numbers get revised days later. How does the table absorb that?
Merge/upsert, replace the partition, keep history with SCD2, dedupe at read
time?

**Choice:**

**Reasoning, and what you'd rule out:**

---

### 4. Where the transform runs

In the warehouse, in the lake, or split between them? If you'd split it, where
does the line fall?

**Choice:**

**Reasoning, and what you'd rule out:**

---

### 5. What stays in Redshift

A customer-facing API reads from Redshift today and needs to stay fast. What,
if anything, stays put?

**Choice:**

**Reasoning, and what you'd rule out:**

---

### 6. File sizing and compaction

Daily per-item, per-marketplace writes. What do you do about the file count,
and when?

**Choice:**

**Reasoning, and what you'd rule out:**
