# Protocols

Each directory is a frozen package, copied verbatim; its own manifest (`SHA256SUMS`) and README describe its content.

| Directory | Content | Manifest |
|---|---|---|
| `c1-preregistration/` | internal pre-registration C1: research questions and hypotheses, design, toolchain pins, relation specification, model equations and code, parameter ledger, held-out matrix, numeric predictions, falsifiers, criteria and tolerances, proof corpus, pilot / full / negative-control protocols, evidence schema, scorer, deviations policy | `SHA256SUMS` |
| `c1-amendment-fflonk-setup/` | recorded amendment for the FFLONK setup path (single frozen file) | file SHA-256 in `provenance/PATH-MAP.tsv` |
| `c2-forward-test/stage1/` | separate prospective test C2: model, calibration, prediction procedure, criteria, scoring code | `SHA256SUMS` |
| `c2-forward-test/stage2/` | C2 structural derivation and frozen predictions | `SHA256SUMS` |
| `posthoc-heap-retrace/` | protocol of the post hoc deterministic re-trace, frozen before the re-trace | `SHA256SUMS` |
| `prover-d1/` | D1 protocol, frozen circuits and keys, build records, kit | `SHA256SUMS` |
| `prover-d2/preregistration/`, `amendments/`, `final/` | D2 internal pre-registration, recorded amendments and engineering tests, final protocol record and analysis script | `SHA256SUMS` |
| `prover-d3/` | D3 protocol and re-analysis script | `SHA256SUMS` |
| `prover-procedure/` | `PROVER-PROCEDURE-v3-EXTRACT.md` (verbatim extract of the timed-round procedure cited by D2; `provenance/EXTRACTS.tsv`) and `kit/` (the prover kit it describes) | `provenance/OBJECT-CLASS.tsv` |
