# 20 — Deviations policy (V2-C1, frozen)

**Principle:** nothing is excluded silently. Every departure from the protocol produces a deviation record before
analysis continues; the record is adjudicated (by the owner for classes marked ★) and its consequence is applied by
rule, not by looking at whether the affected numbers help or hurt a hypothesis.

## 1. Record

`deviations/DEV-<campaign>-<nnn>.md` with: id; UTC; run_id; cells / proof IDs / records affected; class; observation
(verbatim error, log excerpt with log sha256); immediate action taken; proposed consequence; adjudication (who, when,
decision); link from every affected evidence record (`deviation_ref`). Deviation records are append-only.

## 2. Classes and pre-registered consequences

| Class | Trigger | Immediate action | Consequence for scoring |
|---|---|---|---|
| **D-CRASH** node crash / hang | node process exits or stops answering | stop the run; keep logs; restart the **whole cell** on a fresh node | partial records of the aborted attempt are kept (role unchanged, flagged); the cell's scored values come from the first complete attempt; ≥ 3 aborted attempts on one cell → ★ |
| **D-DEPLOY** deploy failure | deploy reverts or out-of-gas, or bytecode hash ≠ manifest | stop the cell; check pins | no measurement possible; if reproducible ★ (cell recorded as MISSING; it is never replaced by another configuration) |
| **D-PROOFGEN** proof-generation failure | (corpus is frozen before the pilot) any missing / unreadable proof file | stop | ★; a regenerated proof gets a new ID suffix `-r1` and is reported as such |
| **D-REJECT** unexpected reject | a valid corpus proof returns `false` / reverts | continue the cell; record | ★; the cell is excluded from predictive scoring **and** reported as a failure of the corpus or the harness, never treated as a measurement outlier |
| **D-ACCEPT** unexpected accept | any negative control returns `true` | stop the campaign | ★; blocks all predictive scoring of that regime until resolved; reported |
| **D-NATIVE** missing native / pubdata field | ZKsync OS DEBUG line absent or unparsable | rerun the cell once on a fresh node | if still missing: N_dir MISSING for those proofs; gas remains scored; ★ if > 1 cell |
| **D-HASH** version or hash mismatch | any pinned binary, config, key, verifier or proof hash differs | stop | ★; records produced under the mismatch are retained but marked and excluded from scoring; the cell is rerun under the pins |
| **D-INT** interruption | host sleep, network loss, manual stop | rerun the cell from its start on a fresh node | first complete attempt is scored; interrupted partial attempt kept and flagged |
| **D-DUP** duplication | a cell or proof measured twice (operator error) | none | the **first** complete measurement in pre-registered order is scored; later duplicates are kept as replays (role `replay`) |
| **D-CTRL** control outcome other than expected (except D-ACCEPT) | e.g. replay cost differs, version stamp mismatch | stop the cell | ★ |
| **D-PROTO** any other departure from the written protocol | — | record | ★ |

## 3. Rules that hold for every class

1. **No outcome-based exclusion.** A record is never removed because its value is unexpected. Only the classes above
   change what is scored, and only by their pre-registered rule.
2. **No migration after inspection.** No cell moves between CALIBRATION, HELD-OUT, SEMANTIC or VALIDATION after any
   registered value has been seen (`08-…`).
3. **No model change after inspection.** Equations, tolerances, criteria and prediction files are frozen by hash. A
   proposed change after data exist is reported as a *post-hoc* analysis next to the pre-registered one, never instead.
4. **Amendments before data:** a change made before any registered measurement it affects is an amendment record
   (`AMD-<nnn>`) with new hashes; the frozen originals stay in place.
5. **Missing cells are reported as missing**, with their deviation ids, in every results table.
6. The owner performs all Git/GitHub state changes; deviation and amendment records are files in the V2 workspace.
