'use strict';
// kit v3-x86 (Host B setup, untimed): regenerate the 11 PLONK proving keys of the v3 artifact set, deterministic from the
// committed R1CS and pot16_final.ptau (v3 protocol §1.2; P7 checks the same regeneration). The runner then checks every
// key against ARTIFACTS.sha256. Mounts: /work (repository, read-only), /out (= data/plonk-zkeys, writable).
const fs = require('fs'); const path = require('path');
(async () => {
  const snarkjs = require('snarkjs');
  for (let d = 5; d <= 15; d++) {
    const b = `CredentialVerifier_Depth${d}`; const out = path.join('/out', `${b}_plonk.zkey`);
    if (fs.existsSync(out)) { console.log(`exists ${b}`); continue; }
    const t0 = Date.now();
    await snarkjs.plonk.setup(path.join('/work/data/zkp-circuits', b, `${b}.r1cs`), '/work/pot16_final.ptau', out + '.tmp');
    fs.renameSync(out + '.tmp', out); console.log(`regenerated ${b} (${Math.round((Date.now() - t0) / 1000)} s, setup duration is not evidence)`);
  }
  if (globalThis.curve_bn128) await globalThis.curve_bn128.terminate();
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
