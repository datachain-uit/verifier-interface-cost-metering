// P0 EVM runner (EDR via Hardhat). Reads job JSON (env JOB), writes results JSON (env OUT).
// job = {contracts:{name:{abi,bytecode}}, steps:[{op,kind:'deploy'|'tx'|'call',contract,ctor?,to?,data?,expect?,trace?}]}
const fs = require('fs');
const hre = require('hardhat');
const { ethers } = hre;
async function opProfile(hash) {
  const t = await hre.network.provider.send('debug_traceTransaction', [hash, { disableStorage: true, disableMemory: true, disableStack: false }]);
  const prof = {}; const pre = {}; let maxMem = 0; const depthGas = {}; const kecc = []; const copies = []; let calldataLoads = 0;
  for (const s of t.structLogs) { const p = prof[s.op] || (prof[s.op] = { n: 0, gas: 0 }); p.n++; p.gas += s.gasCost;
    if (s.memSize !== undefined) maxMem = Math.max(maxMem, s.memSize);
    if (s.op === 'STATICCALL' || s.op === 'CALL') { const st = s.stack; const a = BigInt((x => x.startsWith('0x') ? x : '0x' + x)(st[st.length - 2])); if (a < 0x100n) { const k = '0x' + a.toString(16); const q = pre[k] || (pre[k] = { n: 0, gasCost: 0 }); q.n++; q.gasCost += s.gasCost; } }
    if (s.op === 'KECCAK256' || s.op === 'SHA3') { const st = s.stack; kecc.push(Number(BigInt((x => x.startsWith('0x') ? x : '0x' + x)(st[st.length - 2])))); }
    if (/COPY$/.test(s.op) && s.op !== 'MCOPY') { const st = s.stack; copies.push([s.op, Number(BigInt((x => x.startsWith('0x') ? x : '0x' + x)(st[st.length - 3])))]); }
    depthGas[s.depth] = (depthGas[s.depth] || 0) + s.gasCost; }
  return { gas: t.gas, failed: t.failed, steps: t.structLogs.length, ops: prof, precompiles: pre, maxMem, depthGas, keccak_sizes: kecc, copies };
}
async function main() {
  const job = JSON.parse(fs.readFileSync(process.env.JOB, 'utf8'));
  const [A0] = await ethers.getSigners();
  const HF = hre.network.config.hardfork;
  const legacy = ['byzantium','constantinople','petersburg','istanbul','muirGlacier','berlin'].includes(HF) || job.legacy;
  const txo = legacy ? { type: 0, gasPrice: job.gasPrice || 1n } : { maxFeePerGas: 0n, maxPriorityFeePerGas: 0n };
  const addr = {}; const out = { hardfork: HF, steps: [] };
  for (const s of job.steps) {
    const r = { op: s.op, kind: s.kind, contract: s.contract };
    try {
      if (s.kind === 'deploy') {
        const c = job.contracts[s.contract];
        const f = new ethers.ContractFactory(c.abi, c.bytecode, A0); s.args = (s.args || []).map((a) => typeof a === 'string' && a.startsWith('$') ? addr[a.slice(1)] : a);
        const dtx = await f.getDeployTransaction(...(s.args || []));
        const tx = await A0.sendTransaction({ ...dtx, gasLimit: s.gasLimit || 15000000, ...txo });
        const rc = await tx.wait();
        r.status = rc.status; r.gasUsed = Number(rc.gasUsed); addr[s.key || s.contract] = rc.contractAddress; r.address = rc.contractAddress;
        const code = await ethers.provider.getCode(rc.contractAddress); r.runtime_bytes = (code.length - 2) / 2; r.initcode_bytes = (dtx.data.length - 2) / 2;
      } else if (s.kind === 'tx') {
        const data = s.data;
        const tx = await A0.sendTransaction({ to: addr[s.to], data, gasLimit: s.gasLimit || 3000000, ...txo });
        const rc = await tx.wait().catch((e) => e.receipt);
        r.status = rc.status; r.gasUsed = Number(rc.gasUsed); r.calldata_bytes = (data.length - 2) / 2;
        let z = 0; for (let i = 2; i < data.length; i += 2) if (data.slice(i, i + 2) === '00') z++; r.calldata_zero = z;
        if (s.trace) r.trace = await opProfile(rc.hash);
        if (s.ret) { const res = await hre.network.provider.send('debug_traceTransaction', [rc.hash, { disableStorage: true, disableMemory: true, disableStack: true }]); r.returnValue = res.returnValue; }
      } else if (s.kind === 'call') {
        try { r.ret = await ethers.provider.call({ to: addr[s.to], data: s.data, from: A0.address }); r.ok = true; }
        catch (e) { r.ok = false; r.err = String(e.shortMessage || e.message).slice(0, 200); }
      }
    } catch (e) { r.error = String(e.shortMessage || e.message).slice(0, 300); }
    out.steps.push(r);
  }
  fs.writeFileSync(process.env.OUT, JSON.stringify(out, null, 1)); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
