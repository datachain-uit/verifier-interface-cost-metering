# 17 — Negative-control protocol (V2-C1, frozen)

Controls run in every registered cell (every regime, every npg level), after the measurements, on proof j = 0 unless
stated. They are `eth_call`s (no state change) except where marked "tx". Expected outcomes are fixed here; any
other outcome is a deviation of class D-CTRL (`20-…`) and blocks the cell's use for predictive scoring until adjudicated.

| Control | Construction | Expected | Purpose |
|---|---|---|---|
| `valid` | j = 0 proof, unchanged | `true` | Positive control |
| `tampered_proof` | last proof word w → w + 1 (w − 1 if w + 1 ≥ modulus) (V1 rule) | `false` or revert | Proof binding |
| `perturb_pub_i`, **every** i = 0 … k − 1 | public input i → (x + 1) mod r | `false` or revert | Binding of each public input (root and every tag) |
| `out_of_field_pub` | public input k − 1 → x + r (non-canonical, < 2²⁵⁶) | `false` or revert | Field check of the template |
| `foreign_vk_proof` (k ∈ {4, 8} only, where another circuit with the same k exists) | k = 4: the `c1_a4` j = 0 proof sent to the `c1_ctx_k04` verifier, the `c1_ctx_k04` proof to the `c1_a4` and `c1_disc_k04` verifiers; k = 8: `c1_a8` ↔ `c1_ctx_k08` | `false` or revert | Key binding |
| `replay` (tx) | j = 0 direct verify sent a second time | success, same cost as the first in EVM / EraVM / ZKsync OS (deterministic meters) | Determinism; **not** a replicate |
| `unknown_root_tx` (tx, manager) | `verifyCredential` with public input 0 perturbed | reverted (`Invalid root`) | Manager semantics (V1) |
| `cross_regime_identity` | same proof ID returns `true` in every regime | `true` | Corpus integrity |

Additional run-level controls:

- **Bytecode identity:** the deployed verifier runtime bytecode hash equals the hash in the run manifest (EVM regimes
  and ZKsync OS share the solc output; EraVM regimes share the zksolc output).
- **Bridge cells:** the FULL campaign re-measures the k = 1 and k = 4 CORE cells (both backends, three regimes) and
  must reproduce the pilot values exactly for Groth16 in every regime and for ZKsync OS native of every proof
  (deterministic meters); PLONK EVM / EraVM values must be identical per proof ID (same proof file).
- **Version stamp:** each ZKsync OS run records the protocol-upgrade log line (0.32.0) and `execution_version: 7`;
  each EraVM run records the protocol flag; mismatch → D-HASH.

Controls are excluded from cell means by role, and reported in `AC_checks.csv` of the scoring output.
