# Licences

This artifact combines author code, author data and documentation, and third-party material. Each file is covered by
exactly one licence, found with the first rule below that matches it; a licence notice embedded in a file (rule 1)
takes precedence over every path rule. Licence texts are in `LICENSES/`; third-party notices are in `NOTICE`. No file
was edited to add a licence header: frozen files keep their bytes.

The per-file result is `provenance/LICENSE-MAP.tsv`, produced and audited by `python3 scripts/classify_licences.py --check`
(every published file classified exactly once; path rules 2–6 disjoint; no file with conflicting embedded notices).

| # | Files | Licence | Licence text |
|---|---|---|---|
| 0 | `LICENSES/*` | the licence texts themselves, under their own terms | – |
| 1 | Any file that carries its own `SPDX-License-Identifier` tag. This covers the Solidity verifier contracts generated with snarkJS (`*Verifier*.sol` under `data/p0-feasibility/verifiers/`, `protocols/c1-preregistration/circuits/keys/`, `setup/fflonk/keys/` and `setup/prover-objects/contracts/`), which state GPL-3.0, version 3 or any later version, and author files tagged MIT | the licence stated in the file | `LICENSES/GPL-3.0.txt`, `LICENSES/MIT.txt` |
| 2 | Compiled forms of those verifiers (each file also holds the compiled author manager contract): `data/c1/*/evidence/compiled*/*.json` and `setup/fflonk/compiled-verifiers/compiled-fflonk/*.json` | GPL-3.0-or-later | `LICENSES/GPL-3.0.txt` |
| 3 | Witness-generator code emitted by the circom compiler: files in `*_js/` directories and `*.wasm` files | GPL-3.0 | `LICENSES/GPL-3.0.txt` |
| 4 | Constraint and key files produced with the circom / circomlib and snarkJS toolchain: R1CS files (`*.r1cs`), proving keys (`*.zkey`) and verification keys (`*.json` files whose name contains `vkey`) | GPL-3.0 | `LICENSES/GPL-3.0.txt` |
| 5 | Constant files copied from the ZKsync OS source: `protocols/c1-preregistration/toolchain/zksync-os-v0.4.0-*.rs` and `data/p0-feasibility/toolchain/zksync-os-v0.3.2-*.rs` | MIT OR Apache-2.0 (upstream) | `LICENSES/MIT.txt`, `LICENSES/Apache-2.0.txt` |
| 6 | Author code outside `*_js/` directories: `*.py`, `*.js`, `*.cjs`, `*.mjs`, `*.sh`, `*.circom`, `*.sol` without a notice, `Dockerfile`, `.dockerignore`, `compose.yaml`, `package.json`, `package-lock.json` | MIT | `LICENSES/MIT.txt` |
| 7 | Everything else: protocols, records, measurements, logs, documentation, generated values, tables and figures, powers-of-tau files, proofs, public inputs and calldata | CC BY 4.0 | `LICENSES/CC-BY-4.0.txt` |

Objects that are not stored in the repository follow the same rules once present: the regenerable PLONK proving keys
and the FFLONK proving keys fall under rule 4, the research powers-of-tau file under rule 7.

Copyright for rules 6 and 7: © 2026 Khoa Tan VO, Hong-Tri Nguyen and Tu-Anh Nguyen-Hoang.

Third-party tools used to produce the material (compilers, nodes, libraries) are not redistributed; they are pinned in
`provenance/EXTERNAL-PINS.tsv` and are subject to their own licences.
