# 14 — Proof corpus specification (V2-C1, frozen)

Files: `corpus/gen_corpus.js` (inputs), `corpus/prove_corpus.js` + `corpus/prove_all.sh` (proofs),
`corpus/corpus_calldata.js` (calldata of every registered transaction), `corpus/corpus-manifest.json`,
`corpus/inputs/<relation>/j<j>.json`, `corpus/proofs/<circuit>/<backend>-j<j>.json`, `corpus/corpus-calldata.json`,
`corpus/CORPUS-SHA256SUMS`.

## 1. Synthetic instances

- **8 logical instances** j = 0…7 (the P0-supported number of proofs per cell).
- **Synthetic records only.** No V1 record, V1 seed or V1-derived file is used. Every value is
  v(label, j, i) = SHA-256("V2-C1-corpus-2026-10-04|label|j|i") reduced to the stated bit length and modulo r (BN254).
  Values therefore do not depend on generation order.
- Record of instance j: nameHash (248-bit), majorCode (16-bit), studentId (32-bit), issueDate = 1,700,000,000 + 20-bit
  value. The same record is used by every relation (anchors add holderSecret, scope, message, issuerId, validUntil from
  the same seed rule; `disc` uses the record as attributes 0–3 plus 28 seeded attributes).
- Merkle path: leaf index (37·j + 5) mod 2¹¹; 11 seeded sibling values; root computed with Poseidon₂ (V1 hashing).
  The path is synthetic (siblings are not other members' leaves); the verifier relation only checks path consistency.
- Context tags: one fixed vector of 63 seeded 248-bit tags per instance; circuit k uses the first k − 1 (nested).
  248-bit values have a zero top byte, so each tag contributes one zero calldata byte; this is part of the corpus and is
  accounted for exactly in the EVM predictions (`06-…`).

## 2. Proofs

- One proof per (circuit, backend, j): **matched witnesses** (the same input file for Groth16, PLONK and, if run,
  FFLONK).
- **Stable proof ID:** `<circuit>/<backend>/j<j>` (stored inside each proof file and in every evidence record).
- Generated once, before the pilot, with the frozen keys; each proof verified off-chain at generation
  (`corpus/prove-log.jsonl`, all 208 `ok: true`). PLONK proofs are randomised by snarkjs at generation; the generated files are
  then frozen, so no regime ever sees a regenerated proof.
- The same proof file is submitted in every regime (EVM, EraVM v29 / v27, ZKsync OS at every npg level).
- Proving times recorded during generation are **not** prover evidence (shared 2-vCPU host).

## 3. Order and use

- Within a cell: roots added for j = 0…7, then `verifyCredential` j = 0…7, then direct `verifyProof` j = 0…7, then
  controls. Cell order: `03-…` §5 (deterministic permutation).
- **No outcome-based exclusion.** Every proof of every cell is scored. A proof that fails in a regime where it verified
  off-chain is a deviation (`20-…`), never silently dropped.
- **Replays** (the same proof sent again in the same cell) are controls, not replicates; they are excluded from cell
  means by design (role `replay` in the schema), and reported.

## 4. Calldata

`corpus/corpus-calldata.json` lists, for every proof, the direct-call and manager-call calldata length, zero-byte count,
intrinsic calldata gas (16/4) and the calldata sha256. Predictions for EVM gasUsed add the exact registered calldata
gas to the modelled execution gas.

## 5. FFLONK (conditional)

If the FFLONK gate passes, FFLONK proofs for `c1_ff_kKK` use the **same** input files as `c1_k01` / `c1_ctx_kKK`
(instances j = 0…7), and are added under the same ID rule. Their hashes are appended to the corpus manifest by an
amendment record before any FFLONK measurement.
