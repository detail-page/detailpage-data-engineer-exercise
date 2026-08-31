# Decisions (Part B)

Six decisions. **Any defensible answer passes. Leaving one blank does not.**

We are not looking for the answer we would have given — we are looking for
evidence you considered the alternative and had a reason. Two or three
sentences each is plenty. If a decision depends on something you'd need to
measure first, say what you'd measure.

---

### 1. Table format for the lake

Iceberg? Delta? Plain Parquet plus a catalog? Something else?

**Choice:**

**Why, and what you rejected:**

---

### 2. Partition key and grain

What do you partition on — and, just as importantly, **what did you refuse to
partition on and why?**

**Choice:**

**Why, and what you rejected:**

---

### 3. Restatement strategy

Yesterday's numbers get revised days later. How does the table absorb that?
Merge/upsert? Replace the whole partition? Keep history with SCD2? Append and
deduplicate at read time?

**Choice:**

**Why, and what you rejected:**

---

### 4. Where the transform runs

In the warehouse (SQL against Redshift) or in the lake (Spark against files)?
You may split it — if you do, say where the line is.

**Choice:**

**Why, and what you rejected:**

---

### 5. What stays in Redshift

A customer-facing API reads from Redshift today and needs to stay fast. What,
if anything, remains in the warehouse after this migration?

**Choice:**

**Why, and what you rejected:**

---

### 6. File sizing and compaction

Daily per-item, per-marketplace writes. What do you do about the resulting
file count, and when?

**Choice:**

**Why, and what you rejected:**
