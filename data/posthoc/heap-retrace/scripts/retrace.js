// V2-M7B-A deterministic EDR re-trace of frozen proofs (no new proof, no ZKsync OS run, no timing).
// For each (circuit, backend): deploy the frozen compiled verifier (runtime sha256 checked), send verifyProof(j0) as a
// tx (gasLimit 3,000,000, zero fees; as in the registered EVM cells), trace with storage/memory disabled, stack enabled.
// Writes raw/<circuit>-<backend>-j0.structlogs.json.gz and retrace-summary.json (profile in the registered format).
const fs = require('fs'); const path = require('path'); const zlib = require('zlib'); const crypto = require('crypto');
const hre = require('hardhat'); const { ethers } = hre;
const P = require(process.env.HOME + '/full/harness/lib/proofs');
const COMPILED = { c1_k01: process.env.HOME + '/full/V2-MPI-FULL-01/compiled', c1_ctx_k02: process.env.HOME + '/pilot/V2-MPI-PILOT-01/compiled' };
const CIRC = ['c1_k01', 'c1_ctx_k02', 'c1_ctx_k04', 'c1_ctx_k08', 'c1_ctx_k12', 'c1_ctx_k16', 'c1_ctx_k24', 'c1_ctx_k32', 'c1_ctx_k64'];
const CORPUS = process.env.HOME + '/c1/pkg/corpus/proofs'; const OUT = path.join(__dirname, '..');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const big = (x) => BigInt(x.startsWith('0x') ? x : '0x' + x);
function profile(t) { // identical to the registered opProfile() of evm_run.js
  const prof = {}; const pre = {}; let maxMem = 0; const depthGas = {}; const kecc = []; const copies = [];
  for (const s of t.structLogs) { const p = prof[s.op] || (prof[s.op] = { n: 0, gas: 0 }); p.n++; p.gas += s.gasCost;
    if (s.memSize !== undefined) maxMem = Math.max(maxMem, s.memSize);
    if (s.op === 'STATICCALL' || s.op === 'CALL') { const st = s.stack; const a = big(st[st.length - 2]); if (a < 0x100n) { const k = '0x' + a.toString(16); const q = pre[k] || (pre[k] = { n: 0, gasCost: 0 }); q.n++; q.gasCost += s.gasCost; } }
    if (s.op === 'KECCAK256' || s.op === 'SHA3') { const st = s.stack; kecc.push(Number(big(st[st.length - 2]))); }
    if (/COPY$/.test(s.op) && s.op !== 'MCOPY') { const st = s.stack; copies.push([s.op, Number(big(st[st.length - 3]))]); }
    depthGas[s.depth] = (depthGas[s.depth] || 0) + s.gasCost; }
  return { gas: t.gas, failed: t.failed, steps: t.structLogs.length, ops: prof, precompiles: pre, maxMem, depthGas, keccak_sizes: kecc, copies };
}
async function main() {
  if (hre.network.config.hardfork !== 'osaka') throw new Error('hardfork');
  const [A0] = await ethers.getSigners(); const summary = { hardfork: hre.network.config.hardfork, utc: new Date().toISOString(), items: [] };
  for (const circuit of CIRC) for (const backend of ['groth16', 'plonk']) {
    const C = JSON.parse(fs.readFileSync(path.join(COMPILED[circuit] || (process.env.HOME + '/full/V2-MPI-FULL-01/compiled'), `${circuit}-${backend}.json`), 'utf8'));
    const pf = path.join(CORPUS, circuit, `${backend}-j0.json`); const raw = fs.readFileSync(pf); const { id, proof, publicSignals } = JSON.parse(raw);
    const a = await P.args(backend, proof, publicSignals);
    const f = new ethers.ContractFactory(C.evm.V.abi, C.evm.V.bytecode, A0);
    const dtx = await f.getDeployTransaction(); const rc0 = await (await A0.sendTransaction({ ...dtx, gasLimit: 15000000, maxFeePerGas: 0n, maxPriorityFeePerGas: 0n })).wait();
    const code = await ethers.provider.getCode(rc0.contractAddress); const rsha = sha(Buffer.from(code.slice(2), 'hex'));
    if (rsha !== C.evm.V.runtime_sha256) throw new Error(`runtime sha ${circuit} ${backend}`);
    const data = new ethers.Interface(C.evm.V.abi).encodeFunctionData('verifyProof', a);
    const rc = await (await A0.sendTransaction({ to: rc0.contractAddress, data, gasLimit: 3000000, maxFeePerGas: 0n, maxPriorityFeePerGas: 0n })).wait();
    const ret = await hre.network.provider.send('debug_traceTransaction', [rc.hash, { disableStorage: true, disableMemory: true, disableStack: true }]);
    const t = await hre.network.provider.send('debug_traceTransaction', [rc.hash, { disableStorage: true, disableMemory: true, disableStack: false }]);
    const name = `${circuit}-${backend}-j0.structlogs.json.gz`; const buf = zlib.gzipSync(Buffer.from(JSON.stringify(t)), { level: 9, mtime: 0 });
    fs.writeFileSync(path.join(OUT, 'raw', name), buf);
    summary.items.push({ proof_id: id, circuit, backend, k: publicSignals.length, proof_file_sha256: sha(raw), verifier_runtime_sha256: rsha, status: rc.status, gas_used: Number(rc.gasUsed),
      calldata_bytes: (data.length - 2) / 2, return_value: ret.returnValue, raw_file: name, raw_sha256: sha(buf), profile: profile(t) });
    console.log(`${id}: status ${rc.status} gasUsed ${rc.gasUsed} steps ${t.structLogs.length}`);
  }
  fs.writeFileSync(path.join(OUT, 'retrace-summary.json'), JSON.stringify(summary, null, 1)); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
