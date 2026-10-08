// V2-C2 stage-2 structural derivation (deterministic; NOT a cost measurement): executes the frozen compiled verifier on
// EDR (osaka, registered network configuration) for each proof of a manifest and writes ONLY the structural record used
// by c2_model.py. It never writes or prints gasUsed, gas or gasCost. The EVM gas of a registered cell is measured only by
// the registered harness.
//   HF=osaka MANIFEST=<manifest.json> OUT=<records.jsonl> npx hardhat run c2_structural.js
// manifest: [{proof_id, circuit, backend, k, compiled: <compiled artifact json>, proof_file: <corpus proof json>}]
// record: {proof_id, circuit, backend, k, proof_file_sha256, verifier_runtime_sha256, verifier_runtime_bytes, calldata_bytes,
//          status, returns_true, ops:{OP:n}, precompile_calls:[{addr,in_len,out_len}], keccak_sizes:[], copies:[[op,len]],
//          mcopy_sizes:[], exp_exponent_bytes:[], heap_events, heap_final_bytes, steps}
// Heap events follow ZKsync OS v0.4.0 resize_heap call sites (evm_interpreter/src: utils.rs resize_heap_implementation;
// instructions/heap.rs, system.rs, host.rs, control_flow.rs), as in V2-M7B-A.
const fs = require('fs'); const crypto = require('crypto');
const hre = require('hardhat'); const { ethers } = hre;
const P = require(process.env.C2_PROOFS_LIB || (process.env.HOME + '/full/harness/lib/proofs'));
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const I = (x) => BigInt(x.startsWith('0x') ? x : '0x' + x);
const ceil32 = (x) => (x + 31n) / 32n * 32n;
function regions(op, s) {
  const t = (i) => I(s[s.length - 1 - i]);
  if (op === 'MLOAD' || op === 'MSTORE') return [[t(0), 32n]];
  if (op === 'MSTORE8') return [[t(0), 1n]];
  if (op === 'KECCAK256' || op === 'SHA3' || op === 'RETURN' || op === 'REVERT' || op.startsWith('LOG')) return [[t(0), t(1)]];
  if (op === 'CALLDATACOPY' || op === 'CODECOPY' || op === 'RETURNDATACOPY') return [[t(0), t(2)]];
  if (op === 'MCOPY') return [[t(0) > t(1) ? t(0) : t(1), t(2)]];
  if (op === 'EXTCODECOPY') return [[t(1), t(3)]];
  if (op === 'STATICCALL' || op === 'DELEGATECALL') return [[t(2), t(3)], [t(4), t(5)]];
  if (op === 'CALL' || op === 'CALLCODE') return [[t(3), t(4)], [t(5), t(6)]];
  if (op === 'CREATE' || op === 'CREATE2') return [[t(1), t(2)]];
  return [];
}
function structure(logs) {
  const ops = {}; const calls = []; const kec = []; const copies = []; const mcopy = []; const expb = []; let heap = 0n; let ev = 0;
  for (const x of logs) {
    if (x.depth !== 1) throw new Error('unexpected nested EVM frame');
    ops[x.op] = (ops[x.op] || 0) + 1; const s = x.stack; const t = (i) => I(s[s.length - 1 - i]);
    if (x.op === 'STATICCALL' || x.op === 'CALL' || x.op === 'DELEGATECALL' || x.op === 'CALLCODE') {
      const a = t(1); const o = (x.op === 'CALL' || x.op === 'CALLCODE') ? 1 : 0;
      calls.push({ addr: a < 0x100n ? '0x' + a.toString(16) : 'contract', in_len: Number(t(3 + o)), out_len: Number(t(5 + o)) });
    }
    if (x.op === 'KECCAK256' || x.op === 'SHA3') kec.push(Number(t(1)));
    if (/COPY$/.test(x.op) && x.op !== 'MCOPY') copies.push([x.op, Number(x.op === 'EXTCODECOPY' ? t(3) : t(2))]);
    if (x.op === 'MCOPY') mcopy.push(Number(t(2)));
    if (x.op === 'EXP') { const e = t(1); expb.push(e === 0n ? 0 : Math.floor((e.toString(2).length - 1) / 8) + 1); }
    for (const [off, len] of regions(x.op, s)) { if (len === 0n) continue; const n = ceil32(off + len); if (n > heap) { ev++; heap = n; } }
  }
  return { ops, precompile_calls: calls, keccak_sizes: kec, copies, mcopy_sizes: mcopy, exp_exponent_bytes: expb, heap_events: ev, heap_final_bytes: Number(heap), steps: logs.length };
}
async function main() {
  if (hre.network.config.hardfork !== 'osaka') throw new Error('hardfork must be osaka');
  const M = JSON.parse(fs.readFileSync(process.env.MANIFEST, 'utf8')); const [A0] = await ethers.getSigners(); const out = [];
  for (const m of M) {
    const Cc = JSON.parse(fs.readFileSync(m.compiled, 'utf8')); const raw = fs.readFileSync(m.proof_file); const { id, proof, publicSignals } = JSON.parse(raw);
    if (id !== m.proof_id || publicSignals.length !== m.k || Cc.backend !== m.backend || Cc.circuit !== m.circuit) throw new Error(`manifest mismatch ${m.proof_id}`);
    const a = await P.args(m.backend, proof, publicSignals);
    const f = new ethers.ContractFactory(Cc.evm.V.abi, Cc.evm.V.bytecode, A0);
    const rc0 = await (await A0.sendTransaction({ ...(await f.getDeployTransaction()), gasLimit: 15000000, maxFeePerGas: 0n, maxPriorityFeePerGas: 0n })).wait();
    const code = await ethers.provider.getCode(rc0.contractAddress); const rsha = sha(Buffer.from(code.slice(2), 'hex'));
    if (rsha !== Cc.evm.V.runtime_sha256) throw new Error(`runtime sha ${m.proof_id}`);
    const data = new ethers.Interface(Cc.evm.V.abi).encodeFunctionData('verifyProof', a);
    const rc = await (await A0.sendTransaction({ to: rc0.contractAddress, data, gasLimit: 3000000, maxFeePerGas: 0n, maxPriorityFeePerGas: 0n })).wait();
    const t = await hre.network.provider.send('debug_traceTransaction', [rc.hash, { disableStorage: true, disableMemory: true, disableStack: false }]);
    out.push({ proof_id: id, circuit: m.circuit, backend: m.backend, k: m.k, proof_file_sha256: sha(raw), verifier_runtime_sha256: rsha, verifier_runtime_bytes: (code.length - 2) / 2,
      calldata_bytes: (data.length - 2) / 2, status: rc.status, returns_true: BigInt(t.returnValue ? '0x' + t.returnValue.replace(/^0x/, '') : '0x0') === 1n, ...structure(t.structLogs) });
    console.log(`${id}: structural record written (status ${rc.status})`);
  }
  fs.writeFileSync(process.env.OUT, out.map((r) => JSON.stringify(r)).join('\n') + '\n'); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
