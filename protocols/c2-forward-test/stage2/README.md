# V2-C2 stage 2 — structural derivation and numeric FFLONK predictions (frozen before any FFLONK measurement)

Stage-1 package: `research/csi/protocols/v2/V2-C2-fflonk-forward-test/` (`SHA256SUMS`
`dfea3a87a775c067ffaa250d05771fb065d32e6a779063eb43eb1561cc626652`, frozen 2026-10-05T01:49:18Z), unchanged.
This directory is the stage-2 record required by stage-1 `04` S2.5. It was produced with the stage-1 code only; no term,
constant, τ or rule was changed, nothing was fitted to FFLONK, and no FFLONK EVM gas, EraVM or ZKsync OS value
(d = 11, P0 depth 0 or self-test) was read, computed or printed. No registered FFLONK cell had run when this directory
was frozen (freeze time: `FROZEN-UTC.txt`, written on the Mac after the hash check; it is not inside `SHA256SUMS`).

Model: source-augmented ZKsync OS native-cost model (extended transaction-level accounting), C2-SA —
N̂ = OPS + PRE + KEC + COP + CDT + DEC + HEAPB + HEAPE + CALL + C_env, C_env = 1,669,012 (calibrated on Groth16 / PLONK
only; not decomposed from source; the model is not "source-complete"). τ_C2 = 0.000138 is the predeclared precision /
acceptance threshold per proof; it is not a confidence interval.

## Chronology (UTC, 2026-10-05)

| Time | Event |
|---|---|
| 04:28:07 | fresh workstation precheck (GO) |
| 04:28:27–04:43:43 | local power-19 research PTAU (AMD-FF-1, DEV-FF-PTAU-1); `verify` PASS (G1 fallback) |
| 04:49:42–05:13:23 | FFLONK setup c1_ff_k01/k04/k16/k32 + 32 untimed validation proofs (G2) |
| ~05:14–05:16 | transfer (71 files, 0 bad), compile (registered pipeline), cloud off-chain verification 32/32 (G3) |
| 05:16:58 | AMD-FF-1 recorded |
| 05:17:10–05:17:21 | S2.2 structural derivation (`c2_structural.js`, EDR osaka), run once, no rerun |
| after 05:17:21 | S2.3 gates + S2.4 predictions (`c2_predict.py`), gates passed |
| `FROZEN-UTC.txt` | stage 2 frozen; only afterwards the registered FFLONK cells may start |

## Contents

| File | Content |
|---|---|
| `C2-STAGE2-MANIFEST.json` | 32 entries, proof_id `c1_ff_kNN/fflonk/jJ` (= the registered harness id `${circuit}/${backend}/j${j}`), compiled artifact `<circuit>-fflonk.json`, corpus proof file. Same circuits, k, j0…j7 and files as the 12 registered FFLONK cells (`design-cells.csv`, campaign `FULL-IF-FFLONK-GATE-PASSES`); no difference except absolute paths |
| `fflonk-structural.jsonl` | 32 structural records (no gas, gasUsed or gasCost field) |
| `C2-STAGE2-PREDICTIONS.json` / `.csv` | per-proof N̂, [N̂(1 − τ), N̂(1 + τ)], term ledger; per-k summaries; ranking vs registered Groth16 / PLONK ZKsync OS cell means; sign sequences and crossover |
| `ARTIFACT-HASHES.txt` | stage-1, C1, AMD-FF-1, PTAU, transfer, zkey / vkey / verifier, compiled artifacts, 32 proof files, code, calibration, comparator records |
| `TOOL-VERSIONS.txt` | node, hardhat, EDR, python, solc, zksolc, snarkjs |
| `run/` | structural run start / end, stdout of both steps, note on the move of the prediction files |

## Stage-1 structural expectations (checked, not scored)

5 ecMul + 7 ecAdd + 1 pairing call with 2 pairs (13 precompile calls): all 32 proofs. Calldata 772 + 32k bytes:
804 / 900 / 1,284 / 1,796 for k = 1 / 4 / 16 / 32 — all match. No EXP: confirmed. One CALLDATACOPY: confirmed.
All 32 records status 1, `verifyProof` true; no unknown opcode or term.

## Frozen predictions

Per-proof N̂ is identical for the 8 proofs of each k (the verifier's structure does not depend on the proof values).

| k | OPS | PRE | KEC | COP | CDT | DEC | HEAP (B + E) | CALL | C_env | **N̂** | τ·N̂ | heap events | verifier bytes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1,587,608 | 24,521,000 | 40,364 | 72,464 | 48,240 | 87,320 | 3,207 | 54,640 | 1,669,012 | **28,083,855** | 3,875.6 | 13 | 14,349 |
| 4 | 1,687,594 | 24,521,000 | 40,364 | 78,080 | 54,000 | 93,100 | 3,609 | 54,640 | 1,669,012 | **28,201,399** | 3,891.8 | 19 | 15,311 |
| 16 | 2,069,018 | 24,521,000 | 51,902 | 98,816 | 77,040 | 114,520 | 5,042 | 54,640 | 1,669,012 | **28,660,990** | 3,955.2 | 38 | 18,927 |
| 32 | 2,577,690 | 24,521,000 | 67,286 | 126,464 | 107,760 | 143,420 | 6,626 | 54,640 | 1,669,012 | **29,273,898** | 4,039.8 | 54 | 23,759 |

Ranking (FFLONK predicted mean − registered comparator mean; determinate if |difference| > τ·N̂_F + half-range of the
comparator cell):

| k | vs Groth16 (band) | vs PLONK (band) |
|---|---|---|
| 1 | −8,423,010 (3,875.6) FFLONK lower | −10,583,101.25 (46,348.6) FFLONK lower |
| 4 | −10,983,904 (3,891.8) FFLONK lower | −10,578,224.75 (35,420.8) FFLONK lower |
| 16 | −21,229,955 (3,955.2) FFLONK lower | −10,599,918.25 (34,051.2) FFLONK lower |
| 32 | −34,893,343 (4,039.8) FFLONK lower | −10,611,171 (47,815.8) FFLONK lower |

All 8 comparisons determinate. Sign sequence over k ∈ {1, 4, 16, 32}: FFLONK lower at every k for both comparators;
predicted crossover: none within the grid (Groth16 and PLONK).

## Scoring (stage 4, later)

`python3 code/c2_score.py <this directory> fflonk-structural.jsonl <pilot> <full> <fflonk records> --out <dir>`; the
scorer re-verifies `SHA256SUMS` of this directory. Predictions are never recomputed after a FFLONK measurement
(stage-1 `08` §2).
