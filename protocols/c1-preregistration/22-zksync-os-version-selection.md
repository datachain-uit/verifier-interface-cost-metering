# 22 — ZKsync OS version selection: bounded v32.0 smoke check (DIAGNOSTIC, not evidence)

**Purpose:** choose one ZKsync OS version for the registered design. No sweep. The values below are diagnostic and are
used only (a) for the version decision and (b) as the declared k = 1 calibration source of the a-priori predictions
(ledger rows `base_zk`, `c_zk`). Raw records: `version-selection/zkos-v32.0-smoke-runs.json`.

**Configuration:** zksync-os-server v0.23.0 (binary sha256 `5a319871…678d`, release tarball `07bd7e50…3004`, commit
610bfa2b); `local-chains/v32.0` (protocol 0.32.0 upgrade transaction applied at genesis; `execution_version: 7`; VM
zksync-os v0.4.0 @ 69bc4305; era-contracts 8fb7c29a); L1 = anvil 1.5.1 with the v32.0 L1 state; fee overrides as in
`04-…`; P0 V1-relation circuit (`v1_d11`, k = 1) with the P0 synthetic proofs j0, j1.

| # | Owner check | Result |
|---|---|---|
| 1 | Server starts reproducibly | ✔ three fresh starts (tags v32b, v32c, v32n150/v32n300); protocol 0.32.0 upgrade found and executed each time |
| 2 | Identical bytecode deploys | ✔ Groth16 verifier deploy gas 349,604 and PLONK 1,226,937, equal to the EVM (EDR Osaka) deploy gas of the same init code |
| 3 | k = 1 Groth16 / PLONK accepted | ✔ `valid → true` |
| 4 | Perturbed rejected | ✔ `tampered_proof → false`, `perturb_pub_0 → false` (both backends) |
| 5 | EVM gas, native and pubdata visible | ✔ receipt gasUsed; DEBUG line gives gas_used, gas_refunded, computational_native_used, native_used, pubdata_used (167 bytes per verify transaction) |
| 6 | Binding meter identifiable | ✔ gas = max(EVM gas, ⌊native / npg⌋) on every row (see table) |
| 7 | `native_per_gas` still available | ✔ operator config route (npg 150, 300) and transaction-price route (priority fee 1e8, 3e8) both act |
| 8 | Fresh runs deterministic | ✔ identical native and gas on fresh restarts (v32b vs v32c) |

| Setting | G16 j0 gas | G16 native | P j0 / j1 gas | P native j0 / j1 | Binding (G16 / P) |
|---|---|---|---|---|---|
| npg 100 (default) | 365,068 | 36,506,865 | 386,830 / 386,528 | 38,683,079 / 38,652,853 | native / native |
| npg 150 (operator) | 243,379 | 36,506,865 | 291,983 / 290,869 | same | native / EVM gas |
| npg 300 (operator) | 214,585 | 36,506,865 | 291,983 / 290,869 | same | EVM gas / EVM gas |
| npg 100 + priority 1e8 | 214,585 | 36,506,865 | 291,983 / 290,869 | same | EVM gas / EVM gas |

EVM-bound gas equals the EDR Osaka gas of the same transaction (214,585; 291,983 / 290,869). Native does not depend on
the price setting.

**Regression check against v31:** none in function. The VM changed its prices (v0.4.0 reprices opcodes, keccak and the
BN254 precompiles; pairing becomes base 6.244M + 6.908M per pair instead of 15M + 15M per pair). Consequence: at k = 1
under npg 100 the PLONK/Groth16 ratio is 1.06 (v32) instead of 0.82 (v31). This is a price-vector change, not a defect.
The P0 v31 natives therefore do not transfer to v32 numerically; the model form does (`06-…`).

**Decision (owner rule applied):** v32.0 passes cleanly → **ZKsync OS v32.0 is frozen as the single ZKsync OS version.**
Pins: `toolchain/PINS-C1.txt`.
