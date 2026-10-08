// V2-PRV-D1-01 synthetic inputs (synthetic records only, V2-D-18; same construction as the C1 corpus generator).
// One instance per depth (leaf index 5), deterministic in SEED. Padded circuits use the d = 10 input plus padSeed.
// usage: node d1_inputs.js <circomlibjs node_modules dir> <out dir>
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const [NM, OUT] = process.argv.slice(2); const { buildPoseidon } = require(path.join(NM, 'circomlibjs'));
const R = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const SEED = 'V2-D1-inputs-2026-10-04';
const v = (label, i = 0, bits = 248) => BigInt('0x' + crypto.createHash('sha256').update(`${SEED}|${label}|${i}`).digest('hex')) % (1n << BigInt(bits)) % R;
(async () => {
  const P = await buildPoseidon(); const F = P.F; const H = (xs) => F.toObject(P(xs.map((x) => F.e(x))));
  const S = (o) => JSON.parse(JSON.stringify(o, (k, x) => typeof x === 'bigint' ? x.toString() : x));
  const rec = { nameHash: v('nameHash'), majorCode: v('majorCode', 0, 16), studentId: v('studentId', 0, 32), issueDate: 1700000000n + v('issueDate', 0, 20) };
  const leaf = H([rec.nameHash, rec.majorCode, rec.studentId, rec.issueDate]);
  fs.mkdirSync(OUT, { recursive: true });
  for (const D of [10, 11]) {
    const idx = 5; const pathIndices = [], siblings = []; let cur = leaf;
    for (let l = 0; l < D; l++) { const bit = (idx >> l) & 1; const sib = v(`sibling-d${D}`, l); pathIndices.push(bit); siblings.push(sib); cur = bit ? H([sib, cur]) : H([cur, sib]); }
    const inp = { ...rec, pathIndices, siblings, root: cur };
    fs.writeFileSync(path.join(OUT, `input_d${D}.json`), JSON.stringify(S(inp), null, 1) + '\n');
    if (D === 10) fs.writeFileSync(path.join(OUT, 'input_pad.json'), JSON.stringify(S({ padSeed: v('padSeed'), ...inp }), null, 1) + '\n');
  }
  console.log('inputs written'); process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
