// Reproduce V1 EVM d=11 cells (V1 contracts + V1 public proof set) on EDR; diagnostic only.
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const { ethers } = require('./node/node_modules/ethers');
const S = require('./lib/solc'); const P = require('./lib/proofs');
const R = process.env.HOME + '/p0/research'; const PS = R + '/csi/campaigns/chain/CSI-CHAIN-LOCAL-01/inputs/proofset';
(async () => {
  const HF = process.argv[2] || 'osaka'; const d = Number(process.argv[3] || 11); const evmVersion = process.argv[4] || 'paris';
  const C = S.evm([`contracts/Groth16LegacyVerifierDepth${d}.sol`, `contracts/chain/PlonkVerifierDepth${d}.sol`, 'contracts/chain/CredentialManagerGroth16.sol', 'contracts/chain/CredentialManagerPlonk.sol'], { roots: [R], evmVersion });
  const results = {};
  for (const [backend, V, M, tag] of [['groth16', `Groth16LegacyVerifierDepth${d}`, 'CredentialManagerGroth16', 'G16'], ['plonk', `PlonkVerifierDepth${d}`, 'CredentialManagerPlonk', 'PLK']]) {
    const vI = new ethers.Interface(C[V].abi), mI = new ethers.Interface(C[M].abi);
    const proofs = [];
    for (let j = 0; j < 8; j++) { const pr = JSON.parse(fs.readFileSync(`${PS}/${backend}/d${d}/p${j}.proof.json`)); const pub = JSON.parse(fs.readFileSync(`${PS}/${backend}/d${d}/p${j}.public.json`)); proofs.push({ j, a: await P.args(backend, pr, pub), root: pub[0] }); }
    const A0 = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';
    const steps = [{ op: 'deploy_verifier', kind: 'deploy', contract: V, key: 'v' }, { op: 'deploy_manager', kind: 'deploy', contract: M, key: 'm', args: ['$v'] },
      { op: 'set_issuer', kind: 'tx', to: 'm', data: mI.encodeFunctionData('setIssuer', [A0, true]) }, { op: 'add_root', kind: 'tx', to: 'm', data: mI.encodeFunctionData('addRoot', [proofs[0].root]) }];
    for (const p of proofs) steps.push({ op: 'verify_credential', j: p.j, kind: 'tx', to: 'm', data: mI.encodeFunctionData('verifyCredential', p.a) });
    for (const p of proofs) steps.push({ op: 'verify_proof_direct', j: p.j, kind: 'tx', to: 'v', data: vI.encodeFunctionData('verifyProof', p.a), trace: p.j === 0 });
    steps.push({ op: 'neg_tampered_call', kind: 'call', to: 'v', data: vI.encodeFunctionData('verifyProof', P.tamperLast(backend, proofs[0].a)) });
    steps.push({ op: 'neg_pub_call', kind: 'call', to: 'v', data: vI.encodeFunctionData('verifyProof', P.perturbPub(backend, proofs[0].a, 0)) });
    steps.push({ op: 'valid_call', kind: 'call', to: 'v', data: vI.encodeFunctionData('verifyProof', proofs[0].a) });
    const job = { contracts: { [V]: C[V], [M]: C[M] }, steps };
    const jp = `/tmp/job-${backend}-${HF}.json`, op = `/tmp/out-${backend}-${HF}.json`; fs.writeFileSync(jp, JSON.stringify(job, (k, v) => typeof v === 'bigint' ? v.toString() : v));
    execFileSync('npx', ['hardhat', 'run', 'evm_run.js'], { cwd: process.env.HOME + '/p0/hh', env: { ...process.env, HF, JOB: jp, OUT: op }, stdio: 'inherit' });
    results[backend] = JSON.parse(fs.readFileSync(op));
  }
  const fmt = (b) => { const s = results[b].steps; const g = (o) => s.filter((x) => x.op === o).map((x) => x.gasUsed);
    return { deploy_verifier: g('deploy_verifier')[0], deploy_manager: g('deploy_manager')[0], verify_credential: g('verify_credential'), verify_proof_direct: g('verify_proof_direct'),
      calls: s.filter((x) => x.kind === 'call').map((x) => `${x.op}:${x.ok ? x.ret.slice(-1) : 'revert'}`), status: s.filter((x) => x.kind !== 'call').map((x) => x.status).join(''), trace_steps: (s.find((x) => x.trace) || {}).trace?.steps }; };
  const summary = { hardfork: HF, depth: d, evmVersion, groth16: fmt('groth16'), plonk: fmt('plonk') };
  fs.writeFileSync(`${process.env.HOME}/p0/out/v1repro-evm-${HF}-d${d}-${evmVersion}.json`, JSON.stringify({ summary, raw: results }, null, 1));
  console.log(JSON.stringify(summary, null, 1));
})().catch((e) => { console.error(e); process.exit(1); });
