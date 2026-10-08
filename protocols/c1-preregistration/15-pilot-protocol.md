# 15 — Registered pilot protocol (V2-C1, frozen; NOT run in C1)

## 1. Scope (owner-amended)

| Part | Cells | Proofs |
|---|---|---|
| CORE pilot grid | k ∈ {1, 2, 4, 16} × {Groth16, PLONK} × {EVM Osaka, EraVM v29, ZKsync OS v32.0 @ npg 100} = **24 cells** | j = 0…7 each |
| Intervention | ZKsync OS v32.0, k = 1, every level of `09-numeric-predictions/zkos_npg_levels.csv` for k = 1 other than 100, × 2 templates | j = 0…7 each |

Roles in the pilot: k = 1 and k = 4 are CALIBRATION (EVM, EraVM); k = 1 is CALIBRATION for ZKsync OS (base, c);
k = 2 and k = 16 are HELD-OUT (seen-in-P0). The pilot therefore tests H1, H2 (signs at 1, 2, 4, 16; crossover
brackets where they fall in the pilot grid), H3, H4 (ZKsync OS k = 2, 4, 16), H5 (k = 1 levels). It cannot alone
establish a Level-4 claim (`13-…` §8).

## 2. Steps

| Step | Action | Gate |
|---|---|---|
| 0 | **H-freeze:** finalise the registered harness (`04-…` §Harness), hash it, run its self-test on P0 circuits (tooling check, not evidence); write `RUN-MANIFEST-PILOT.json` with pins, harness hash, C1 package `SHA256SUMS` hash | Owner sees the manifest; any hash mismatch with this package → stop |
| 1 | Verify the C1 package against `SHA256SUMS`; verify corpus files against `corpus/CORPUS-SHA256SUMS`; regenerate PLONK zkeys and compare sha256 with `circuits/CIRCUITS.csv` | all equal |
| 2 | Run the 24 CORE cells in the deterministic order of `03-…` §5, each on a fresh node; EDR traces for every direct call | per-cell controls pass |
| 3 | Run the k = 1 intervention levels (fresh ZKsync OS node per level; same bytecode, same corpus) | |
| 4 | Freeze evidence: JSONL + raw logs + manifest; sha256 list; record in `V2-experiment-evidence-registry.md` | owner records |
| 5 | Score with `scoring/score_c1.py` against `09-numeric-predictions/` (unaltered); output `pilot-scoring/` | scorer hash = package hash |
| 6 | Pilot report: accounting, explanatory, predictive results kept separate; deviations listed | — |
| 7 | **Go / no-go for the full factorial** (owner) | see §3 |

## 3. Go / no-go rule (fixed now)

Proceed to the full factorial if and only if:
1. every accounting identity and control passes, or each failure has an adjudicated deviation record that names an
   infrastructure cause fixed without touching models, predictions or criteria;
2. no unresolved D-ACCEPT, D-HASH or D-REJECT;
3. the ZKsync OS version stamp and meters are as in the smoke check.

Predictive or explanatory failures in the pilot do **not** stop the full factorial and do **not** permit changes to
the model, tolerances or cell roles. They are reported as pilot results.

## 4. What the pilot must not do

- No re-generation of proofs, keys or predictions.
- No inspection-driven change of cell roles, grid, npg levels or criteria.
- No additional cells beyond §1 (anything else is the full factorial).
- No manuscript edits.
