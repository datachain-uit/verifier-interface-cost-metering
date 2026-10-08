// V2 AMD-FF-1 cloud re-verification (G3, second check): every transferred FFLONK proof verifies off-chain with the
// pinned snarkjs 0.7.5 and its vkey; proof id / public-signal count = k; public signals equal the frozen C1 corpus
// signals of the same relation and instance (Groth16 proof j of c1_k01 / c1_ctx_kKK). No timing is recorded.
// usage: node ff_cloud_verify.js <transfer dir> <C1 corpus proofs dir> <out.json>
const fs = require('fs'), path = require('path');
const snarkjs = require(process.env.HOME + '/p0/node/node_modules/snarkjs');
const [T, CORP, OUT] = process.argv.slice(2);
const MAP = { c1_ff_k01: ['c1_k01', 1], c1_ff_k04: ['c1_ctx_k04', 4], c1_ff_k16: ['c1_ctx_k16', 16], c1_ff_k32: ['c1_ctx_k32', 32] };
(async () => {
  const rows = [];
  for (const [N, [SRC, k]] of Object.entries(MAP)) {
    const vk = JSON.parse(fs.readFileSync(path.join(T, 'keys', N, 'fflonk.vkey.json')));
    for (let j = 0; j < 8; j++) {
      const p = JSON.parse(fs.readFileSync(path.join(T, 'proofs', N, `fflonk-j${j}.json`)));
      const g = JSON.parse(fs.readFileSync(path.join(CORP, SRC, `groth16-j${j}.json`)));
      const ok = await snarkjs.fflonk.verify(vk, p.publicSignals, p.proof);
      rows.push({ id: p.id, id_ok: p.id === `${N}/fflonk/j${j}`, k, n_public: p.publicSignals.length, n_public_ok: p.publicSignals.length === k,
        signals_equal_corpus: JSON.stringify(p.publicSignals) === JSON.stringify(g.publicSignals), protocol: p.proof.protocol, curve: p.proof.curve, verified: ok === true,
        vkey_power: vk.power, vkey_nPublic: vk.nPublic });
    }
  }
  const all = rows.every((r) => r.id_ok && r.n_public_ok && r.signals_equal_corpus && r.verified && r.protocol === 'fflonk');
  fs.writeFileSync(OUT, JSON.stringify({ label: 'AMD-FF-1 G3 cloud re-verification (snarkjs 0.7.5)', proofs: rows.length, all_pass: all, rows }, null, 1) + '\n');
  console.log(`proofs ${rows.length} all_pass ${all}`); if (globalThis.curve_bn128) await globalThis.curve_bn128.terminate(); process.exit(all ? 0 : 1);
})().catch((e) => { console.error(e); process.exit(1); });
