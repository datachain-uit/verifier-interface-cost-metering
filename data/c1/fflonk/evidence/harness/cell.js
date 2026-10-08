// V2-C1 registered harness (v2: + cell_id field) — one cell (frozen protocol: 03 §5, 14, 17, 18 of the C1 package).
// usage: node cell.js <spec.json>
// spec: {campaign, run_id, order_index, cell_id, env, regime, backend, circuit, k, relation, compiled, proofs_dir, foreign_dirs, outdir, pins_sha256, port}
// Writes <outdir>/records.jsonl (schema v2-c1-evidence/1) and raw files; never edits a value by hand.
const fs = require('fs'); const path = require('path'); const crypto = require('crypto'); const { execFileSync } = require('child_process');
const HOME = process.env.HOME; const H = __dirname;
const { ethers } = require(HOME + '/p0/node/node_modules/ethers');
const P = require('./lib/proofs'); const E = require('./lib/eravm');
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// foreign-key controls (17-negative-control-protocol.md): k in {4, 8} only
const FOREIGN = { c1_ctx_k04: ['c1_a4'], c1_a4: ['c1_ctx_k04'], c1_disc_k04: ['c1_ctx_k04'], c1_ctx_k08: ['c1_a8'], c1_a8: ['c1_ctx_k08'] };
if (process.env.SELFTEST_FOREIGN_JSON) Object.assign(FOREIGN, JSON.parse(process.env.SELFTEST_FOREIGN_JSON));   // self-test fixtures only (P0 circuit names)
const zeroBytes = (hex) => { let z = 0; for (let i = 2; i < hex.length; i += 2) if (hex.slice(i, i + 2) === '00') z++; return z; };
const retv = (ok, ret) => (ok ? (BigInt(ret) === 1n ? 'true' : 'false') : 'revert');
class Dev extends Error { constructor(cls, msg) { super(`${cls}: ${msg}`); this.cls = cls; } }
(async () => {
  const { campaign, run_id, order_index, env, regime, backend, circuit, k, relation, outdir } = spec;
  fs.mkdirSync(outdir, { recursive: true });
  const C = JSON.parse(fs.readFileSync(spec.compiled, 'utf8'));
  if (C.circuit !== circuit || C.backend !== backend || C.k !== k) throw new Dev('D-HASH', 'compiled artifact does not match cell');
  // ---- corpus: j = 0..7 from the frozen corpus ----
  const proofs = [];
  for (let j = 0; j < 8; j++) {
    const f = path.join(spec.proofs_dir, circuit, `${backend}-j${j}.json`); const raw = fs.readFileSync(f);
    const { id, proof, publicSignals } = JSON.parse(raw);
    if (id !== `${circuit}/${backend}/j${j}`) throw new Dev('D-PROOFGEN', `unexpected proof id ${id}`);
    if (publicSignals.length !== k) throw new Dev('D-PROTO', `k mismatch in ${id}`);
    proofs.push({ j, id, a: await P.args(backend, proof, publicSignals), pub: publicSignals, file_sha256: sha(raw) });
  }
  const foreign = [];
  for (const fc of (FOREIGN[circuit] || [])) {
    const f = path.join(spec.proofs_dir, fc, `${backend}-j0.json`); if (!fs.existsSync(f)) continue; const raw = fs.readFileSync(f);
    const { id, proof, publicSignals } = JSON.parse(raw); if (publicSignals.length !== k) continue;
    foreign.push({ id, a: await P.args(backend, proof, publicSignals), file_sha256: sha(raw) });
  }
  const records = []; const pins = spec.pins_sha256;
  const base = { schema: 'v2-c1-evidence/1', campaign, run_id, order_index, cell_id: spec.cell_id, env, regime, backend, circuit, k, relation };
  let vsha = null, msha = null;
  const rec = (o) => records.push({ ...base, utc: new Date().toISOString(), proof_id: null, control: null, returned: null, tx_hash: null, gas_used: null, calldata_bytes: null, calldata_zero: null,
    evm_trace: null, eravm: null, zkos: null, deviation_ref: null, supersedes: null, ...o, artifacts: { verifier_runtime_sha256: vsha, manager_runtime_sha256: msha, proof_file_sha256: o.proof_file_sha256 || null, pins_sha256: pins } });
  // ---- step plan (identical in every regime) ----
  const plan = [];
  plan.push({ op: 'deploy_verifier', kind: 'deploy', role: 'setup' }, { op: 'deploy_manager', kind: 'deploy', role: 'setup' }, { op: 'set_issuer', kind: 'tx', to: 'm', role: 'setup', fn: 'setIssuer' });
  for (const p of proofs) plan.push({ op: 'add_root', kind: 'tx', to: 'm', role: 'setup', fn: 'addRoot', root: p.pub[0], p });
  for (const p of proofs) plan.push({ op: 'verify_credential', kind: 'tx', to: 'm', role: 'measurement', fn: 'verifyCredential', a: p.a, p });
  for (const p of proofs) plan.push({ op: 'verify_proof_direct', kind: 'tx', to: 'v', role: 'measurement', fn: 'verifyProof', a: p.a, p, trace: true });
  const p0 = proofs[0];
  plan.push({ op: 'verify_proof_direct', kind: 'tx', to: 'v', role: 'replay', control: 'replay', fn: 'verifyProof', a: p0.a, p: p0, trace: true });
  plan.push({ op: 'verify_credential', kind: 'tx', to: 'm', role: 'control', control: 'unknown_root_tx', fn: 'verifyCredential', a: P.perturbPub(backend, p0.a, 0), p: p0 });
  plan.push({ op: 'control', kind: 'call', control: 'valid', a: p0.a, p: p0 });
  plan.push({ op: 'control', kind: 'call', control: 'tampered_proof', a: P.tamperLast(backend, p0.a), p: p0 });
  for (let i = 0; i < k; i++) plan.push({ op: 'control', kind: 'call', control: `perturb_pub_${i}`, a: P.perturbPub(backend, p0.a, i), p: p0 });
  plan.push({ op: 'control', kind: 'call', control: 'out_of_field_pub', a: P.outOfField(backend, p0.a, k - 1), p: p0 });
  for (const f of foreign) plan.push({ op: 'control', kind: 'call', control: 'foreign_vk_proof', a: f.a, p: { id: f.id, file_sha256: f.file_sha256 } });
  for (const p of proofs) plan.push({ op: 'control', kind: 'call', control: 'cross_regime_identity', a: p.a, p });
  const ABI = (side) => new ethers.Interface(side === 'v' ? C.evm.V.abi : C.evm.M.abi);
  const vI = ABI('v'), mI = ABI('m');
  const dataOf = (s, from) => s.fn === 'setIssuer' ? mI.encodeFunctionData('setIssuer', [from, true]) : s.fn === 'addRoot' ? mI.encodeFunctionData('addRoot', [s.root])
    : (s.to === 'm' ? mI : vI).encodeFunctionData(s.fn, s.a);
  const meta = { env, regime, versions: {} };
  if (env === 'evm-osaka' || env === 'evm-petersburg') {
    const A0 = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';
    const steps = plan.map((s) => s.kind === 'deploy' ? { op: s.op, kind: 'deploy', contract: s.op === 'deploy_verifier' ? 'V' : 'M', key: s.op === 'deploy_verifier' ? 'v' : 'm', args: s.op === 'deploy_manager' ? ['$v'] : [] }
      : s.kind === 'tx' ? { op: s.op, kind: 'tx', to: s.to, data: dataOf(s, A0), trace: !!s.trace } : { op: 'call_' + s.control, kind: 'call', to: 'v', data: vI.encodeFunctionData('verifyProof', s.a) });
    const job = path.join(outdir, 'edr-job.json'), out = path.join(outdir, 'edr-out.json');
    fs.writeFileSync(job, JSON.stringify({ contracts: { V: { abi: C.evm.V.abi, bytecode: C.evm.V.bytecode }, M: { abi: C.evm.M.abi, bytecode: C.evm.M.bytecode } }, steps }));
    const hf = env === 'evm-osaka' ? 'osaka' : 'petersburg';
    execFileSync('npx', ['hardhat', 'run', 'evm_run.js'], { cwd: path.join(H, 'hh'), env: { ...process.env, HF: hf, JOB: job, OUT: out, HARDHAT_DISABLE_TELEMETRY_PROMPT: 'true', CI: 'true' }, stdio: ['ignore', 'inherit', 'inherit'] });
    const res = JSON.parse(fs.readFileSync(out, 'utf8')); meta.versions.hardfork = res.hardfork;
    if (res.hardfork !== hf) throw new Dev('D-HASH', `hardfork stamp ${res.hardfork} != ${hf}`);
    res.steps.forEach((r, i) => {
      const s = plan[i]; if (r.error) throw new Dev('D-PROTO', `${s.op}: ${r.error}`);
      if (s.kind === 'deploy') {
        const want = s.op === 'deploy_verifier' ? C.evm.V.runtime_sha256 : C.evm.M.runtime_sha256;
        if (r.runtime_sha256 !== want) throw new Dev('D-HASH', `${s.op} runtime ${r.runtime_sha256} != ${want}`);
        if (s.op === 'deploy_verifier') vsha = r.runtime_sha256; else msha = r.runtime_sha256;
        rec({ op: s.op, role: 'setup', status: r.status, tx_hash: r.hash, gas_used: r.gasUsed });
      } else if (s.kind === 'tx') {
        const tr = r.trace ? { ...r.trace, sdiv_count: (r.trace.ops.SDIV || { n: 0 }).n } : null;
        rec({ op: s.op, role: s.role, control: s.control || null, proof_id: s.p ? s.p.id : null, proof_file_sha256: s.p ? s.p.file_sha256 : null, status: r.status, tx_hash: r.hash, gas_used: r.gasUsed, calldata_bytes: r.calldata_bytes, calldata_zero: r.calldata_zero, evm_trace: tr });
      } else {
        rec({ op: 'control', role: 'control', control: s.control, proof_id: s.p.id, proof_file_sha256: s.p.file_sha256, status: r.ok ? 1 : 0, returned: retv(r.ok, r.ret) });
      }
    });
  } else if (env === 'eravm-29' || env === 'eravm-27') {
    const protocol = Number(env.split('-')[1]);
    const node = await E.start({ protocol, port: spec.port || 18011, logFile: path.join(outdir, 'anvil-zksync.log') });
    const traces = [];
    try {
      const s0 = await E.session(node); const from = s0.W[0].address; let vaddr, maddr;
      for (const s of plan) {
        if (s.kind === 'deploy') {
          const art = s.op === 'deploy_verifier' ? C.eravm.V : C.eravm.M;
          const t = await s0.tx({ create: s.op === 'deploy_verifier' ? art : { ...art, ctor: ethers.AbiCoder.defaultAbiCoder().encode(['address'], [vaddr]) }, gasLimit: s.op === 'deploy_verifier' ? 400000000n : 200000000n });
          if (t.status !== 1) throw new Dev('D-DEPLOY', `${s.op} status ${t.status}`);
          const code = await E.rpcCall(node.url, 'eth_getCode', [t.contractAddress, 'latest']); const csha = sha(Buffer.from(code.slice(2), 'hex'));
          if (csha !== art.sha256) throw new Dev('D-HASH', `${s.op} code ${csha} != ${art.sha256}`);
          if (s.op === 'deploy_verifier') { vaddr = t.contractAddress; vsha = csha; } else { maddr = t.contractAddress; msha = csha; }
          rec({ op: s.op, role: 'setup', status: t.status, tx_hash: t.hash, gas_used: t.gasUsed, _fee: true });
        } else if (s.kind === 'tx') {
          const data = dataOf(s, from); const t = await s0.tx({ to: s.to === 'v' ? vaddr : maddr, data, trace: !!s.trace });
          if (t.trace) traces.push({ hash: t.hash, op: s.op, control: s.control || null, proof_id: s.p.id, trace: t.trace });
          rec({ op: s.op, role: s.role, control: s.control || null, proof_id: s.p ? s.p.id : null, proof_file_sha256: s.p ? s.p.file_sha256 : null, status: t.status, tx_hash: t.hash, gas_used: t.gasUsed, calldata_bytes: t.calldata_bytes, calldata_zero: zeroBytes(data), _fee: true, _vaddr: vaddr });
        } else {
          const c = await s0.call(vaddr, vI.encodeFunctionData('verifyProof', s.a));
          rec({ op: 'control', role: 'control', control: s.control, proof_id: s.p.id, proof_file_sha256: s.p.file_sha256, status: c.ok ? 1 : 0, returned: retv(c.ok, c.ret) });
        }
      }
      await sleep(500);
    } finally { await node.stop(); }
    fs.writeFileSync(path.join(outdir, 'eravm-calltraces.json'), JSON.stringify(traces));
    const fee = E.feeRecords(node); const TR = new Map(traces.map((t) => [t.hash, t.trace]));
    const g = (f) => parseInt(f.gasUsed || '0x0', 16);
    for (const r of records) {
      if (!r._fee) continue; const f = fee.get(r.tx_hash);
      if (!f || f.computational_gas == null) throw new Dev('D-NATIVE', `no refund-trace fee record for ${r.op} ${r.tx_hash}`);
      r.eravm = { computational_gas: f.computational_gas, pubdata_gas: f.pubdata_gas, pubdata_bytes: f.pubdata_bytes, gas_limit: f.gas_limit };
      const tr = TR.get(r.tx_hash);
      if (tr) {
        const v = r._vaddr.toLowerCase(); let vf = null;
        const find = (fr) => { if ((fr.to || '').toLowerCase() === v && (fr.from || '').toLowerCase() === '0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266') return fr; for (const c of fr.calls || []) { const x = find(c); if (x) return x; } return null; };
        for (const c of tr.calls || []) { vf = find(c); if (vf) break; }
        if (!vf) throw new Dev('D-NATIVE', `verifier frame not found in ${r.tx_hash}`);
        const pre = {}; let sum = 0;
        for (const c of vf.calls || []) { const a = (c.to || '').toLowerCase().slice(-4); pre[a] = pre[a] || [0, 0]; pre[a][0]++; pre[a][1] += g(c); sum += g(c); }
        r.eravm.frames = { outside: f.computational_gas - g(vf), self: g(vf) - sum, precompiles: pre, verifier_frame: g(vf) };
      }
      delete r._fee; delete r._vaddr;
    }
    meta.versions.protocol_flag = protocol; meta.versions.anvil_zksync_log_head = fs.readFileSync(path.join(outdir, 'anvil-zksync.log'), 'utf8').split('\n').slice(0, 5);
  } else if (env === 'zkos-v32') {
    const SERVER_LOG = spec.server_log;
    const provider = new ethers.JsonRpcProvider('http://127.0.0.1:3050', undefined, { staticNetwork: true, batchMaxCount: 1 });
    const w = new ethers.Wallet('0x7726827caac94a7f9e1b160f7ea819f172f7b6f9d2a97f992c38edeab82d4110', provider);
    const blk = await provider.getBlock('latest'); const baseFee = blk.baseFeePerGas; const prio = BigInt(regime.priority_fee || 0);
    if (baseFee !== BigInt(regime.npg) * 1000000n) throw new Dev('D-HASH', `base fee ${baseFee} != npg ${regime.npg} x native price`);
    const fee = { maxFeePerGas: baseFee + prio, maxPriorityFeePerGas: prio, type: 2 };
    let nonce = await provider.getTransactionCount(w.address, 'latest'); let vaddr, maddr;
    for (const s of plan) {
      if (s.kind === 'deploy') {
        const art = s.op === 'deploy_verifier' ? C.evm.V : C.evm.M;
        const data = s.op === 'deploy_verifier' ? art.bytecode : art.bytecode + ethers.AbiCoder.defaultAbiCoder().encode(['address'], [vaddr]).slice(2);
        const tx = await w.sendTransaction({ data, ...fee, nonce: nonce++, gasLimit: 10000000n, chainId: 506 }); const rc = await tx.wait();
        if (rc.status !== 1) throw new Dev('D-DEPLOY', `${s.op} status ${rc.status}`);
        const code = await provider.getCode(rc.contractAddress); const csha = sha(Buffer.from(code.slice(2), 'hex'));
        if (csha !== art.runtime_sha256) throw new Dev('D-HASH', `${s.op} runtime ${csha} != ${art.runtime_sha256}`);
        if (s.op === 'deploy_verifier') { vaddr = rc.contractAddress; vsha = csha; } else { maddr = rc.contractAddress; msha = csha; }
        rec({ op: s.op, role: 'setup', status: rc.status, tx_hash: tx.hash, gas_used: Number(rc.gasUsed), _zk: rc.gasPrice?.toString() });
      } else if (s.kind === 'tx') {
        const data = dataOf(s, w.address);
        const tx = await w.sendTransaction({ to: s.to === 'v' ? vaddr : maddr, data, ...fee, nonce: nonce++, gasLimit: 10000000n, chainId: 506 });
        let rc; try { rc = await tx.wait(); } catch (e) { rc = e.receipt; if (!rc) throw e; }
        rec({ op: s.op, role: s.role, control: s.control || null, proof_id: s.p ? s.p.id : null, proof_file_sha256: s.p ? s.p.file_sha256 : null, status: rc.status, tx_hash: tx.hash, gas_used: Number(rc.gasUsed),
              calldata_bytes: (data.length - 2) / 2, calldata_zero: zeroBytes(data), _zk: rc.gasPrice?.toString() });
      } else {
        let ok = true, ret = null; try { ret = await provider.call({ to: vaddr, data: vI.encodeFunctionData('verifyProof', s.a) }); } catch (e) { ok = false; }
        rec({ op: 'control', role: 'control', control: s.control, proof_id: s.p.id, proof_file_sha256: s.p.file_sha256, status: ok ? 1 : 0, returned: retv(ok, ret) });
      }
    }
    await sleep(2000);
    const log = fs.readFileSync(SERVER_LOG, 'utf8'); const m = new Map();
    for (const l of log.split('\n')) { const x = /Transaction (0x[0-9a-f]{64}) executed with status (\w+) .*gas_used: (\d+), gas_refunded: (\d+), computational_native_used: (\d+), native_used: (\d+), pubdata_used: (\d+)/.exec(l);
      if (x) m.set(x[1], { status_log: x[2], gas_used_log: +x[3], gas_refunded: +x[4], computational_native: +x[5], native_used: +x[6], pubdata_used: +x[7] }); }
    for (const r of records) {
      if (r._zk === undefined) continue; const z = m.get(r.tx_hash);
      if (!z) throw new Dev('D-NATIVE', `no native line for ${r.op} ${r.tx_hash}`);
      r.zkos = { ...z, effective_gas_price: r._zk, base_fee: baseFee.toString() }; delete r._zk;
    }
    const v32 = /L1 upgrade transaction found for protocol version 0\.32\.0/.test(log), ev7 = /execution_version: 7\b/.test(log);
    meta.versions.protocol_0_32_0 = v32; meta.versions.execution_version_7 = ev7; meta.versions.base_fee = baseFee.toString();
    if (!v32 || !ev7) throw new Dev('D-HASH', `version stamp missing (0.32.0: ${v32}, execution_version 7: ${ev7})`);
  } else throw new Dev('D-PROTO', 'unknown env ' + env);
  for (const r of records) for (const k2 of Object.keys(r)) if (k2.startsWith('_')) delete r[k2];
  fs.writeFileSync(path.join(outdir, 'records.jsonl'), records.map((r) => JSON.stringify(r)).join('\n') + '\n');
  fs.writeFileSync(path.join(outdir, 'cell-meta.json'), JSON.stringify({ ...meta, n_records: records.length, verifier_runtime_sha256: vsha, manager_runtime_sha256: msha }, null, 1));
  console.log(JSON.stringify({ cell: spec.cell_id, n_records: records.length, statuses: records.filter((r) => r.role === 'measurement').map((r) => r.status).join('') }));
  process.exit(0);
})().catch((e) => { console.error('CELL-ERROR', e.cls || 'D-PROTO', String(e.message).slice(0, 3000)); try { fs.writeFileSync(path.join(spec.outdir, 'CELL-ERROR.txt'), `${e.cls || 'D-PROTO'}\n${e.stack || e.message}\n`); } catch (_) {} process.exit(2); });
