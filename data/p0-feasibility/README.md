# p0-feasibility — V2-P0 scientific feasibility sprint (2026-10-04)

**These are FEASIBILITY OUTPUTS, not registered campaign evidence.**
- Numbers here must not be cited as final results.
- The registered protocol, predictions and tolerances are frozen in C1, before any registered pilot.
- Report: `notes/V2-P0-gate-F-report.md`.

## Contents

| Path | What |
|---|---|
| `toolchain/PINS.txt` | Exact binaries (sha256), versions and settings used |
| `toolchain/zksync-os-v0.3.2-*.rs` | ZKsync OS VM cost constants at the pinned tag (native table, BN254 natives) |
| `tools/lib/` | Standard-JSON compilation (solc / zksolc), proof calldata helpers, EraVM runner (anvil-zksync, EIP-712 transactions, refund-trace accounting as in V1) |
| `tools/hh/` | EDR runner (Hardhat 2.29.1); opcode, precompile, keccak and copy profile of traced transactions; hardfork from `HF` |
| `tools/sweep/` | `run.js` (EVM / EraVM per circuit × backend), `zkos_run.js` (ZKsync OS), batch scripts, generated managers, analysis scripts (`summarize.py`, `eravm_frames.py`, `eravm_model.py`, `zkos_native_model.py`) |
| `tools/zkos/start.sh` | Fresh local ZKsync OS (server v0.23.0, local chain v31.0, L1 anvil 1.5.1) with fixed fee overrides |
| `tools/circ/` | Circuit family generator (`ctx` context tags, `a4` / `a8` semantic anchors, `disc` attribute disclosure, `mini` depth 0, `pad` D1 padding), setup and synthetic prover |
| `tools/micro/` | EraVM microbenchmark contract and runner |
| `tools/ptau/mk.sh` | Local feasibility ptau generator (single contribution + beacon; not a ceremony) |
| `tools/v1repro/` | Reproduction of V1 d = 11 cells from V1 contracts and the V1 public proof set |
| `circuits/` | Generated `.circom` sources, setup times, PLONK gate counts |
| `verifiers/<circuit>/` | Generated Solidity verifiers and verification keys (keys themselves not kept; deterministic PLONK keys regenerate byte-identically) |
| `proofs/<circuit>/` | Synthetic proofs (synthetic records only) |
| `results/raw/` | Per-run JSON (EVM `sweep-evm-*`, EraVM `sweep-eravm-*`, ZKsync OS `zkos-*`, microbenchmarks, V1 reproduction) |
| `results/derived/` | Summary tables, EraVM frame decomposition, model outputs, batch logs |

## Where it ran

The cloud container: x86_64 Linux, 2 vCPU, 7 GB, Node 22. Paths inside the scripts point to `~/p0/...` in that
container. To rerun, recreate that layout or adjust `HOME`-relative paths. Every binary is an official GitHub
release pinned by sha256 in `toolchain/PINS.txt`.
