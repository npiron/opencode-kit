# Memory Harness — 4-phase memory consolidation

Memory consolidation skill inspired by the KAIROS/autoDream architecture from Claude Code.
Implements a 3-layer memory system (L1/L2/L3) with asynchronous consolidation
and a concurrency lock.

## Architecture

```
L1 (preferences.md)     ← Timeless rules, always loaded
L2 (Knowledge Graph)     ← Structured facts, queryable
L3 (session archives)    ← Dated history, never read in full

.consolidate-lock        ← File mutex (lastConsolidatedAt timestamp)
```

## Consolidation thresholds

| Parameter | Value | Description |
|---|---|---|
| `minSessions` | 3 | Minimum number of sessions before fullCompact |
| `minHours` | 6 | Minimum elapsed time before fullCompact |
| `maxL1Lines` | 60 | L1 cleaned if exceeding this limit |

These thresholds are configurable within the skill context.

## Compaction levels

### microCompact (every session end)

Quick action, triggered automatically:
1. Add key decisions and new information to L2 (Knowledge Graph)
2. Create an L3 archive file: `memory/sessions/YYYY-MM-DD.md`
3. If an explicit preference is expressed: add it to L1 AND L2

### fullCompact (every `minSessions` sessions or `minHours` elapsed)

Complete consolidation in 4 phases:

---

## 4-phase consolidation prompt

When fullCompact conditions are met, execute this workflow:

### Phase 1 — ORIENT

Goal: Understand the current state of memory before modifying it.

```
1. Read L1 (agents/preferences.md) to understand the rules in effect
2. Open the Knowledge Graph (memory_open_nodes) on the main entities
3. List existing L3 archives (memory/sessions/)
4. Check .consolidate-lock to know lastConsolidatedAt
```

### Phase 2 — GATHER

Goal: Collect all new signals since the last consolidation.

```
1. Scan L3 archives created since lastConsolidatedAt
2. Identify in each archive:
   - Key decisions made
   - New entities/projects/technologies mentioned
   - Preferences or rules expressed by the user
   - Lessons learned (errors, corrections)
   - Recurring patterns
3. List L2 entities not updated for >30 days
```

### Phase 3 — CONSOLIDATE

Goal: Merge new signals into persistent memory.

```
FOR EACH affected entity:
  1. memory_open_nodes on the existing entity
  2. memory_add_observations to add new information
  3. If the entity does not exist: memory_create_entities

FOR EACH identified relation:
  1. memory_create_relations

MERGE duplicates:
  - Two entities with similar names → merge observations
  - Two identical observations → delete the duplicate via memory_delete_observations

UPDATE stale data:
  - Delete obsolete observations (memory_delete_observations)
  - Update entities whose status has changed
```

### Phase 4 — PRUNE & INDEX

Goal: Clean up and finalize.

```
1. CLEAN L1:
   - If preferences.md > maxL1Lines (60 lines):
     - Identify rules that have become obsolete
     - Delete or condense
     - Target: ~50 lines

2. UPDATE THE LOCK:
   - Write current timestamp to memory/.consolidate-lock
   - Format: ISO 8601 date

3. CREATE THE CONSOLIDATION ARCHIVE:
   - File: memory/sessions/YYYY-MM-DD-consolidation.md
   - Content: summary of changes made

4. VERIFY:
   - memory_read_graph to confirm final state
   - Ensure no data was lost
```

---

## ConsolidationLock

### File format

```
/Users/$USER/.config/opencode/memory/.consolidate-lock
```

Contains a single line: the ISO 8601 timestamp of the last consolidation.

```
2026-07-08T14:30:00Z
```

### Acquisition rules

1. **Before consolidating**: verify the lock is not already held
2. **Stale lock**: if the timestamp is >1h, the lock is considered expired
3. **After consolidation**: update the timestamp
4. **On failure**: do not modify the lock (implicit rollback)

---

## "Skeptical memory" rule

> Memory is a hint, not a truth. Always verify the actual code before acting.

In practice:
- Before exploring a known project: `memory_open_nodes` on the entity **then** explore the code
- If memory contradicts code: code is right, update memory
- L3 transcripts are never read in full, only searched by keywords
- The agent treats its own memory as a "hint" — it must verify

---

## Periodic maintenance

Every 10 sessions or 30 days (whichever comes first):
1. List all L2 entities
2. Identify entities untouched for >30 days
3. Propose to the user to archive or delete them
4. Verify relation consistency (orphans, circularities)
