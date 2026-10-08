# V2-PRV-D3-01 — D3 statistics re-analysis of the frozen V1 prover campaign (protocol, frozen before execution)

Status: frozen 2026-10-04 before the run; owner authorization V2-A22 (D3 authorized, V2-D-37). Class: SUPPORTING.
**No new runs and no new timing.** Inputs are the frozen V1 prover evidence inherited read-only in V2.

## 1. Source campaign and meaning of the allocations

`campaign-20260925T060607Z` (V1 protocol v3; MacBook Pro Mac17,2, Apple M5; Docker Desktop VM 10 vCPUs; image
`linux/arm64`; snarkjs 0.7.5 / ffjavascript 0.3.1). `cpu2`, `cpu4`, `cpu8` are **three resource allocations on one
host** (Docker cpusets `1-2`, `1-4`, `1-8` of the VM's vCPUs with matched ffjavascript workers, 8 GiB, no quota). They
are never called devices, machines or hardware classes. Audit: `notes/V2-M5-prover-audit-and-D1-D2-D3-readiness.md`.

## 2. Inputs (sha256 verified by the script before any computation; mismatch aborts)

Raw: `research/results/postcorr-20260925/prover/cpu{2,4,8}/{runs,diag,rounds}.csv`, `prover/round_ledger.csv`,
`CAMPAIGN.json`. V1 derived tables used **only for reconciliation**: `derived/prover_summary.csv`,
`derived/prover_diag.csv`, `research/submission/csi/generated/prover_per_round.csv`. Hashes: the `MANIFEST` in
`d3_reanalysis.py` (identical to the V2 copy manifest, i.e. to V1).

## 3. Accepted rows

`runs.csv`: kind = primary, is_warmup = 0, status = ok, round_attempt = the accepted attempt of that round in
`round_ledger.csv`, proof_valid and root_matches true. Expected 495 rows (3 allocations × (11 depths × 10 Groth16
rounds + 11 depths × 5 PLONK rounds)). `diag.csv`: status ok, accepted diagnostic attempt; expected 240 rows. A different
count aborts.

## 4. Reconciliation (before statistics; reported, never repaired)

Every value of `prover_per_round.csv` (prove_ms, norm_d5, plonk_minus_groth16_s, gap_reduction_cpu2_to_cpu8_pct) is
recomputed from the raw accepted rows; every row of `prover_summary.csv` (n, median, q1, q3, iqr, min, max) and
`prover_diag.csv` (n, median_prove_ms, median_zkey_readfile_ms) likewise. Tolerance 1e-9 relative. Mismatches are
listed in `D3-reconciliation.json`; statistics always use the raw rows.

## 5. Quantities (descriptive; no decision thresholds)

| Output | Definition |
|---|---|
| `D3-cell-stats.csv` | per (allocation, backend, depth, rounds, stage) for stages input, witness, prove, verify_first, verify_steady, wall, stage_sum: n, mean, sd, **CV** = sd / mean, median, Q1, Q3, **IQR** (type-7 quantiles), min, max, **95 % percentile-bootstrap interval of the median**. Groth16: rounds 1–10 and, separately, rounds 1–5; PLONK: rounds 1–5, labelled **COARSE (n = 5)** |
| `D3-backend-ratios.csv` | **within-round PLONK / Groth16** ratio per (allocation, depth, round 1–5) for prove and wall: per-round values, median, min–max, CV, bootstrap interval (COARSE) |
| `D3-allocation-speedups.csv` | **within-round allocation speedups** cpu2→cpu4, cpu4→cpu8, cpu2→cpu8 = time at the smaller allocation / time at the larger, same round, per (backend, stage, depth): per-round values, median, min–max, bootstrap interval (COARSE) |
| `D3-zkey-diagnostic.csv` | zkey-loading diagnostic per (allocation, backend, depth), diagnostic rounds 1–5: prove_ms with the key read from the file path, with the key preloaded in memory, their difference, zkey read time: n, median, IQR, min–max, CV, bootstrap interval (COARSE) |

Bootstrap: B = 10,000 resamples with replacement of the per-round values; statistic = median (type 7); interval =
2.5th / 97.5th percentiles; seed per quantity = first 16 hex digits of sha256("20261004|" + key), recorded per row.
With n = 5 there are at most 126 distinct resamples; such intervals are coarse and are labelled so.

## 6. Execution

1. Freeze this protocol and `d3_reanalysis.py` (`SHA256SUMS` in this directory); register V2-PRV-D3-01 as planned.
2. `python3 d3_reanalysis.py --root <V2 root> --out research/results/v2/V2-PRV-D3-01/out --mode check`.
3. `... --mode run` **once**. Outputs and run records are hashed (`SHA256SUMS`), a campaign record is written and the
   registry row is set to validated.

Deviations: any rerun, script change or input change after step 1 is a deviation and is recorded. The V1 evidence is
never modified.

## 7. Wording rules

Effect sizes, not verdicts; "allocation" never "device"; COARSE for n = 5; no comparison with D1 / D2 data; no pooling.

## 8. Deviations (recorded)

- **DEV-D3-1 (2026-10-04, before any statistic was computed).** The first `--mode check` aborted at row loading: the V1
  raw tables encode booleans as `1`, while script v1.0 expected `true`. Script v1.1 accepts `1` or `true` and also
  requires valid proofs in the diagnostic rows; nothing else changed. v1.0 freeze: `SHA256SUMS` `af70d086…2800`
  (script `6446aff2…93ea`). The check output of the aborted attempt (input verification, 14 / 14 OK) is kept as
  `out-attempt-1/`. Re-frozen as v1.1 before the check and the single run.
