# Deviations — V2-PRV-D3-01

- **DEV-D3-1 (before any statistic).** Script v1.0 expected booleans `true`; the V1 raw tables use `1`. The first check
  aborted at row loading (input verification had passed, kept in `out-attempt-1/`). Script v1.1 accepts `1` / `true` and
  also requires valid proofs in diagnostic rows; re-frozen before the check and the single run.
- **DEV-D3-2 (found after the single run; no rerun).** The V1 diagnostic rows record the zkey read time on the
  key-in-memory call (`mem`, where the file is read into memory), not on the `path` call. The script took it from `path`
  rows, which are empty, so `D3-zkey-diagnostic.csv` has no `zkey_readfile_ms` rows (72 instead of 96). The prove-time
  quantities (path, mem, difference) are unaffected. The per-cell median read time remains available in the V1 derived
  `prover_diag.csv` (`median_zkey_readfile_ms`), which D3 reconciled exactly against the raw rows (48 / 48). Not rerun,
  to keep the single-run rule.
