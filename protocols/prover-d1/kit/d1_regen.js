'use strict';
// V2-PRV-D1-01: regenerate the four PLONK proving keys inside the D1 image (untimed; deterministic from the frozen R1CS
// and pot16_final.ptau). The host then compares them with KEYS-SHA256SUMS before any timed round.
//   node --max-old-space-size=7000 /opt/zcorp-d1/d1_regen.js       (mounts: /d1art ro, /pot16.ptau ro, /d1keys rw)
const fs = require('fs'); const path = require('path');
(async () => {
  const snarkjs = require('snarkjs');
  for (const c of ['d10', 'p1150', 'p1180', 'd11']) {
    fs.mkdirSync(path.join('/d1keys', c), { recursive: true });
    const out = path.join('/d1keys', c, 'plonk.zkey'); if (fs.existsSync(out)) { console.log('exists', c); continue; }
    await snarkjs.plonk.setup(path.join('/d1art', c, 'circuit.r1cs'), '/pot16.ptau', out); console.log('regenerated', c);
  }
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
