# Identifiers inside frozen records

Some immutable scientific records retain historical internal identifiers because changing those files would invalidate
their frozen identity. These labels are provenance identifiers only and are not external dependencies of the present
article.

They include campaign and package names, protocol and kit version tags, names used inside frozen code (environment
variables, container image and directory names), references to internal notes, decisions or records that are not part
of this artifact, and the workspace paths at which the records were produced. They are kept verbatim because every frozen manifest, and
every record that cites another record by hash, depends on these exact bytes.

How to read them:

- A path or package name cited inside a frozen record is resolved with `PATH-MAP.tsv`, which maps each original location
  to its published location.
- A frozen package is identified by the SHA-256 of its manifest (`PACKAGES.tsv`, Table S8), not by its name.
- A reference to a record that is not published has no bearing on the reported results: every value, table and figure
  is derived from published files only (`generated/MANIFEST.json` lists every input read), and withheld records are listed
  in `WITHHELD.tsv`.

The same applies to the verbatim copies of earlier files whose identity frozen records fix by hash: the prover kit in
`protocols/prover-procedure/kit/` (file hashes recorded in `data/prover/d3/source/CAMPAIGN.json`), the setup scripts in
`setup/prover-objects/scripts/setup/` and the D3 source files. Files written for this artifact (this directory,
`analysis/`, `scoring/`, `scripts/`, the top-level documents) use the neutral package names of `PACKAGES.tsv`; where a
tool must name a frozen file or a frozen directory layout, it uses the frozen name.
