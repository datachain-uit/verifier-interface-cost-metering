// V2-C1 corpus proofs: one proof per (relation circuit, backend, instance j); matched witness for all backends.
// Proof ID = <circuit>/<backend>/j<j>. Off-chain verification recorded. Timing is NOT prover evidence (shared host).
const fs = require('fs'); const path = require('path');
const NM = process.env.HOME + '/p0/node/node_modules'; const snarkjs = require(NM + '/snarkjs');
const C = path.join(process.env.HOME, 'c1/circ');
const man = JSON.parse(fs.readFileSync(path.join(__dirname, 'corpus-manifest.json')));
(async () => {
  const [rel, backendsArg] = process.argv.slice(2); const name = man.relations[rel]; const backends = (backendsArg || 'groth16,plonk').split(',');
  const outDir = path.join(__dirname, 'proofs', name); fs.mkdirSync(outDir, { recursive: true });
  for (let j = 0; j < man.n_instances; j++) {
    const inp = JSON.parse(fs.readFileSync(path.join(__dirname, 'inputs', rel, `j${j}.json`)));
    for (const b of backends) {
      const f = path.join(outDir, `${b}-j${j}.json`); if (fs.existsSync(f)) continue;
      const zkey = path.join(C, 'keys', name, `${b}.zkey`); const wasm = path.join(C, 'build', name, `${name}_js`, `${name}.wasm`);
      const t0 = Date.now(); const { proof, publicSignals } = await snarkjs[b].fullProve(inp, wasm, zkey); const ms = Date.now() - t0;
      const vk = JSON.parse(fs.readFileSync(path.join(C, 'keys', name, `${b}.vkey.json`))); const ok = await snarkjs[b].verify(vk, publicSignals, proof);
      fs.writeFileSync(f, JSON.stringify({ id: `${name}/${b}/j${j}`, proof, publicSignals }) + '\n');
      fs.appendFileSync(path.join(process.env.HOME, 'c1/logs/prove.jsonl'), JSON.stringify({ id: `${name}/${b}/j${j}`, ok, nPub: publicSignals.length, ms }) + '\n');
    }
  }
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
