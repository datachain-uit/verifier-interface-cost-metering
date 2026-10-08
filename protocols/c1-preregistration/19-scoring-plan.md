# 19 — Scoring plan (V2-C1, frozen)

**Code:** `scoring/score_c1.py` (+ `model/c1_model.py`, `model/zkos_native_trace_model.py`). Invocation:
`python3 scoring/score_c1.py 09-numeric-predictions <out_dir> <evidence.jsonl …>`. Python 3 standard library only.
The code was exercised on a mock built from P0 data (`test/p0_to_mock_evidence.py`; output is not evidence): it
reproduces the P0 v31 conditional-model constants exactly (base 1,868,919; c 8,655) and flags the P0 PLONK trace that
lacks a keccak profile through the transcript-rounds check.

## Sections (in order) and outputs

| Section | Output | Criterion (`13-…`) | Hypotheses |
|---|---|---|---|
| AC — accounting, structure, controls | `AC_checks.csv` | exact identities; ±1 gas for L1-ZK; control expectations | prerequisite for all |
| CELL — per-cell summaries (n, mean, min, max, half-range) | `CELL_summary.csv` | — | — |
| P — a-priori numeric predictions | `P_scoring.csv` | [lo, hi]; calibration cells reported as TRANSFER-CHECK; k = 64 DESCRIPTIVE | FP |
| R — registered-calibration procedure (refit A, B on registered k ∈ {1, 4}; v27 transfer with registered k = 1 frames) | `R_scoring.csv` | \|e\| ≤ τ | H1–H3, H7 |
| ZC — ZKsync OS conditional (base, c from registered k = 1 G16 + PLONK; per-proof prediction from the same proof's EDR trace) | `ZC_scoring.csv` | \|e\| ≤ τ_cond, no unpriced opcode | H4, H8 |
| SG — signs, ratio intervals, monotonicity | `SG_signs.csv`, `SG_monotonicity.csv` | §3 | H1, H2 |
| XO — crossovers | `XO_crossovers.csv` | §4 | H2, H3, H7 |
| NPG — meter, gas interval, ranking per level | `NPG_scoring.csv`, `NPG_ranking.csv` | §6 | H5 |
| SEM — semantic invariance | `SEM_scoring.csv` | §7 | H6 |
| summary | `summary.json` | counts per verdict | — |

## Reporting rules

1. Report accounting, explanatory and predictive results in separate tables; never combine them into one score.
2. Report P and R side by side for every held-out cell; report seen-in-P0 and strictly-unseen k separately.
3. Report every FAIL with its error; no pooled "average error" replaces a per-cell verdict.
4. Report every deviation and every MISSING cell in each table where the cell would appear.
5. Any analysis not in this plan is labelled **post hoc** and reported after the registered results.
6. EVM gas, EraVM computational gas and ZKsync OS gas/native are never put on one axis or in one unit.
