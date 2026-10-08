// P0 ZKsync OS runner: same solc bytecode as the EVM arm; per-tx gas/native/pubdata from the sequencer debug log.
// usage: node zkos_run.js <circuit> <backend> <tag> [priorityFeeWei]
const fs = require('fs'); const path = require('path');
const HOME = process.env.HOME; const { ethers } = require(HOME + '/p0/node/node_modules/ethers');
const S = require(HOME + '/p0/lib/solc'); const P = require(HOME + '/p0/lib/proofs'); const CT = require('./contracts');
const [circuit, backend, tag, prioArg] = process.argv.slice(2);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function parseLog(file) { const m = new Map(); for (const l of fs.readFileSync(file, 'utf8').split('\n')) { const x = /Transaction (0x[0-9a-f]{64}) executed with status (\w+) .*gas_used: (\d+), gas_refunded: (\d+), computational_native_used: (\d+), native_used: (\d+), pubdata_used: (\d+)/.exec(l);
  if (x) m.set(x[1], { status_log: x[2], gas_used_log: +x[3], gas_refunded: +x[4], computational_native: +x[5], native_used: +x[6], pubdata_used: +x[7] }); } return m; }
(async () => {
  const provider = new ethers.JsonRpcProvider('http://127.0.0.1:3050', undefined, { staticNetwork: true, batchMaxCount: 1 });
  const w = new ethers.Wallet('0x7726827caac94a7f9e1b160f7ea819f172f7b6f9d2a97f992c38edeab82d4110', provider);
  const proofDir = path.join(HOME, 'p0/circ/proofs', circuit);
  const pf = fs.readdirSync(proofDir).filter((f) => f.startsWith(backend + '-p')).sort(); const proofs = [];
  for (const f of pf) { const { proof, publicSignals } = JSON.parse(fs.readFileSync(path.join(proofDir, f))); proofs.push({ j: Number(/p(\d+)/.exec(f)[1]), a: await P.args(backend, proof, publicSignals), pub: publicSignals }); }
  const k = proofs[0].pub.length; const src = CT.sources(circuit, backend, k);
  const C = S.evm(['contracts/p0/Verifier.sol', 'contracts/p0/Manager.sol'], { roots: [HOME + '/p0/research'], extraSources: src.extra, evmVersion: process.env.EVMVERSION || 'paris' });
  const V = C[src.vname], M = C[src.mname]; const vI = new ethers.Interface(V.abi), mI = new ethers.Interface(M.abi);
  const blk = await provider.getBlock('latest'); const base = blk.baseFeePerGas; const prio = BigInt(prioArg || 0);
  const fee = { maxFeePerGas: base + prio, maxPriorityFeePerGas: prio, type: 2 };
  let nonce = await provider.getTransactionCount(w.address, 'latest'); const rows = [];
  async function send(op, req, extra = {}) { const tx = await w.sendTransaction({ ...req, ...fee, nonce: nonce++, gasLimit: req.gasLimit || 30000000n, chainId: 506 }); const rc = await tx.wait(); rows.push({ op, hash: tx.hash, status: rc.status, gasUsed: Number(rc.gasUsed), effectiveGasPrice: rc.gasPrice?.toString(), contract: rc.contractAddress, calldata_bytes: (req.data.length - 2) / 2, ...extra }); return rc; }
  const dV = await send('deploy_verifier', { data: V.bytecode }); const dM = await send('deploy_manager', { data: M.bytecode + ethers.AbiCoder.defaultAbiCoder().encode(['address'], [dV.contractAddress]).slice(2) });
  await send('set_issuer', { to: dM.contractAddress, data: mI.encodeFunctionData('setIssuer', [w.address, true]) });
  for (const p of proofs) await send('add_root', { to: dM.contractAddress, data: mI.encodeFunctionData('addRoot', [p.pub[0]]) });
  for (const p of proofs) await send('verify_credential', { to: dM.contractAddress, data: mI.encodeFunctionData('verifyCredential', p.a) }, { j: p.j });
  for (const p of proofs) await send('verify_proof_direct', { to: dV.contractAddress, data: vI.encodeFunctionData('verifyProof', p.a) }, { j: p.j });
  const calls = {}; const L = [['valid', proofs[0].a], ['tampered_proof', P.tamperLast(backend, proofs[0].a)]]; for (let i = 0; i < k; i++) L.push([`perturb_pub_${i}`, P.perturbPub(backend, proofs[0].a, i)]);
  for (const [n, a] of L) { try { const r = await provider.call({ to: dV.contractAddress, data: vI.encodeFunctionData('verifyProof', a) }); calls[n] = BigInt(r) === 1n ? 'true' : 'false'; } catch (e) { calls[n] = 'revert'; } }
  await sleep(1500);
  const logs = parseLog(path.join(HOME, 'p0/zkos/run', tag, 'server.log')); for (const r of rows) Object.assign(r, logs.get(r.hash) || {});
  const res = { arm: 'zkos', circuit, backend, k, tag, base_fee: base.toString(), priority_fee: prio.toString(), rows, calls, sizes: { verifier_runtime: V.runtime_bytes, verifier_sha256: V.runtime_sha256 } };
  fs.writeFileSync(path.join(HOME, 'p0/out', `zkos-${tag}-${circuit}-${backend}-p${prio}.json`), JSON.stringify(res, null, 1));
  const g = (o, f) => rows.filter((r) => r.op === o).map((r) => r[f]);
  console.log(JSON.stringify({ circuit, backend, k, tag, prio: prio.toString(), status: rows.map((r) => r.status).join(''), vpd_gas: g('verify_proof_direct', 'gasUsed'), vpd_native: g('verify_proof_direct', 'native_used'), vpd_cnative: g('verify_proof_direct', 'computational_native'), vpd_pubdata: g('verify_proof_direct', 'pubdata_used'), vc_gas: g('verify_credential', 'gasUsed'), vc_native: g('verify_credential', 'native_used'), deployV_gas: g('deploy_verifier', 'gasUsed')[0], calls }));
  process.exit(0);
})().catch((e) => { console.error('ERR', e.message.slice(0, 1500)); process.exit(1); });
