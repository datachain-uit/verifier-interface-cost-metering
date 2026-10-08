# V2-PRV-D3-01 — D3 statistics re-analysis of the frozen V1 prover campaign (SUPPORTING evidence package)

Protocol (frozen before execution): `research/csi/protocols/v2/prover-D3/` (v1.1, `SHA256SUMS` `cdbb7256…e162d`).
Source: V1 campaign `campaign-20260925T060607Z` (inherited read-only; 14 / 14 input hashes verified). **No new runs, no
new timing.** cpu2 / cpu4 / cpu8 are three resource allocations on one Apple M5 host (VM-vCPU cpusets), never devices.
PLONK intervals (n = 5) are COARSE.

| Path | Content |
|---|---|
| `out/D3-input-verification.json` | 14 / 14 input sha256 OK |
| `out/D3-reconciliation.json` | V1 derived tables vs raw accepted rows: prover_per_round 1,210 / 1,210, prover_summary 462 / 462, prover_diag 48 / 48 match; 0 mismatches |
| `out/D3-cell-stats.csv` | 693 rows: n, mean, sd, CV, median, Q1, Q3, IQR, min, max, bootstrap 95 % interval of the median, seed |
| `out/D3-backend-ratios.csv` | 66 rows: within-round PLONK / Groth16 (prove, wall) per allocation and depth, rounds 1–5 |
| `out/D3-allocation-speedups.csv` | 462 rows: within-round speedups cpu2→cpu4, cpu4→cpu8, cpu2→cpu8 per backend, stage, depth, rounds 1–5 |
| `out/D3-zkey-diagnostic.csv` | 72 rows: key-path vs key-in-memory prove time and their difference (see DEV-D3-2) |
| `out/D3-CHECK-RECORD.json`, `out/D3-RUN-RECORD.json` | run records (script hash, seed 20261004, B = 10,000, Python, counts) |
| `out-attempt-1/` | aborted first check (DEV-D3-1), kept |
| `run-stdout.txt` | console output of the single run |
| `DEVIATIONS.md` | DEV-D3-1, DEV-D3-2 |
