# Harness self-test (H-freeze, pilot step 0) — TOOLING CHECK, NOT EVIDENCE

Fixtures: P0 feasibility circuits only (`v1_d11` → fx_k01, `ctx_d11_k4` → fx_ctx_k04, `a4_d11` → fx_a4 for the foreign-key
control), P0 verifier sources and P0 synthetic proofs (2 per circuit, repeated to fill j0..j7). No registered circuit,
key, proof or measurement was used. Cells: `selftest-cells.csv` (EVM Osaka, EraVM v29, ZKsync OS v32.0 @ npg 100 and 300).

Results: two independent runs (run1, run2) gave identical records; the evidence validator reported 0 issues; the frozen
scorer's accounting section reported 288 checks, 0 failures (trace closure, frame closure, precompile counts, transcript
rounds, ZKsync OS gas rule, every negative control). Only `orchestrator.log`, `VALIDATION.json` and the scorer's
accounting outputs are kept here; the fixture measurements themselves are not part of the campaign.

Disclosure: PLONK verifiers are deterministic, so the P0 `ctx_d11_k4` PLONK fixture verifier is byte-identical to the
registered `c1_ctx_k04` PLONK verifier; the fixture therefore exercised that template under ZKsync OS v32 with P0 proofs.
The values were not analysed and could not influence the predictions, which are hash-frozen in the C1 package and
re-verified before and after collection.
