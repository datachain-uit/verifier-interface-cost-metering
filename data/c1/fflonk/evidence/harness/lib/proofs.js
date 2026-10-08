// Calldata helpers for snarkjs proofs (Groth16 / PLONK / FFLONK). V2-C1 pilot harness copy of the P0 helper; adds outOfField (17-negative-control-protocol.md).
const snarkjs = require(process.env.HOME + '/p0/node/node_modules/snarkjs');
async function args(backend, proof, pub) {
  if (backend === 'groth16') return JSON.parse('[' + (await snarkjs.groth16.exportSolidityCallData(proof, pub)) + ']');
  if (backend === 'plonk') return JSON.parse('[' + (await snarkjs.plonk.exportSolidityCallData(proof, pub)).replace('][', '],[') + ']');
  if (backend === 'fflonk') return JSON.parse('[' + String(await snarkjs.fflonk.exportSolidityCallData(pub, proof)).replace(/0x[0-9a-fA-F]+/g, (m) => '"' + m + '"') + ']');
  throw new Error(backend);
}
const Q = 21888242871839275222246405745257275088696311157297823662689037894645226208583n;
const R = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const hex32 = (x) => '0x' + BigInt(x).toString(16).padStart(64, '0');
function tamperLast(backend, a) { // V1 rule: last proof word w -> w+1 (or w-1)
  a = JSON.parse(JSON.stringify(a));
  if (backend === 'groth16') { const w = BigInt(a[2][1]); a[2][1] = hex32(w + 1n < Q ? w + 1n : w - 1n); }
  else { const w = BigInt(a[0][a[0].length - 1]); a[0][a[0].length - 1] = hex32(w + 1n < R ? w + 1n : w - 1n); }
  return a;
}
function perturbPub(backend, a, i) { // public input i -> +1 mod r
  a = JSON.parse(JSON.stringify(a)); const idx = backend === 'groth16' ? 3 : 1;
  a[idx][i] = hex32((BigInt(a[idx][i]) + 1n) % R); return a;
}
function outOfField(backend, a, i) { // public input i -> x + r (non-canonical, < 2^256)
  a = JSON.parse(JSON.stringify(a)); const idx = backend === 'groth16' ? 3 : 1;
  a[idx][i] = hex32(BigInt(a[idx][i]) + R); return a;
}
module.exports = { args, tamperLast, perturbPub, outOfField, hex32, Q, R };
