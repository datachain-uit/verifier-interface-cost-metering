# 04 — Toolchain matrix (V2-C1, frozen)

Exact hashes: `toolchain/PINS-C1.txt`. A run whose tool hash differs from the pin is a deviation (`20-…`, class D-HASH).

| Role | Tool | Version / pin | Used for | Class |
|---|---|---|---|---|
| Circuit compiler | circom | 2.1.6 (official linux-amd64 release) | R1CS / wasm of all C1 circuits | all |
| Circuit library | circomlib | 2.0.5 | Poseidon, comparators (V1 templates byte-identical) | all |
| Proving system | snarkjs | 0.7.5 (ffjavascript 0.3.1) | Setup, proving, Solidity verifier export (templates hashed in pins) | all |
| ptau (G16, PLONK) | V1 `pot16_final.ptau` | sha256 `4a64b121…439e` | Groth16 phase 2 base, PLONK setup (deterministic; k = 1 key byte-identical to V1) | CORE |
| ptau (FFLONK) | Hermez `powersOfTau28_hez_final_19.ptau` | BLAKE2b-512 `bca9d8b0…0887` (snarkjs 0.7.5 README) | FFLONK d = 11 setup | VALIDATION, conditional (`21-…`) |
| EVM compiler | solc | 0.8.20 static, EVM version Paris, optimizer 200 runs | Verifiers and managers (V1 primary profile) | all EVM-type regimes |
| EVM execution | Hardhat 2.29.1 / EDR 0.12.0-next.23 | hardfork `osaka` (CORE), `petersburg` (SUPPORTING) | Y_dir, Y_app, full opcode trace of every proof | CORE |
| EraVM compiler | zksolc 1.5.15 + era-solc 0.8.20-1.0.2 | `-O3`, size fallback, codegen Yul, EVM version Paris (V1 pins) | EraVM bytecode | CORE / VALIDATION |
| EraVM node | anvil-zksync | **0.6.11** (V1-compatible pin; sha256 match with V1) | protocol 29 (CORE), 27 (VALIDATION); computational gas from the refund trace; callTracer frames | CORE / VALIDATION |
| ZKsync OS node | zksync-os-server | v0.23.0 prebuilt x86_64 (commit 610bfa2b) | local chain **v32.0** (zksync_os_version 0.32.0, execution_version 7) | CORE |
| ZKsync OS VM | zksync-os | **v0.4.0** (commit 69bc4305; per `local-chains/v32.0/versions.yaml`) | Native cost constants (copied into `toolchain/`) | CORE model |
| L1 for ZKsync OS | foundry anvil | 1.5.1 | `--load-state` of the v32.0 L1 state | CORE |
| Runtime | node | v22.22.0; ethers 6.13.5 | Harness | all |
| Analysis | python 3 | stdlib only | `model/`, `scoring/` | all |

## ZKsync OS version: frozen to v32.0

Decision rule (owner): "v32 passes cleanly → use v32; any regression → v31 with documentation". The bounded v32.0 smoke
check passed every item (`22-zksync-os-version-selection.md`). **v32.0 is the only ZKsync OS version in the registered
design.** v31.0 / VM v0.3.2 appears only in P0 feasibility data and in the tolerance transfer documented in the ledger.

## Fee configuration (ZKsync OS, all registered runs)

Environment of the server process: `general_ephemeral=true`, `fee_native_price_override=0xf4240`,
`fee_pubdata_price_override=0x0`, `fee_native_per_gas=<level>` (100 = operator default per `FeeConfig`),
`RUST_LOG=info,zksync_os_sequencer::execution::execute_block_in_vm=debug` (per-transaction native / pubdata line).
Transactions: EIP-1559, gas limit 10,000,000 (v32 rejects limits above its transaction limit:
`CallerGasLimitMoreThanTxLimit`), priority fee 0 except the robustness cells.

## EraVM node

anvil-zksync stays at the V1-compatible 0.6.11 (`--protocol-version 29` / `27`, V1 command-line flags, one transaction
per L1 batch). No newer anvil-zksync release is used or claimed (`23-external-fact-hygiene.md`).

## Harness

The registered harness derives from the P0 tools (`p0-feasibility/tools/`) with these frozen requirements:
(1) 8 proofs per cell from `corpus/proofs/`; (2) an EDR opcode trace for **every** direct verifier call (not only
j = 0); (3) the controls of `17-…`; (4) output records in the schema of `18-evidence-schema.md`; (5) a run manifest with
the pin hashes. The harness code is hashed at the **H-freeze** step, which is step 0 of the pilot and precedes any
registered measurement (`15-pilot-protocol.md`). A harness self-test on P0 circuits at H-freeze is a tooling check and
is not evidence.
