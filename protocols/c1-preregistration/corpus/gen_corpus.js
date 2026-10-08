// V2-C1 proof corpus: frozen synthetic instances (synthetic records only; no V1 records or seed-derived data).
// Every value is a deterministic function of (SEED, label, instance j, index i) -> the same logical instance j is
// used by every relation, backend and regime; context tags are nested (k uses tags 0..k-2 of instance j).
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const NM = process.env.HOME + '/p0/node/node_modules'; const { buildPoseidon } = require(NM + '/circomlibjs');
const R = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const SEED = 'V2-C1-corpus-2026-10-04'; const NINST = 8; const D = 11; const MAXTAGS = 63;
const v = (label, j, i = 0, bits = 248) => BigInt('0x' + crypto.createHash('sha256').update(`${SEED}|${label}|${j}|${i}`).digest('hex')) % (1n << BigInt(bits)) % R;
(async () => {
  const P = await buildPoseidon(); const F = P.F; const H = (xs) => F.toObject(P(xs.map((x) => F.e(x))));
  const out = path.join(__dirname, 'inputs'); fs.mkdirSync(out, { recursive: true });
  const S = (o) => JSON.parse(JSON.stringify(o, (kk, x) => typeof x === 'bigint' ? x.toString() : x));
  const manifest = { seed: SEED, n_instances: NINST, depth: D, relations: {}, instances: [] };
  for (let j = 0; j < NINST; j++) {
    const rec = { nameHash: v('nameHash', j), majorCode: v('majorCode', j, 0, 16), studentId: v('studentId', j, 0, 32), issueDate: 1700000000n + v('issueDate', j, 0, 20) };
    const holderSecret = v('holderSecret', j), scope = v('scope', j), message = v('message', j);
    const issuerId = v('issuerId', j, 0, 32), validUntil = 1900000000n + v('validUntil', j, 0, 20);
    const tags = Array.from({ length: MAXTAGS }, (_, i) => v('tag', j, i));
    const attr = [rec.nameHash, rec.majorCode, rec.studentId, rec.issueDate, ...Array.from({ length: 28 }, (_, i) => v('attr', j, i + 4))];
    const idx = (j * 37 + 5) % (2 ** D); const sib = Array.from({ length: D }, (_, l) => v('sibling', j, l));
    const path_ = (leaf) => { const pathIndices = [], siblings = []; let cur = leaf; for (let l = 0; l < D; l++) { const bit = (idx >> l) & 1; pathIndices.push(bit); siblings.push(sib[l]); cur = bit ? H([sib[l], cur]) : H([cur, sib[l]]); } return { pathIndices, siblings, root: cur }; };
    const leafV1 = H([rec.nameHash, rec.majorCode, rec.studentId, rec.issueDate]);
    const I = {};
    I.v1 = { ...rec, ...path_(leafV1) };
    for (const k of [2, 4, 6, 8, 12, 16, 24, 32, 64]) I['ctx_k' + k] = { ...rec, ...path_(leafV1), tag: tags.slice(0, k - 1) };
    I.a4 = { ...rec, holderSecret, ...path_(H([rec.nameHash, rec.majorCode, rec.studentId, rec.issueDate, holderSecret])), nullifier: H([holderSecret, scope]), scope, message };
    I.a8 = { nameHash: rec.nameHash, studentId: rec.studentId, issueDate: rec.issueDate, holderSecret, validUntil, ...path_(H([rec.nameHash, rec.majorCode, rec.studentId, rec.issueDate, holderSecret, issuerId, validUntil])),
             nullifier: H([holderSecret, scope]), scope, message, majorCode: rec.majorCode, issuerId, minIssueDate: 1600000000n, epoch: 1800000000n };
    const h0 = H(attr.slice(0, 16)), h1 = H(attr.slice(16)); I.disc_k4 = { ...path_(H([h0, h1])), attrPub: attr.slice(0, 3), attrPriv: attr.slice(3) };
    for (const [rel, inp] of Object.entries(I)) { fs.mkdirSync(path.join(out, rel), { recursive: true }); fs.writeFileSync(path.join(out, rel, `j${j}.json`), JSON.stringify(S(inp), null, 1) + '\n'); }
    manifest.instances.push({ j, leaf_index: idx });
  }
  manifest.relations = { v1: 'c1_k01', ctx_k2: 'c1_ctx_k02', ctx_k4: 'c1_ctx_k04', ctx_k6: 'c1_ctx_k06', ctx_k8: 'c1_ctx_k08', ctx_k12: 'c1_ctx_k12', ctx_k16: 'c1_ctx_k16', ctx_k24: 'c1_ctx_k24', ctx_k32: 'c1_ctx_k32', ctx_k64: 'c1_ctx_k64', a4: 'c1_a4', a8: 'c1_a8', disc_k4: 'c1_disc_k04' };
  fs.writeFileSync(path.join(__dirname, 'corpus-manifest.json'), JSON.stringify(manifest, null, 1) + '\n'); console.log('ok'); process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
