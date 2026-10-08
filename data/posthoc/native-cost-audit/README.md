# V2-M7A — F4 mechanism audit package (POST HOC, DESCRIPTIVE DIAGNOSTIC)

Not registered evidence, not a revised model, not confirmatory. C1, H4, F4, tolerances, predictions, scorer outputs and
the pilot / full evidence are unchanged. Report: `notes/V2-M7-F4-mechanism-audit.md`.

| File | Content |
|---|---|
| `m7a_f4_audit.py` | the audit script (run once on 2026-10-04 in the cloud working copy; Python 3, standard library + the frozen C1 trace-model module) |
| `INPUT-HASHES.txt` | sha256 of the inputs, verified before the run (pilot and FULL records, frozen scorer summary, frozen trace model) |
| `SOURCE-FILES-SHA256.txt` | sha256 of the 16 cited ZKsync OS v0.4.0 source files (commit 69bc430549e88f9264066d14f2001707572c5d33, clean checkout) |
| `out/M7A-per-proof.csv` | 208 proofs: measured native, frozen prediction and residual, frozen components, source-defined omitted charges, remainder, mod-35 check |
| `out/M7A-cells.csv` | per (backend, relation, k) summary |
| `out/M7A-summary.json` | identification of c, exact decomposition of the k = 1 contrast, remainder structure |
