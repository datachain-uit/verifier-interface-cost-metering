# AMD-FF-1 — FFLONK gate record for V2-C1 (completed 2026-10-05T05:16:45Z, before any FFLONK measurement)

C1 package (unchanged): `research/csi/protocols/v2/V2-C1-preregistration/`, `SHA256SUMS` `7dac8482aea1420a30b303c3d45b0c46627da67a976e578fa1d09d7c715bfc8f`.
Basis: C1 `21-fflonk-decision-and-ptau-plan.md` §2 step 5 (fallback) and §3 (gate G1–G4). Owner decisions: V2-D-34
(published file not obtainable, HTTP 403), V2-D-38 (fallback approved), V2-A23 (execution authorized 2026-10-05:
"THE WORKSTATION IS FREE FOR V2 WORK"). Fresh read-only workstation precheck 2026-10-05T04:28:07Z: 0 containers,
load 0.00, CPU 100 % idle (5 s), 59.6 GiB available, 132.3 GiB free → GO.

| Gate | Condition (C1 doc 21 §3) | Record |
|---|---|---|
| G1 | ptau obtained and BLAKE2b-verified, **or the disclosed fallback** | **Fallback, PASS.** `powersOfTau19_v2_local_research.ptau` — **LOCALLY GENERATED RESEARCH PTAU** (not the Hermez ceremony file; not a trusted setup; not a public multi-party ceremony). Procedure: `powersoftau new bn128 19` → one contribution (64 B /dev/urandom entropy supplied on stdin, never stored; sha256 commitment `c95c00b1e3848fe44ed7bd66f7e64c4f9753beb25f17a06119ac2c5704deac46`) → deterministic recorded beacon `a5dabf111ad93e69c270a021ae947f68fb868726651304f4d677eb3a2518f02c` (sha256("V2-C1-AMD-FF-1"‖C1 hash‖sha256 of the contributed file), 2^10) → `prepare phase2` → `powersoftau verify` = **"Powers of Tau Ok!"** (PASS). Bytes 603,982,838; BLAKE2b-512 `dd34a643a5234521dfe96798c1988e0e0143641c643da8a4e08bcf234d40e726ef9098d68f5073c2d65003a6b69dcd7f0b4ce996aa01a2996812f00db6967dde`; SHA-256 `8fc8e14afd97f0a580c904a54ab2cf4f9cd8df97ed54218f83861d91b62457a8`; host ad-Precision-7920-Tower (kernel 6.14.0-29); node v22.22.0, snarkjs 0.7.5, ffjavascript 0.3.1; 2026-10-05T04:28:27Z → 04:43:43Z (duration not evidence); path `/home/ad/Workspace/Z-CORP-V2-workstation/ptau/local/`. Pre-execution correction DEV-FF-PTAU-1: the prepared job passed the entropy as a command-line argument, which its step logger would have written into `log-contribute.txt`; the executed copy passes it on stdin so that only the commitment is kept, as the runbook specifies. Procedure otherwise identical. |
| G2 | setup completes for k ∈ {1, 4, 16, 32}; verifier exports compile with solc 0.8.20 and zksolc 1.5.15 | **PASS.** `snarkjs fflonk setup` from the frozen R1CS (c1_k01, c1_ctx_k04, c1_ctx_k16, c1_ctx_k32; same family, d = 11), domain power 16 (doc 21 §1). zkey / vkey / verifier sha256: k01 `9983d751…` / `8ed73222…` / `1ced35ab…`; k04 `7c3daa36…` / `a0c5f6f2…` / `228e2ca2…`; k16 `6350907f…` / `2884be29…` / `509a652f…`; k32 `5ab16d42…` / `cdaead6c…` / `86ff588c…` (full hashes in `records/FFLONK-ARTIFACTS-SHA256SUMS`). Registered compile pipeline (`compile_all.js`, harness `02cee61b…`, `BACKENDS=fflonk`, solc 0.8.20 Paris, zksolc 1.5.15): EVM verifier runtime 14,349 / 15,311 / 18,927 / 23,759 bytes (all below the 24,576-byte limit); EraVM verifier 162,464 / 170,336 / 201,952 / 244,256 bytes. Compiled artifact sha256: k01 `3e72ef94…`, k04 `df60f95e…`, k16 `10f39c68…`, k32 `c6d8f4a2…`. |
| G3 | 8 corpus proofs per circuit generated and verified off-chain | **PASS.** 32 / 32 verified on the workstation (`records/prove-log.jsonl`) and 32 / 32 again in the cloud with the pinned snarkjs 0.7.5; proof IDs `<circuit>/fflonk/jJ`; public-signal count = k; public signals equal the frozen C1 corpus signals of the same relation and instance (c1_k01 / c1_ctx_kKK Groth16 proof jJ) for all 32 (`AMD-FF-1-G3-cloud-verify.json`). Public input 1 = Merkle root; inputs 2 … k = the registered context tags (no semantic change). |
| G4 | no FFLONK measurement of any kind at d = 11 before G1–G3 | **Confirmed**: until this record no FFLONK verifier has been deployed or executed on EDR, EraVM or ZKsync OS, and no FFLONK cell, trace or meter has been recorded. Next, in this order: C2 stage-2 structural derivation (EDR, no cost recorded) and the C2 numeric freeze, then the 12 registered cells. |

Consequence (C1 doc 21 §3): G1–G4 pass → **RETAIN VALIDATION**; the 12 `FULL-IF-FFLONK-GATE-PASSES` cells run; H8 is
scored with τ_cond(F); base and c are **not** re-fitted with FFLONK data; snarkjs FFLONK "Beta" status disclosed.
Disclosure: the FFLONK verifier keys derive from a locally generated research ptau; this affects the trust model of the
setup only, not the verifier's metered cost.

Artifacts: `research/results/v2/AMD-FF-1-fflonk-artifacts/` (transfer `fflonk-transfer.tgz` `80658421…9d71`;
`TRANSFER-SHA256SUMS` `67e46cc366f1609cd707ba0619037af0ba5d5db810d83fad672edba3ffca3953`, 70 files) and
`research/results/v2/AMD-FF-1-fflonk-artifacts-cloud/` (compiled verifiers, cloud G3 check). Workstation originals kept
at `/home/ad/Workspace/Z-CORP-V2-workstation/{ptau/local,fflonk}/` (zkeys and the ptau stay there; hashes travel).
Procedural note DEV-FF-2: the frozen `make_manifest.py` checks verifier sources against C1 `CIRCUITS.csv`, which has
no FFLONK rows (FFLONK keys did not exist at C1). The FFLONK compiled artifacts are therefore kept outside the
manifest's `compiled/` glob and their expected hashes are the ones in this record; the measurement harness is unchanged.
