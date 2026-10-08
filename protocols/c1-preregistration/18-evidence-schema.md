# 18 — Evidence schema (V2-C1, frozen): `v2-c1-evidence/1`

Registered evidence = JSON Lines files, one record per transaction or control call, plus one run manifest per run.
Machine-readable schema: `18-evidence-schema.json`. The scorer (`scoring/score_c1.py`) reads only these files.
Raw node logs (EDR trace dumps, anvil-zksync refund traces, ZKsync OS server logs) are kept beside the JSONL, hashed
in the run manifest, and are the primary source if a record is questioned.

## 1. Record fields

| Field | Type | Meaning |
|---|---|---|
| `schema` | "v2-c1-evidence/1" | |
| `campaign` | PILOT \| FULL \| BRIDGE \| AMENDMENT-<id> | |
| `run_id` | string | `<campaign>-<utc>-<cell_id hash 8>` |
| `order_index` | int | position in the pre-registered cell order |
| `utc` | ISO-8601 | record time |
| `env` | evm-osaka \| evm-petersburg \| eravm-29 \| eravm-27 \| zkos-v32 | regime |
| `regime` | object | `{hardfork}` \| `{protocol}` \| `{npg, native_price, pubdata_price, priority_fee}` |
| `backend` | groth16 \| plonk \| fflonk | |
| `circuit` | string | `c1_…` (see `circuits/CIRCUITS.csv`) |
| `k` | int | public-input count |
| `relation` | ctx \| a4 \| a8 \| disc | |
| `proof_id` | string \| null | `<circuit>/<backend>/j<j>` |
| `op` | deploy_verifier \| deploy_manager \| set_issuer \| add_root \| verify_credential \| verify_proof_direct \| control | |
| `control` | null \| valid \| tampered_proof \| perturb_pub_<i> \| out_of_field_pub \| foreign_vk_proof \| replay \| unknown_root_tx \| cross_regime_identity | |
| `role` | measurement \| control \| replay \| setup | only `measurement` enters cell means |
| `status` | 0 \| 1 | receipt status (tx) |
| `returned` | "true" \| "false" \| "revert" \| null | decoded return of a call |
| `tx_hash` | string \| null | |
| `gas_used` | int \| null | receipt gasUsed (EVM: EDR; EraVM: receipt total; ZKsync OS: receipt) |
| `calldata_bytes`, `calldata_zero` | int | of the submitted transaction |
| `evm_trace` | object \| null | EDR: `gas`, `steps`, `ops{op:{n,gas}}`, `precompiles{addr:{n,gas}}`, `keccak_sizes[]`, `copies[[kind,bytes]]`, `maxMem`, `sdiv_count` — **required for every `verify_proof_direct` in evm-osaka** |
| `eravm` | object \| null | `computational_gas`, `pubdata_gas`, `pubdata_bytes`, `frames{outside, self, precompiles{"0006":[n,total], "0007":…, "0008":…, "8010":…}}` |
| `zkos` | object \| null | `gas_used_log`, `gas_refunded`, `computational_native`, `native_used`, `pubdata_used`, `effective_gas_price`, `base_fee` |
| `artifacts` | object | `verifier_runtime_sha256`, `manager_runtime_sha256`, `proof_file_sha256`, `pins_sha256` |
| `deviation_ref` | string \| null | `DEV-…` if a deviation record covers this record |

## 2. Metrics derived by the scorer

| Metric | Definition | Unit |
|---|---|---|
| Y_dir | `gas_used` (EVM, ZKsync OS) or `eravm.computational_gas` (EraVM) of `verify_proof_direct` | regime unit |
| Y_app | same for `verify_credential` | regime unit |
| Ync | EVM only: `gas_used − c_nz·(calldata_bytes − calldata_zero) − 4·calldata_zero` | gas |
| N_dir | `zkos.computational_native` of `verify_proof_direct` | native |
| cell mean | arithmetic mean over j = 0…7 of measurement records | |
| r_E(k) | mean_P / mean_G for the same metric, regime and k | ratio |

EraVM computational gas follows V1: receipt total minus the pubdata component, taken from the anvil-zksync refund trace
(`RUST_LOG`), with callTracer frames for the decomposition.

## 3. Run manifest (one per run)

`run_id`, campaign, cell list, UTC start/end, host description, pins file sha256, harness code sha256 (from H-freeze),
node versions and flags, server config hashes, the sha256 of every raw log, the deviation records opened.

## 4. Immutability

Evidence files are written once. Corrections are new records referencing the original (`supersedes`), never edits.
The scorer output is regenerated from the evidence; it is never edited by hand.
