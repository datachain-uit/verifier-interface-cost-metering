// V2 AMD-FF-1: FFLONK corpus proofs (8 per circuit, frozen C1 inputs j0..j7), each verified off-chain. Artifact production only:
// no timing is recorded. Proof ID = <circuit>/fflonk/j<j>; file format identical to the C1 corpus (id, proof, publicSignals).
const fs = require('fs'), path = require('path');
const W = process.env.HOME + '/Workspace/Z-CORP-V2-workstation', F = W + '/fflonk', I = W + '/inputs/fflonk-inputs';
const snarkjs = require(W + '/toolchain/js/node_modules/snarkjs');
const [N, SRC, REL] = process.argv.slice(2);
(async () => {
  const out = path.join(F, 'proofs', N); fs.mkdirSync(out, { recursive: true });
  const vk = JSON.parse(fs.readFileSync(path.join(F, 'keys', N, 'fflonk.vkey.json')));
  for (let j = 0; j < 8; j++) {
    const f = path.join(out, `fflonk-j${j}.json`); if (fs.existsSync(f)) throw new Error('refusing to overwrite ' + f);
    const inp = JSON.parse(fs.readFileSync(path.join(I, 'corpus-inputs', REL, `j${j}.json`)));
    const { proof, publicSignals } = await snarkjs.fflonk.fullProve(inp, path.join(I, 'wasm', SRC + '.wasm'), path.join(F, 'keys', N, 'fflonk.zkey'));
    const ok = await snarkjs.fflonk.verify(vk, publicSignals, proof);
    fs.writeFileSync(f, JSON.stringify({ id: `${N}/fflonk/j${j}`, proof, publicSignals }) + '\n');
    fs.appendFileSync(path.join(F, 'prove-log.jsonl'), JSON.stringify({ id: `${N}/fflonk/j${j}`, ok, nPub: publicSignals.length }) + '\n');
    if (!ok) { console.error('OFF-CHAIN VERIFY FAILED', N, j); process.exit(2); }
  }
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
