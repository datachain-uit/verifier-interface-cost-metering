# Re-running the frozen scorers and analysis scripts (Level 2)

`rescore.py` runs each frozen scorer or analysis script, unchanged and from its frozen location, on the frozen evidence,
writes its outputs to a work directory outside the repository, and compares them byte for byte with the frozen outputs
(one exception, below).

```
python3 scoring/rescore.py --list                 # families, with what each re-runs
python3 scoring/rescore.py --inputs-only --all    # every input and frozen output present (no run)
python3 scoring/rescore.py --all                  # run everything; exit code 0 = every compared output identical
python3 scoring/rescore.py c1-full d3 --work /tmp/rescore --report /tmp/rescore/report.json
```

| Family | Re-runs | Compared with |
|---|---|---|
| `c1-full`, `c1-fflonk` | `protocols/c1-preregistration/scoring/score_c1.py` on the pilot and full (and FFLONK) records | `data/c1/full/record/scoring/`, `data/c1/fflonk/record/scoring-c1/` |
| `c1-predictions` | `protocols/c1-preregistration/model/c1_predict.py` on the P0 data | `protocols/c1-preregistration/09-numeric-predictions/` |
| `c2-calibration`, `c2-internal-check`, `c2-predict`, `c2-score` | `protocols/c2-forward-test/stage1/code/c2_*.py` | stage 1 `calibration/`, stage 2 predictions, `data/c1/fflonk/record/scoring-c2/` |
| `c1-residual`, `c1-npg-per-proof`, `c1-bridge` | `data/c1/full/record/tools/*.py` | `data/c1/full/record/post-registered/`, `bridge-check/` |
| `posthoc-audit`, `posthoc-retrace-count` | `data/posthoc/native-cost-audit/m7a_f4_audit.py`, `data/posthoc/heap-retrace/scripts/m7b_a_count.py` | their `out/` directories |
| `d1`, `d2`, `d3`, `d2-side-by-side` | the D1, D2 and D3 analysis scripts | `data/prover/d1/analysis/`, `data/prover/d2/analysis/`, `data/prover/d3/reanalysis/out/` |

Families marked `recorded` by `--list` use the invocation recorded next to the frozen outputs; `usage` families use the
argument order documented in the script's own usage line. Files that carry run metadata (timestamps, absolute paths)
are reported as informational and do not decide the outcome.

**Comparison rule.** Every compared output must be byte-identical, with one exception: `p0_model_check.csv` of
`c1-predictions`. The frozen predictor emits the same complete row multiset, but filesystem-dependent unsorted glob
ordering can permute row order; this specific output is therefore compared as an order-insensitive multiset (header
exact; every complete data row with its multiplicity, so an extra, missing or changed row is a DIFF) and reported as
`IDENTICAL-AS-ROW-MULTISET`, while all other outputs retain byte-identity checks. The last line before the work
directory reports both counts.

**Environment.** Byte identity is verified with Python 3.10.12 (`environment/README.md`). Under Python 3.13, `d1`, `d2`
and `d3` report DIFF: their outputs differ only in the last digit of some `sd` / `cv` values.

The frozen scripts expect the layout of the environment they ran in: a home directory with the C1 model, the pinned
ZKsync OS constant files and the P0 outputs (`~/c1/model`, `~/p0/zkos/vm-0.4.0/…`, `~/p0/out`), and a workspace root
for the D3 re-analysis. `rescore.py` builds both layouts in the work directory from files of this repository; the ZKsync
OS v32.0 smoke runs are written under the file names recorded in
`protocols/c1-preregistration/version-selection/zkos-v32.0-smoke-runs.json`.

Not covered here (Level 3): new measurements, the EVM re-trace that produced `data/posthoc/heap-retrace/raw/`, and prover
timing campaigns.
