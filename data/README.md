# Data

Each directory is a frozen package, copied verbatim with its own manifest. Records (`record/`) hold the campaign record,
the scorer outputs and validation; evidence (`evidence/`) holds the raw per-cell records, traces, logs, compiled
artifacts, harness copies and run manifests.

| Directory | Content | Manifest |
|---|---|---|
| `p0-feasibility/` | P0 feasibility study: calibration source of the C1 predictions and of the tolerance sizes; never registered evidence | `SHA256SUMS` |
| `c1/pilot/record/`, `c1/pilot/evidence/` | registered pilot campaign | `SHA256SUMS` each |
| `c1/full/record/`, `c1/full/evidence/` | registered full campaign (with bridge cells as a reproduction control, and post-registered descriptive tables) | `SHA256SUMS` each |
| `c1/fflonk/record/`, `c1/fflonk/evidence/` | registered FFLONK cells; C1 scoring including FFLONK, and the C2 scores | `SHA256SUMS` each |
| `posthoc/native-cost-audit/` | post hoc source-level audit of the F4 residual (descriptive) | `SHA256SUMS` |
| `posthoc/heap-retrace/` | post hoc deterministic re-trace of heap-expansion events (descriptive) | `SHA256SUMS` |
| `prover/d1/evidence/`, `prover/d1/analysis/` | D1 timed rounds and analysis (Host A) | `SHA256SUMS` each |
| `prover/d2/timed/`, `prover/d2/analysis/`, `prover/d2/host-b-records/` | D2 timed campaign, analysis and Host B records | `SHA256SUMS`, `SHA256SUMS`, `RECORDS-SHA256SUMS` |
| `prover/d3/reanalysis/` | D3 descriptive re-analysis | `SHA256SUMS` |
| `prover/d3/source/` | the source files read by the D3 re-analysis, with the hashes verified in `reanalysis/out/D3-input-verification.json` (Table S25) | `provenance/OBJECT-CLASS.tsv` |

Some files listed by a manifest are classified rather than published (`provenance/WITHHELD.tsv`,
`provenance/REGENERABLE.tsv`); `scripts/verify-artifact.sh` reports them as such.
