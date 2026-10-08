// P0 k-sweep feasibility runner: compile (solc / zksolc), deploy, verify, negative controls; EVM (EDR) and EraVM (anvil-zksync).
// usage: node run.js <evm|eravm> <circuit> <backend> [hardfork|protocol] [tag]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const HOME = process.env.HOME; const { ethers } = require(HOME + '/p0/node/node_modules/ethers');
const S = require(HOME + '/p0/lib/solc'); const P = require(HOME + '/p0/lib/proofs'); const E = require(HOME + '/p0/lib/eravm'); const CT = require('./contracts');
const [arm, circuit, backend, regime, tagArg] = process.argv.slice(2);
const proofDir = path.join(HOME, 'p0/circ/proofs', circuit);
(async () => {
  const pf = fs.readdirSync(proofDir).filter((f) => f.startsWith(backend + '-p')).sort();
  const proofs = []; for (const f of pf) { const { proof, publicSignals } = JSON.parse(fs.readFileSync(path.join(proofDir, f))); proofs.push({ j: Number(/p(\d+)/.exec(f)[1]), a: await P.args(backend, proof, publicSignals), pub: publicSignals }); }
  const k = proofs[0].pub.length; const src = CT.sources(circuit, backend, k);
  const foreign = process.env.FOREIGN; // circuit name with same k and backend (different vk) for the foreign-proof control
  let foreignArgs = null; if (foreign) { const f0 = JSON.parse(fs.readFileSync(path.join(HOME, 'p0/circ/proofs', foreign, `${backend}-p0.json`))); foreignArgs = await P.args(backend, f0.proof, f0.publicSignals); }
  const files = ['contracts/p0/Verifier.sol', 'contracts/p0/Manager.sol'];
  const res = { arm, circuit, backend, k, regime: regime || null, nproofs: proofs.length, rows: [], calls: {} };
  const callsList = (I, a) => { const L = [['valid', a], ['tampered_proof', P.tamperLast(backend, a)]]; for (let i = 0; i < k; i++) L.push([`perturb_pub_${i}`, P.perturbPub(backend, a, i)]); if (foreignArgs) L.push(['foreign_vk_proof', foreignArgs]); return L.map(([n, x]) => [n, I.encodeFunctionData('verifyProof', x)]); };
  if (arm === 'evm') {
    const C = S.evm(files, { roots: [HOME + '/p0/research'], extraSources: src.extra, evmVersion: process.env.EVMVERSION || 'paris' });
    const V = C[src.vname], M = C[src.mname]; res.sizes = { verifier_init: V.init_bytes, verifier_runtime: V.runtime_bytes, manager_init: M.init_bytes, manager_runtime: M.runtime_bytes, eip170_ok: V.runtime_bytes <= 24576 && M.runtime_bytes <= 24576, eip3860_ok: V.init_bytes <= 49152, verifier_sha256: V.runtime_sha256 };
    const vI = new ethers.Interface(V.abi), mI = new ethers.Interface(M.abi); const A0 = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';
    const steps = [{ op: 'deploy_verifier', kind: 'deploy', contract: 'V', key: 'v' }, { op: 'deploy_manager', kind: 'deploy', contract: 'M', key: 'm', args: ['$v'] }, { op: 'set_issuer', kind: 'tx', to: 'm', data: mI.encodeFunctionData('setIssuer', [A0, true]) }];
    for (const p of proofs) steps.push({ op: 'add_root', kind: 'tx', to: 'm', data: mI.encodeFunctionData('addRoot', [p.pub[0]]) });
    for (const p of proofs) steps.push({ op: 'verify_credential', j: p.j, kind: 'tx', to: 'm', data: mI.encodeFunctionData('verifyCredential', p.a) });
    for (const p of proofs) steps.push({ op: 'verify_proof_direct', j: p.j, kind: 'tx', to: 'v', data: vI.encodeFunctionData('verifyProof', p.a), trace: p.j === 0 });
    for (const [n, data] of callsList(vI, proofs[0].a)) steps.push({ op: 'call_' + n, kind: 'call', to: 'v', data });
    steps.push({ op: 'neg_unknown_root_tx', kind: 'tx', to: 'm', data: mI.encodeFunctionData('verifyCredential', P.perturbPub(backend, proofs[0].a, 0)) });
    const jp = `/tmp/sw-${process.pid}.json`, op = `/tmp/sw-${process.pid}-out.json`;
    fs.writeFileSync(jp, JSON.stringify({ contracts: { V, M }, steps }));
    execFileSync('npx', ['hardhat', 'run', 'evm_run.js'], { cwd: HOME + '/p0/hh', env: { ...process.env, HF: regime || 'osaka', JOB: jp, OUT: op, HARDHAT_DISABLE_TELEMETRY_PROMPT: 'true', CI: 'true' }, stdio: ['ignore', 'ignore', 'inherit'] });
    const out = JSON.parse(fs.readFileSync(op)); res.hardfork = out.hardfork;
    for (const s of out.steps) { if (s.kind === 'call') res.calls[s.op.slice(5)] = s.ok ? (BigInt(s.ret) === 1n ? 'true' : 'false') : 'revert'; else res.rows.push(s); }
  } else {
    const C = S.zk(files, { roots: [HOME + '/p0/research'], extraSources: src.extra });
    const V = C[src.vname], M = C[src.mname]; res.sizes = { verifier_bytes: V.bytes, manager_bytes: M.bytes, eravm_size_ok: V.bytes <= (2 ** 16 - 1) * 32, verifier_hash: V.hash };
    const vI = new ethers.Interface(V.abi), mI = new ethers.Interface(M.abi);
    const node = await E.start({ protocol: Number(regime || 29), port: 18000 + (process.pid % 1000), logFile: `/tmp/anv-${process.pid}.log` });
    try {
      const s = await E.session(node);
      const dv = await s.tx({ create: V, gasLimit: 400000000n }); res.rows.push({ op: 'deploy_verifier', ...dv });
      if (dv.status !== 1) throw new Error('verifier deploy failed');
      const dm = await s.tx({ create: { ...M, ctor: ethers.AbiCoder.defaultAbiCoder().encode(['address'], [dv.contractAddress]) }, gasLimit: 200000000n }); res.rows.push({ op: 'deploy_manager', ...dm });
      res.rows.push({ op: 'set_issuer', ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('setIssuer', [s.W[0].address, true]) })) });
      for (const p of proofs) res.rows.push({ op: 'add_root', ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('addRoot', [p.pub[0]]) })) });
      for (const p of proofs) res.rows.push({ op: 'verify_credential', j: p.j, ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('verifyCredential', p.a) })) });
      for (const p of proofs) res.rows.push({ op: 'verify_proof_direct', j: p.j, ...(await s.tx({ to: dv.contractAddress, data: vI.encodeFunctionData('verifyProof', p.a), trace: p.j === 0 })) });
      for (const [n, data] of callsList(vI, proofs[0].a)) { const c = await s.call(dv.contractAddress, data); res.calls[n] = c.ok ? (BigInt(c.ret) === 1n ? 'true' : 'false') : 'revert'; }
      res.rows.push({ op: 'neg_unknown_root_tx', ...(await s.tx({ to: dm.contractAddress, data: mI.encodeFunctionData('verifyCredential', P.perturbPub(backend, proofs[0].a, 0)) })) });
      await new Promise((r) => setTimeout(r, 500));
    } finally { await node.stop(); }
    const fee = E.feeRecords(node); for (const r of res.rows) Object.assign(r, fee.get(r.hash) || {});
  }
  const outFile = path.join(HOME, 'p0/out', `sweep-${arm}-${regime || (arm === 'evm' ? 'osaka' : 29)}-${circuit}-${backend}${tagArg ? '-' + tagArg : ''}.json`);
  fs.writeFileSync(outFile, JSON.stringify(res, null, 1));
  const g = (o, f = 'gasUsed') => res.rows.filter((r) => r.op === o).map((r) => r[f]);
  const neg = Object.entries(res.calls); const negOk = neg.filter(([n, v]) => n === 'valid' ? v === 'true' : v !== 'true').length;
  console.log(JSON.stringify({ arm, regime: regime || null, circuit, backend, k, sizes: res.sizes, status: res.rows.map((r) => r.status).join(''),
    vpd: arm === 'evm' ? g('verify_proof_direct') : g('verify_proof_direct', 'computational_gas'), vc: arm === 'evm' ? g('verify_credential') : g('verify_credential', 'computational_gas'),
    deployV: arm === 'evm' ? g('deploy_verifier')[0] : g('deploy_verifier', 'computational_gas')[0], controls: `${negOk}/${neg.length}`, failed: neg.filter(([n, v]) => n === 'valid' ? v !== 'true' : v === 'true').map(([n]) => n) }));
  process.exit(0);
})().catch((e) => { console.error('ERR', e.message.slice(0, 2000)); process.exit(1); });
