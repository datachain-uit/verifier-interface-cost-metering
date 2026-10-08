'use strict';
// V2-PRV-D2-01 synthetic credential corpus (V2-D-18: synthetic records only; no V1 record is read or copied).
// Reproduces the FILE SCHEMA and SIZE CLASS of the corpus read by the unchanged input generator
// scripts/setup/generate_input_depth.js (records, leaf count 2^d, full proof list), so that the v3 input stage
// performs the same kind and amount of work on Host B as on Host A. Values are synthetic and deterministic in SEED.
//
//   node d2_synthetic_corpus.js <circomlibjs node_modules dir> <repo dir>
// writes  <repo>/data/merkle-trees/processed_diplomas_<2^d>.json   (d = 5..15; first 2^d records of one sequence)
//         <repo>/data/merkle-trees/merkle_tree_data_depth_<d>.json
// Record i:  nameHash = Poseidon([s_name(i)])  (a field element, as a Poseidon output in the original schema)
//            majorCode = (i mod 5) + 1;  studentId = 8-digit string;  issueDate = YYYYMMDD string (2015-01-01 .. 2025-12-31)
//            leafHash = Poseidon([nameHash, majorCode, studentId, issueDate])
// Tree: node = Poseidon([left, right]); proof of leaf i: pathIndices[l] = bit l of i, siblings[l] = sibling at level l
// (the convention of CredentialVerifier: bit 0 -> hash(cur, sib), bit 1 -> hash(sib, cur)). JSON.stringify(x, null, 2).
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const [NM, REPO] = process.argv.slice(2);
if (!NM || !REPO) { console.error('usage: node d2_synthetic_corpus.js <circomlibjs node_modules dir> <repo dir>'); process.exit(2); }
const { buildPoseidon } = require(path.join(NM, 'circomlibjs'));
const SEED = 'V2-D2-synthetic-corpus-2026-10-04';
const DEPTHS = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
const u = (label, i) => BigInt('0x' + crypto.createHash('sha256').update(`${SEED}|${label}|${i}`).digest('hex'));
const DAY0 = Date.UTC(2015, 0, 1); const NDAYS = Math.round((Date.UTC(2025, 11, 31) - DAY0) / 86400000) + 1;
(async () => {
  const P = await buildPoseidon(); const F = P.F;
  const H = (xs) => F.toObject(P(xs.map((x) => F.e(x))));
  const N = 2 ** Math.max(...DEPTHS);
  const recs = new Array(N);
  for (let i = 0; i < N; i++) {
    const nameHash = H([u('name', i) % (1n << 248n)]);
    const majorCode = (i % 5) + 1;
    const studentId = String(20000000n + (u('studentId', i) % 80000000n));
    const day = new Date(DAY0 + Number(u('issueDate', i) % BigInt(NDAYS)) * 86400000);
    const issueDate = `${day.getUTCFullYear()}${String(day.getUTCMonth() + 1).padStart(2, '0')}${String(day.getUTCDate()).padStart(2, '0')}`;
    const leaf = H([nameHash, BigInt(majorCode), BigInt(studentId), BigInt(issueDate)]);
    recs[i] = { nameHash: nameHash.toString(), majorCode, studentId, issueDate, leafHash: leaf.toString(), _leaf: leaf };
  }
  const dir = path.join(REPO, 'data', 'merkle-trees'); fs.mkdirSync(dir, { recursive: true });
  for (const d of DEPTHS) {
    const n = 2 ** d;
    const layers = [recs.slice(0, n).map((r) => r._leaf)];
    for (let l = 0; l < d; l++) { const prev = layers[l]; const next = []; for (let j = 0; j < prev.length; j += 2) next.push(H([prev[j], prev[j + 1]])); layers.push(next); }
    const root = layers[d][0];
    const proofs = [];
    for (let i = 0; i < n; i++) {
      const pathIndices = []; const siblings = []; let idx = i;
      for (let l = 0; l < d; l++) { pathIndices.push(idx & 1); siblings.push(layers[l][idx ^ 1].toString()); idx >>= 1; }
      proofs.push({ leaf: layers[0][i].toString(), pathIndices, siblings });
    }
    const processed = recs.slice(0, n).map(({ nameHash, majorCode, studentId, issueDate, leafHash }) => ({ nameHash, majorCode, studentId, issueDate, leafHash }));
    fs.writeFileSync(path.join(dir, `processed_diplomas_${n}.json`), JSON.stringify(processed, null, 2));
    fs.writeFileSync(path.join(dir, `merkle_tree_data_depth_${d}.json`),
      JSON.stringify({ depth: d, root: root.toString(), totalLeaves: n, realLeaves: n, leaves: layers[0].map(String), proofs }, null, 2));
    console.log(`depth ${d}: ${n} leaves, root ${root.toString().slice(0, 12)}...`);
  }
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
