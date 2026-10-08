// V2-M7B-A second re-trace of the same 18 transactions with memory ENABLED, only to observe EDR's memory size per step
// (EDR 0.12 omits memSize when memory is disabled; deviation DEV-M7B-A-1). Memory contents are not kept: per step only
// memSize = 32 * memory.length is written, plus a streamed sha256 over all memory words (fingerprint of the full trace).
const fs = require('fs'); const path = require('path'); const zlib = require('zlib'); const crypto = require('crypto');
const hre = require('hardhat'); const { ethers } = hre;
const P = require(process.env.HOME + '/full/harness/lib/proofs');
const COMPILED = { c1_ctx_k02: process.env.HOME + '/pilot/V2-MPI-PILOT-01/compiled' };
const CIRC = ['c1_k01', 'c1_ctx_k02', 'c1_ctx_k04', 'c1_ctx_k08', 'c1_ctx_k12', 'c1_ctx_k16', 'c1_ctx_k24', 'c1_ctx_k32', 'c1_ctx_k64'];
const CORPUS = process.env.HOME + '/c1/pkg/corpus/proofs'; const OUT = path.join(__dirname, '..');
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
async function main() {
  if (hre.network.config.hardfork !== 'osaka') throw new Error('hardfork');
  const [A0] = await ethers.getSigners(); const items = [];
  for (const circuit of CIRC) for (const backend of ['groth16', 'plonk']) {
    const C = JSON.parse(fs.readFileSync(path.join(COMPILED[circuit] || (process.env.HOME + '/full/V2-MPI-FULL-01/compiled'), `${circuit}-${backend}.json`), 'utf8'));
    const { id, proof, publicSignals } = JSON.parse(fs.readFileSync(path.join(CORPUS, circuit, `${backend}-j0.json`)));
    const a = await P.args(backend, proof, publicSignals);
    const f = new ethers.ContractFactory(C.evm.V.abi, C.evm.V.bytecode, A0);
    const rc0 = await (await A0.sendTransaction({ ...(await f.getDeployTransaction()), gasLimit: 15000000, maxFeePerGas: 0n, maxPriorityFeePerGas: 0n })).wait();
    if (sha(Buffer.from((await ethers.provider.getCode(rc0.contractAddress)).slice(2), 'hex')) !== C.evm.V.runtime_sha256) throw new Error('runtime sha');
    const data = new ethers.Interface(C.evm.V.abi).encodeFunctionData('verifyProof', a);
    const rc = await (await A0.sendTransaction({ to: rc0.contractAddress, data, gasLimit: 3000000, maxFeePerGas: 0n, maxPriorityFeePerGas: 0n })).wait();
    const t = await hre.network.provider.send('debug_traceTransaction', [rc.hash, { disableStorage: true, disableMemory: false, disableStack: true }]);
    const h = crypto.createHash('sha256'); const mem = []; const ops = [];
    for (const s of t.structLogs) { const m = s.memory || []; mem.push(32 * m.length); ops.push(s.op); for (const w of m) h.update(w); h.update('|'); }
    const name = `${circuit}-${backend}-j0.memsize.json.gz`;
    const buf = zlib.gzipSync(Buffer.from(JSON.stringify({ proof_id: id, gas: t.gas, steps: t.structLogs.length, ops, memSize: mem })), { level: 9, mtime: 0 });
    fs.writeFileSync(path.join(OUT, 'raw', name), buf);
    items.push({ proof_id: id, gas_used: Number(rc.gasUsed), steps: t.structLogs.length, memory_words_stream_sha256: h.digest('hex'), raw_file: name, raw_sha256: sha(buf) });
    console.log(`${id}: steps ${t.structLogs.length}`);
  }
  fs.writeFileSync(path.join(OUT, 'retrace-mem-summary.json'), JSON.stringify({ utc: new Date().toISOString(), items }, null, 1)); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
