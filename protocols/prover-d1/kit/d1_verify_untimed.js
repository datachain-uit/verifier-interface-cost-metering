// V2-PRV-D1-01: untimed proof generation and off-chain verification for every (cell, backend). Not timing evidence.
// usage: node d1_verify_untimed.js <snarkjs module dir> <artifacts dir>
const path = require('path'); const fs = require('fs');
const [SJ, A] = process.argv.slice(2); const snarkjs = require(SJ);
const CELLS = { d10: 'input_d10.json', p1150: 'input_pad.json', p1180: 'input_pad.json', d11: 'input_d11.json' };
(async () => {
  const out = [];
  for (const [cell, inp] of Object.entries(CELLS)) {
    const input = JSON.parse(fs.readFileSync(path.join(A, 'inputs', inp)));
    for (const b of ['groth16', 'plonk']) {
      const { proof, publicSignals } = await snarkjs[b].fullProve(input, path.join(A, cell, 'circuit.wasm'), path.join(A, cell, `${b}.zkey`));
      const vk = JSON.parse(fs.readFileSync(path.join(A, cell, `${b}.vkey.json`)));
      const ok = await snarkjs[b].verify(vk, publicSignals, proof);
      const r = { cell, backend: b, verified: ok, public_signals: publicSignals, root_matches_input: publicSignals.length === 1 && publicSignals[0] === input.root };
      out.push(r); console.log(JSON.stringify(r));
    }
  }
  fs.writeFileSync(path.join(A, '..', 'D1-UNTIMED-PROOF-CHECK.json'), JSON.stringify(out, null, 1) + '\n');
  process.exit(out.every((r) => r.verified && r.root_matches_input) ? 0 : 2);
})().catch((e) => { console.error(e); process.exit(1); });
