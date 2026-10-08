# 07 — Relation to C1 / H8 (two separate evaluations)

| | C1 / H8 | C2 |
|---|---|---|
| Registered | 2026-10-04 09:01, before any V2 measurement (C1 `SHA256SUMS` `7dac8482…bfc8f`) | 2026-10-05 (`FROZEN-UTC.txt`), **after** the Groth16 / PLONK pilot and FULL campaigns, F4 and the M7A / M7B-A audits; **before any d = 11 FFLONK evidence** |
| Model | frozen C1 trace model: T(trace) + base + c · ncalls (procedure R: base, c from the registered k = 1 Groth16 / PLONK cells) | C2-SA: source terms 1–9 + C_env (`02`) |
| Inputs | registered FFLONK EVM trace of the same proof | stage-2 structural record of the same proof (equal to the registered trace by the consistency gate), verifier length, calldata length |
| Tolerance | τ_cond(F) = 0.569 % | τ_C2 = 0.0138 % (+ exactness) |
| Scorer | frozen `scoring/score_c1.py`, unchanged | `code/c2_score.py` |
| Status if FFLONK runs | scored exactly as registered; F8 as defined in C1 | scored per `06` |

Rules: the two scores are never merged, averaged or used to re-interpret each other. H8 stays "the original registered
FFLONK validation". C2 is described as "a post-F4 test, prospectively registered before any FFLONK evidence"; it is never
described as pre-registered before the Groth16 / PLONK campaigns. A C2 PASS does not repair F4; a C2 FAIL does not
change H8. Manuscript wording is decided only in V2-M8.
