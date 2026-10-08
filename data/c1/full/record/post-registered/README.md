# POST-REGISTERED DESCRIPTIVE OUTPUTS (post hoc; C1 19-scoring-plan rule 5)

Not part of the frozen scoring plan; produced only after collection, freeze, hashing, registration and frozen scoring.
No new model, no refit, no tolerance change, no verdict.

- `ZKOS-residual-vs-k.csv` / `.json` — ZKsync OS conditional-model residual (measured − frozen prediction) per
  (backend, k, relation), Groth16 and PLONK separately, with the frozen v0.4.0 trace-model component changes relative to
  k = 1 and a descriptive least-squares line of the mean residual on k (`tools/zkos_residual_vs_k.py`).
- `npg-per-proof.csv` — per-proof ZKsync OS meters for every registered measurement: EVM trace cost (EVM Osaka gas of the
  same proof), computational native, native_used, native-bound gas, binding meter, final gas, backend, k, proof ID,
  native_per_gas, priority fee (`tools/npg_per_proof.py`). `native_per_gas` is a meter-binding parameter, not a
  cryptographic tariff.
