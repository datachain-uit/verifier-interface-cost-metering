# Provenance tables

| File | Content |
|---|---|
| `PACKAGES.tsv` | the 28 frozen manifests of this artifact: package name, published path, manifest file, manifest SHA-256, entry count, and how entries map to published paths (`entry_prefix`, `remap`). The first 24 rows are the packages read or verified by the values derivation (Table S8). |
| `PATH-MAP.tsv` | original location (as cited inside frozen records) → published location, with the identity (manifest or file SHA-256) of each mapped directory or file |
| `LABELS.md` | how to read internal identifiers retained inside immutable frozen records |
| `OBJECT-CLASS.tsv` | every object of the artifact with exactly one class (`GIT`, `GIT-LFS`, `REGENERABLE`, `EXTERNAL-PIN`, `WITHHELD`), its SHA-256, size, status and the frozen manifest that lists it. External pins use the pseudo-path `pin:<id>`. The table does not list itself; `manifests/SHA256SUMS` does. |
| `LFS-OBJECTS.tsv` | the five objects stored with Git LFS: path, size, SHA-256, BLAKE2b-512, the frozen record that holds the SHA-256, and the source of each value. Public provenance derived from the read-only Host-B identity verification of the FFLONK setup objects; `OBJECT-CLASS.tsv` takes the size and SHA-256 of its `GIT-LFS` rows from this table |
| `WITHHELD.tsv` | records inside frozen packages that are not published: package, path within the package, SHA-256, size, status, reason |
| `REGENERABLE.tsv` | objects rebuilt deterministically instead of stored: path, frozen SHA-256, size where recorded, method, inputs and their SHA-256 |
| `EXTRACTS.tsv` | documents published as verbatim extracts: source path and SHA-256, included line ranges, method, extract path and SHA-256 |
| `LICENSE-MAP.tsv` | the licence of every published file, with the `LICENSE.md` rule that assigns it (`scripts/classify_licences.py`) |
| `EXTERNAL-PINS.tsv` | third-party tools, sources, images and fonts: version or identity, recorded SHA-256, use, the frozen file that records the pin, upstream location |

`scripts/verify-artifact.sh` checks `OBJECT-CLASS.tsv`, every manifest of `PACKAGES.tsv` and `manifests/SHA256SUMS`.
