# 21 — FFLONK: d = 11 setup requirement, ptau plan and decision (V2-C1)

## 1. Requirement (computed from snarkjs 0.7.5 `fflonk_setup.js`)

- cirPower = max(3, ⌊log₂(n_plonk + 1)⌋ + 1); domainSize = 2^cirPower.
- Required: ptau section 2 (τ·G1 powers) must hold at least **9·domainSize + 18** G1 points.
- d = 11 family: n_plonk = 34,077 (k = 1) … 34,139 (k = 32) (C1 setup logs) → cirPower 16, domainSize 65,536 →
  **589,842 G1 points**.
- A power-p ptau holds 2^(p+1) − 1 G1 points: p = 18 → 524,287 (insufficient); **p = 19 → 1,048,575 (sufficient)**.
  P0 observed the matching failure with pot16 ("Section 2 too small").

## 2. Artifact (existing, hash-verifiable)

| Field | Value |
|---|---|
| File | `powersOfTau28_hez_final_19.ptau` — the prepared (phase-2-ready) bn128 series listed in the snarkjs README as "with 54 contributions and a beacon" |
| Published URL | `https://storage.googleapis.com/zkevm/ptau/powersOfTau28_hez_final_19.ptau` |
| Published hash | BLAKE2b-512 `bca9d8b04242f175189872c42ceaa21e2951e0f0f272a0cc54fc37193ff6648600eaf1c555c70cdedfaf9fb74927de7aa1d33dc1e2a7f1a50619484989da0887` |
| Hash source | snarkjs v0.7.5 `README.md` (fetched from raw.githubusercontent.com at tag v0.7.5; sha256 of that README `7a922845d2c597bcf699dc25b5399023c8f5daece469fb6e25774e4c0e438bb2`) |
| Retrieval | blocked from the cloud container (HTTP 403 via proxy). To be downloaded on the owner workstation. |

**Plan (owner-side, no long job in C1):**
1. Download the file on the workstation; `b2sum powersOfTau28_hez_final_19.ptau` must equal the published hash
   (otherwise stop; do not use). Record sha256 as well.
2. Optional: `snarkjs powersoftau verify` (hours; not required since the hash matches the published artifact).
3. Stage the file to the V2 workspace (`setup/ptau/`), record both hashes in an amendment record AMD-FF-1.
4. FFLONK setup for `c1_ff_k01`, `c1_ff_k04`, `c1_ff_k16`, `c1_ff_k32` from the frozen R1CS (same sources as `c1_k01`,
   `c1_ctx_kKK`); export vkey and verifier; record hashes; generate FFLONK proofs from the frozen corpus inputs.
5. Fallback only if no verifiable power-19 ptau can be obtained: one-off local generation on the workstation
   (power 19: new + one contribution + beacon + prepare phase2). P0 timing on 2 vCPU for power 18: contribution 6 min,
   beacon 4 min, phase-2 preparation > 40 min (unfinished). This is a research ptau, disclosed as such.

## 3. Gate and decision

**Decision: RETAIN — VALIDATION (conditional), same d = 11 family; snarkjs "Beta" status disclosed wherever FFLONK
appears.**

FFLONK gate (all required, recorded in AMD-FF-1 before any FFLONK measurement):
- G1: ptau obtained and BLAKE2b-verified (or the disclosed fallback).
- G2: setup completes for k ∈ {1, 4, 16, 32}; verifier exports compile with solc 0.8.20 and zksolc 1.5.15.
- G3: 8 corpus proofs per circuit generated and verified off-chain.
- G4: no FFLONK measurement of any kind has been taken in V2 at d = 11 before G1–G3 (keeps it held out).

| Outcome | Condition | Consequence |
|---|---|---|
| RETAIN VALIDATION | G1–G4 pass | FFLONK cells of `configs/design-cells.csv` run in the FULL campaign; H8 scored with τ_cond(F) |
| RETAIN-REDUCED | G1 or G2 fails | depth-0 family (`mini`, P0) only, labelled "reduced-depth family"; H8 restated for that family; no d = 11 claim |
| DROP | the reduced family also fails, or the owner declines the workstation step | FFLONK removed; H8 not tested; reported as not run |

FFLONK never becomes a co-equal CORE backend in V2-C1.

## 4. A-priori FFLONK numbers

`09-numeric-predictions/predictions_cells.csv` contains a-priori ZKsync OS natives for FFLONK at k ∈ {1, 4, 16, 32}, built from the P0
depth-0 traces (the d = 11 verifier differs only in vk constants and in three extra squarings for the larger domain,
≈ 0.01 % of native). The registered H8 test is the conditional procedure R on registered FFLONK traces.
