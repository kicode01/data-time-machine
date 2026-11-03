# Zero-Downtime Migration Execution Plan

## 1. Migration Metadata
- **Target Table(s):**
- **Estimated Row Count:**
- **Source Database / Engine:**
- **Target Database / Engine:**
- **Primary Key Identifier:**

---

## 2. Phase 1: Expand (Dual-Writing)
- [ ] Deploy backward-compatible schema changes (Nullable columns / shadow tables).
- [ ] Deploy application code writing to both Old and New locations.
- [ ] Confirm write error rate = 0% across 6 hours.

---

## 3. Phase 2: Backfill
- **Chunk Size:** 500 records
- **Throttle Metric:** Replica Lag threshold <= 80ms
- **Script:**
- [ ] Run initial backfill pass.
- [ ] Run delta-sweep pass for modified records during backfill.

---

## 4. Phase 3: Parity & Consistency Audit
- [ ] Execute `verify_merkle_sync.py` across all buckets.
- [ ] Verify 100.00% hash parity.
- [ ] Zero discrepancies detected.

---

## 5. Phase 4: Contract (Cutover & Cleanup)
- [ ] Switch active read traffic to New Schema.
- [ ] Keep dual-writes active for 24-hour safety buffer.
- [ ] Disable dual-write to Old Schema.
- [ ] Schedule drop of obsolete columns / tables.

---

## 6. Rollback Runbook
- Step 1: Flip feature flag `READ_SOURCE=LEGACY`.
- Step 2: Disable dual-write branch.
- Step 3: Purge shadow columns (no impact on live data).
