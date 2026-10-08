# V2-C1 — model specification, experimental protocol and pre-registration

**Status: FROZEN (2026-10-04).** Integrity: `SHA256SUMS` (every file of this package). The prediction files in
`09-numeric-predictions/` are immutable before the registered pilot. **No registered data exist at freeze time.** The
pilot is not run in C1. The manuscript, V1, the frozen V1 public artifact and the CSI draft are not touched.

P0 diagnostics (`p0-feasibility/`) and the ZKsync OS v32.0 smoke check are feasibility data: they calibrate the
a-priori predictions and size the tolerances (declared in the ledger) and are never registered evidence.

## Index (owner's 20 required artifacts → files)

| # | Required artifact | File(s) |
|---|---|---|
| 1 | Thesis / scope | `01-thesis-and-scope.md` |
| 2 | RQs / hypotheses | `02-research-questions-and-hypotheses.md` |
| 3 | Factors / configs | `03-factors-and-configurations.md`, `configs/design-cells.csv`, `configs/make_design_cells.py` |
| 4 | Toolchain matrix | `04-toolchain-matrix.md`, `toolchain/PINS-C1.txt`, `toolchain/zksync-os-v0.4.0-*.rs` |
| 5 | Relation spec | `05-relation-specification.md`, `circuits/` (sources, generator, setup script, Groth16 keys, vkeys, verifiers, `CIRCUITS.csv`) |
| 6 | Equations | `06-model-equations.md`, `model/c1_model.py`, `model/zkos_native_trace_model.py` |
| 7 | Parameter ledger | `07-parameter-ledger.csv`, `07-parameter-ledger.md` |
| 8 | Calibration / held-out matrix | `08-calibration-heldout-matrix.csv`, `08-calibration-heldout-matrix.md` |
| 9 | Numeric predictions | `09-numeric-predictions/` (`predictions_cells.csv`, `predictions_signs.csv`, `fitted_parameters_and_tolerances.json`, `p0_model_check.csv`, `equality_bands.csv`), `09-numeric-predictions.md`, `model/c1_predict.py` |
| 10 | Crossover intervals | `09-numeric-predictions/crossover_intervals.csv`, `10-crossover-intervals.md` |
| 11 | ZKsync OS switch intervals | `09-numeric-predictions/zkos_switch_intervals.csv`, `zkos_npg_levels.csv`, `zkos_npg_predictions.csv`, `11-zksync-os-switch-intervals.md` |
| 12 | Falsifiers | `12-falsifiers.md` |
| 13 | Criteria | `13-criteria.md`, `13-tolerances.csv` |
| 14 | Corpus spec | `14-proof-corpus-spec.md`, `corpus/` (generator, inputs, proofs, calldata, manifest, `CORPUS-SHA256SUMS`) |
| 15 | Pilot protocol | `15-pilot-protocol.md` |
| 16 | Full protocol | `16-full-protocol.md` |
| 17 | Negative-control protocol | `17-negative-control-protocol.md` |
| 18 | Evidence schema | `18-evidence-schema.md`, `18-evidence-schema.json` |
| 19 | Scoring plan | `19-scoring-plan.md`, `scoring/score_c1.py` |
| 20 | Deviations policy | `20-deviations-policy.md` |
| + | FFLONK decision and ptau plan | `21-fflonk-decision-and-ptau-plan.md` |
| + | ZKsync OS version selection | `22-zksync-os-version-selection.md`, `version-selection/zkos-v32.0-smoke-runs.json` |
| + | External-fact hygiene | `23-external-fact-hygiene.md` |
| + | Code test of the scorer (not evidence) | `test/p0_to_mock_evidence.py`, `test/scorer-selftest-summary.json` |

## Verify

```
cd <this folder> && sha256sum -c SHA256SUMS            # every file
cd corpus && sha256sum -c CORPUS-SHA256SUMS             # corpus files
```

PLONK proving keys are not stored (97 MB each); they regenerate byte-identically from the R1CS and the V1 power-16 ptau
(`circuits/build_all.sh`), and their sha256 is in `circuits/CIRCUITS.csv`.

## Where it ran

Setup, corpus generation and prediction generation ran in the cloud container (x86_64, 2 vCPU, node v22.22.0) with the
binaries in `toolchain/PINS-C1.txt`. Scripts use `~/p0/…` and `~/c1/…` paths of that container; adjust `HOME`-relative
paths to rerun elsewhere.
