---
name: data-time-machine
description: >-
  [WHAT IT DOES]: Orchestrates zero-downtime, zero-data-loss database schema migrations and data backfills
  using multi-phase dual-writing, adaptive replica throttling, and cryptographic Merkle-tree parity bisection.
  [WHEN TO USE]: Use when modifying live production database schemas, altering tables with >100k rows,
  splitting/merging high-traffic tables, migrating between SQL/NoSQL engines, or refactoring primary keys.
  [WHEN NOT TO USE]: Do NOT use for blank greenfield database initialization or local offline dev seed generation.
---

# Data Time-Machine: Zero-Downtime State & Schema Migration Engine

```
  +---------------------------------------------------------------------------------+
  |                               DATA TIME-MACHINE                                 |
  |             4-Phase Expand/Contract & Merkle Tree Parity Engine                 |
  +---------------------------------------------------------------------------------+

  [Live Traffic]
        |
        +-----------------------------------+
        |                                   |
        v                                   v
  +---------------+                 +--------------------+
  | Primary Writes|                 | Dual-Writes Shadow |
  | (Old Schema)  |                 | (New Schema)       |
  +---------------+                 +--------------------+
        |                                   |
        +-------------------+---------------+
                            |
                            v
             +------------------------------+
             | Adaptive Background Backfill |
             | (Replica Lag < 80ms Throttle)|
             +------------------------------+
                            |
                            v
             +------------------------------+
             | Merkle Tree Parity Bisection |
             | O(log N) Hash Tree Compare   |
             +------------------------------+
                            |
            +---------------+---------------+
            |                               |
       [Parity 100%]                  [Hash Divergence]
            |                               |
            v                               v
    [Atomic Cutover]              [Pinpoint Row Delta]
    - Reads -> New Schema         - Auto-Repair Corrupted Rows
    - Drop Old Columns
```

---

## 1. When to Activate

Trigger `data-time-machine` when:
- **Altering High-Volume Tables:** Adding columns, changing data types, or adding unique indexes to production tables where table locking causes downtime.
- **Architectural Normalization:** Splitting a monolithic table (e.g., `orders` $\to$ `orders` + `order_fulfillments`).
- **Engine / Cloud Migrations:** Moving data from self-hosted PostgreSQL to DynamoDB, MongoDB to Postgres, or Cloud SQL to Spanner.
- **Data Parity Auditing:** Proving that an active replica or backfilled cache is 100% synchronized with the primary database.

---

## 2. The 4-Phase Migration Lifecycle

### Phase 1: Expand (Dual-Writing)
1. Add target columns or shadow tables as backward-compatible structures.
2. Deploy application code that executes **Dual Writes** (writes to both old and new schema atomically via transaction or transactional outbox).
3. Confirm write error rate stays at $0.00\%$ over a multi-hour window.

### Phase 2: Idempotent Chunked Backfill
1. Run background batch jobs copying records in primary-key sorted chunks (e.g. 500 rows per batch).
2. Measure replication lag on read replicas continuously. If lag exceeds 80ms, pause backfill workers adaptively.
3. Use upsert semantics (`INSERT ... ON CONFLICT DO UPDATE`) to prevent overwriting newer dual-written updates.

### Phase 3: Merkle Tree Parity Bisection
1. Run `verify_merkle_sync.py`:
   ```bash
   python scripts/verify_merkle_sync.py --demo
   ```
2. The auditor constructs binary Merkle trees over both old and new datasets.
3. If roots match: Mathematical proof of $100.00\%$ data parity.
4. If roots differ: Recursively descends the tree in $O(\log N)$ steps to output the exact primary keys and data diffs.

### Phase 4: Contract (Cutover & Cleanup)
1. Switch application reads to the new schema.
2. Keep dual-writes active for a 24-hour observation buffer.
3. Disable writes to the legacy schema.
4. Safely drop obsolete legacy columns and tables.

---

## 3. Reference Files
- [verify_merkle_sync.py](./scripts/verify_merkle_sync.py): O(log N) cryptographic tree auditor.
- [migration_plan.md](./templates/migration_plan.md): Step-by-step production rollback and cutover checklist.
