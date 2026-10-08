// Reproduce V1 EraVM d=11 cells (V1 contracts + V1 public proof set) on anvil-zksync 0.6.11; diagnostic only.
const fs = require('fs'); const { ethers } = require('./node/node_modules/ethers');
const S = require('./lib/solc'); const P = require('./lib/proofs'); const E = require('./lib/eravm');
const R = process.env.HOME + '/p0/research'; const PS = R + '/csi/campaigns/chain/CSI-CHAIN-LOCAL-01/inputs/proofset';
(async () => {
  const protocol = Number(process.argv[2] || 29); const d = Number(process.argv[3] || 11);
  const C = S.zk([`contracts/Groth16LegacyVerifierDepth${d}.sol`, `contracts/chain/PlonkVerifierDepth${d}.sol`, 'contracts/chain/CredentialManagerGroth16.sol', 'contracts/chain/CredentialManagerPlonk.sol'], { roots: [R] });
  const res = { protocol, depth: d, sizes: Object.fromEntries(Object.entries(C).map(([n, c]) => [n, { bytes: c.bytes, hash: c.hash }])) };
  for (const [backend, V, M] of [['groth16', `Groth16LegacyVerifierDepth${d}`, 'CredentialManagerGroth16'], ['plonk', `PlonkVerifierDepth${d}`, 'CredentialManagerPlonk']]) {
    const node = await E.start({ protocol, logFile: `/tmp/anvil-${backend}-${protocol}.log` });
    try {
      const s = await E.session(node); const vI = new ethers.Interface(C[V].abi), mI = new ethers.Interface(C[M].abi);
      const proofs = []; for (let j = 0; j < 8; j++) { const pr = JSON.parse(fs.readFileSync(`${PS}/${backend}/d${d}/p${j}.proof.json`)); const pub = JSON.parse(fs.readFileSync(`${PS}/${backend}/d${d}/p${j}.public.json`)); proofs.push({ j, a: await P.args(backend, pr, pub), root: pub[0] }); }
      const rows = [];
      const dv = await s.tx({ create: C[V], gasLimit: 200000000n }); rows.push({ op: 'deploy_verifier', ...dv });
      const dm = await s.tx({ create: { ...C[M], ctor: ethers.AbiCoder.defaultAbiCoder().encode(['address'], [dv.contractAddress]) }, gasLimit: 200000000n }); rows.push({ op: 'deploy_manager', ...dm });
      rows.push({ op: 'set_issuer', ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('setIssuer', [s.W[0].address, true]) })) });
      rows.push({ op: 'add_root', ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('addRoot', [proofs[0].root]) })) });
      for (const p of proofs) rows.push({ op: 'verify_credential', j: p.j, ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('verifyCredential', p.a) })) });
      for (const p of proofs) rows.push({ op: 'verify_proof_direct', j: p.j, ...(await s.tx({ to: dv.contractAddress, data: vI.encodeFunctionData('verifyProof', p.a), trace: p.j === 0 })) });
      const calls = { tampered: await s.call(dv.contractAddress, vI.encodeFunctionData('verifyProof', P.tamperLast(backend, proofs[0].a))), pub: await s.call(dv.contractAddress, vI.encodeFunctionData('verifyProof', P.perturbPub(backend, proofs[0].a, 0))), valid: await s.call(dv.contractAddress, vI.encodeFunctionData('verifyProof', proofs[0].a)) };
      await new Promise((r) => setTimeout(r, 500)); await node.stop();
      const fee = E.feeRecords(node);
      for (const r of rows) Object.assign(r, fee.get(r.hash) || { computational_gas: null });
      res[backend] = { rows: rows.map(({ trace, ...x }) => x), trace0: rows.find((r) => r.trace)?.trace, calls };
    } finally { await node.stop(); }
  }
  fs.writeFileSync(`${process.env.HOME}/p0/out/v1repro-eravm-v${protocol}-d${d}.json`, JSON.stringify(res, null, 1));
  for (const b of ['groth16', 'plonk']) { const R2 = res[b].rows; const g = (o, k) => R2.filter((x) => x.op === o).map((x) => x[k]);
    console.log(b, 'status', R2.map((x) => x.status).join(''), 'deployV comp', g('deploy_verifier', 'computational_gas'), 'VC comp', g('verify_credential', 'computational_gas'), 'VPD comp', g('verify_proof_direct', 'computational_gas'), 'pubdata', g('verify_proof_direct', 'pubdata_bytes'), 'calls', JSON.stringify(Object.fromEntries(Object.entries(res[b].calls).map(([k, v]) => [k, v.ok ? v.ret.slice(-1) : 'revert'])))); }
  console.log("sizes", JSON.stringify(res.sizes)); process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
