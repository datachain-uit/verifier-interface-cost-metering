// Calldata of every corpus proof for the direct verifier call and the manager call (bytes, zero bytes, intrinsic calldata gas 16/4).
const fs = require('fs'); const path = require('path'); const HOME = process.env.HOME;
const { ethers } = require(HOME + '/p0/node/node_modules/ethers'); const P = require(HOME + '/p0/lib/proofs');
const sig = (b, k) => b === 'groth16' ? `(uint256[2],uint256[2][2],uint256[2],uint256[${k}])` : b === 'plonk' ? `(uint256[24],uint256[${k}])` : `(bytes32[24],uint256[${k}])`;
(async () => {
  const root = path.join(__dirname, 'proofs'); const out = {};
  for (const circ of fs.readdirSync(root).sort()) for (const f of fs.readdirSync(path.join(root, circ)).sort()) {
    const { id, proof, publicSignals } = JSON.parse(fs.readFileSync(path.join(root, circ, f))); const b = f.split('-')[0]; const k = publicSignals.length;
    const a = await P.args(b, proof, publicSignals); const r = {};
    for (const [m, fn] of [['dir', 'verifyProof'], ['app', 'verifyCredential']]) {
      const I = new ethers.Interface([`function ${fn}${sig(b, k)} returns (bool)`]);
      const data = I.encodeFunctionData(fn, a); const bytes = ethers.getBytes(data); const zero = bytes.filter((x) => x === 0).length;
      r[m] = { bytes: bytes.length, zero, gas: 16 * (bytes.length - zero) + 4 * zero, sha256: require('crypto').createHash('sha256').update(bytes).digest('hex') };
    }
    out[id] = { circuit: circ, backend: b, k, ...r };
  }
  fs.writeFileSync(path.join(__dirname, 'corpus-calldata.json'), JSON.stringify(out, null, 1) + '\n'); console.log(Object.keys(out).length); process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
