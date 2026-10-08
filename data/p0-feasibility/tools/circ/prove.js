// Synthetic witness + proofs for the P0 circuit family (synthetic records only; no V1 data).
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const NM = process.env.HOME + '/p0/node/node_modules';
const snarkjs = require(NM + '/snarkjs'); const { buildPoseidon } = require(NM + '/circomlibjs');
const R = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
let seedCounter = 0; const SEED = process.env.SEED || 'p0-synthetic-2026-10-04';
const rnd = (bits = 248) => { const h = crypto.createHash('sha256').update(SEED + ':' + (seedCounter++)).digest(); return BigInt('0x' + h.toString('hex')) % (1n << BigInt(bits)) % R; };
(async () => {
  const [name, kind, k, nproofs, backendsArg] = process.argv.slice(2); const K = Number(k); const NP = Number(nproofs || 2);
  const backends = (backendsArg || 'groth16,plonk').split(',');
  const P = await buildPoseidon(); const F = P.F; const H = (xs) => F.toObject(P(xs.map((x) => F.e(x))));
  const d = Number((/_d(\d+)/.exec(name) || [0, 11])[1]);
  const outDir = path.join(__dirname, 'proofs', name); fs.mkdirSync(outDir, { recursive: true });
  const rows = [];
  for (let j = 0; j < NP; j++) {
    const inp = {}; let leaf;
    if (kind === 'v1' || kind === 'ctx') {
      Object.assign(inp, { nameHash: rnd(), majorCode: rnd(16), studentId: rnd(32), issueDate: rnd(32) });
      leaf = H([inp.nameHash, inp.majorCode, inp.studentId, inp.issueDate]);
      if (kind === 'ctx') inp.tag = Array.from({ length: K - 1 }, () => rnd());
    } else if (kind === 'mini') {
      Object.assign(inp, { nameHash: rnd(), majorCode: rnd(16), studentId: rnd(32), issueDate: rnd(32) });
      leaf = H([inp.nameHash, inp.majorCode, inp.studentId, inp.issueDate]); if (K > 1) inp.tag = Array.from({ length: K - 1 }, () => rnd());
    } else if (kind === 'disc') {
      const attr = Array.from({ length: 32 }, () => rnd()); const h0 = H(attr.slice(0, 16)), h1 = H(attr.slice(16)); leaf = H([h0, h1]);
      if (K > 1) inp.attrPub = attr.slice(0, K - 1); inp.attrPriv = attr.slice(K - 1);
    } else if (kind === 'a4' || kind === 'a8') {
      const s = rnd(), scope = rnd(); Object.assign(inp, { nameHash: rnd(), majorCode: rnd(16), studentId: rnd(32), issueDate: 1700000000n + rnd(20), holderSecret: s, scope, message: rnd(), nullifier: H([s, scope]) });
      if (kind === 'a4') leaf = H([inp.nameHash, inp.majorCode, inp.studentId, inp.issueDate, s]);
      else { Object.assign(inp, { issuerId: rnd(32), validUntil: 1900000000n + rnd(20), minIssueDate: 1600000000n, epoch: 1800000000n }); leaf = H([inp.nameHash, inp.majorCode, inp.studentId, inp.issueDate, s, inp.issuerId, inp.validUntil]); }
    }
    // synthetic Merkle path: leaf index j*37 mod 2^d, random siblings
    if (kind === 'mini') { Object.assign(inp, { root: leaf }); } else {
    const idx = (j * 37 + 5) % (2 ** d); const pathIndices = [], siblings = []; let cur = leaf;
    for (let l = 0; l < d; l++) { const bit = (idx >> l) & 1; const sib = rnd(); pathIndices.push(bit); siblings.push(sib); cur = bit ? H([sib, cur]) : H([cur, sib]); }
    Object.assign(inp, { pathIndices, siblings, root: cur }); }
    const norm = JSON.parse(JSON.stringify(inp, (kk, v) => typeof v === 'bigint' ? v.toString() : v));
    for (const b of backends) {
      const zkey = path.join(__dirname, 'keys', name, `${b}.zkey`); const wasm = path.join(__dirname, 'build', name, `${name}_js`, `${name}.wasm`);
      const t0 = Date.now(); const { proof, publicSignals } = await snarkjs[b].fullProve(norm, wasm, zkey); const ms = Date.now() - t0;
      const vk = JSON.parse(fs.readFileSync(path.join(__dirname, 'keys', name, `${b}.vkey.json`)));
      const ok = await snarkjs[b].verify(vk, publicSignals, proof);
      fs.writeFileSync(path.join(outDir, `${b}-p${j}.json`), JSON.stringify({ proof, publicSignals }));
      rows.push({ name, b, j, ok, ms, nPub: publicSignals.length });
    }
  }
  console.log(JSON.stringify(rows)); process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
