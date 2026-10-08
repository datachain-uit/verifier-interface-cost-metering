# Harness v2 self-test (full-campaign H-freeze) — TOOLING CHECK, NOT EVIDENCE

Harness v2 = the frozen pilot harness plus only frozen full-protocol features: the priority-fee robustness route
(16 §1.4), a `cell_id` field in every record, cell-id matching in the validator, and manifest parameters for the cell
file and key-regeneration file. EraVM protocol 27 and FFLONK paths already existed and were exercised here.

Fixtures: P0 feasibility circuits only (`ctx_d11_k4`, `v1_d11`, `a4_d11`, depth-0 FFLONK `mini_d0_k4`), P0 proofs
repeated to fill j0..j7. Cells: EraVM v27 (G16, PLONK), ZKsync OS v32.0 npg 100 + priority fee 1e8 (PLONK k = 1),
FFLONK in EVM Osaka / EraVM v29 / ZKsync OS v32.0, EVM Osaka G16 (regression against the pilot self-test: identical).
Validator: 0 issues. Frozen scorer accounting: 247 checks; the only 16 non-passes are AC-ZK-gas-rule "NO-EDR-PAIR" for
the priority-fee fixture cell, because this self-test contains no EVM cell for that fixture (expected; in registered
scoring the pilot EVM k = 1 cells provide the pair). FFLONK structural counts (5 / 7 / 1 pairing) and transcript rounds passed.
No registered circuit, key, proof or measurement was used.
