// P0 EraVM runner: anvil-zksync (pinned), EIP-712 txs as in V1, computational gas from the node's refund trace.
const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
const NM = process.env.HOME + '/p0/node/node_modules';
const { ethers } = require(NM + '/ethers'); const { utils, EIP712Signer } = require(NM + '/zksync-ethers');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const MNEMONIC = 'test test test test test test test test test test test junk';
const CHAIN_ID = 260;
function wallets() { const root = ethers.HDNodeWallet.fromPhrase(MNEMONIC, undefined, "m/44'/60'/0'/0"); return [0, 1].map((i) => root.deriveChild(i)); }
async function rpcCall(url, method, params) {
  const r = await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }) });
  const j = await r.json(); if (j.error) throw new Error(`${method}: ${JSON.stringify(j.error).slice(0, 300)}`); return j.result;
}
async function start({ bin = process.env.HOME + '/p0/bin/anvil-zksync-0.6.11', protocol = 29, port = 18011, logFile = '/tmp/anvil-zk.log', extra = [] } = {}) {
  const args = ['--offline', '--timestamp', '1000', '--protocol-version', String(protocol), '--dev-system-contracts', 'built-in', '--enforce-bytecode-compression', 'false',
    '--host', '127.0.0.1', '--port', String(port), '--cache', 'none', '--chain-id', String(CHAIN_ID), '-m', MNEMONIC, '-a', '2', '--balance', '10000',
    '--show-gas-details', 'none', '--show-vm-details', 'none', '--show-storage-logs', 'none', '--log', 'info', '--log-file-path', logFile, ...extra, 'run'];
  const fd = fs.openSync(logFile + '.stdout', 'w');
  const proc = spawn(bin, args, { env: { ...process.env, RUST_LOG: 'zksync_multivm::versions::vm_latest::utils::refund=trace', NO_COLOR: '1' }, stdio: ['ignore', fd, fd] });
  let exited = false; proc.on('exit', () => { exited = true; });
  const url = `http://127.0.0.1:${port}`;
  for (let i = 0; i < 600; i++) { try { await rpcCall(url, 'eth_chainId', []); break; } catch (e) { if (exited) throw new Error('anvil-zksync exited'); await sleep(100); } }
  return { proc, url, logFile, stdoutFile: logFile + '.stdout', stop: async () => { proc.kill('SIGTERM'); for (let i = 0; i < 100 && !exited; i++) await sleep(50); if (!exited) proc.kill('SIGKILL'); } };
}
const KEYS = [['Gas Limit', 'gas_limit'], ['Gas spent on computation', 'computational_gas'], ['Gas spent on pubdata', 'pubdata_gas'], ['Pubdata published', 'pubdata_bytes']];
function parseFee(text) {
  const L = text.split('\n'); const recs = new Map();
  for (let i = 0; i < L.length; i++) { const m = /TRACE Fee benchmark for transaction with hash ([0-9a-f]{64})/.exec(L[i]); if (!m) continue;
    const rec = {}; KEYS.forEach(([k, n], j) => { const mm = new RegExp(`TRACE ${k}: (\\d+)`).exec(L[i + 1 + j] || ''); rec[n] = mm ? Number(mm[1]) : null; });
    recs.set('0x' + m[1], rec); i += 4; }
  return recs;
}
function feeRecords(node) { let t = ''; for (const f of [node.logFile, node.stdoutFile]) if (fs.existsSync(f)) t += fs.readFileSync(f, 'utf8') + '\n'; return parseFee(t); }
async function session(node) {
  const W = wallets(); const signers = W.map((w) => new EIP712Signer(w, CHAIN_ID)); const nonce = [0, 0];
  async function tx({ from = 0, to, data, create, gasLimit = 30000000n, factoryDeps = [], trace = false }) {
    const w = W[from]; const n = nonce[from]++;
    const req = { type: 113, from: w.address, to: create ? utils.CONTRACT_DEPLOYER_ADDRESS : to,
      data: create ? utils.CONTRACT_DEPLOYER.encodeFunctionData('create', [ethers.ZeroHash, create.hash, create.ctor || '0x']) : data,
      value: 0n, nonce: n, chainId: CHAIN_ID, gasLimit: BigInt(gasLimit), maxFeePerGas: 45250000n, maxPriorityFeePerGas: 45250000n,
      customData: { gasPerPubdata: 50000n, factoryDeps: create ? [create.bytecode, ...factoryDeps] : factoryDeps } };
    req.customData.customSignature = await signers[from].sign(req);
    const raw = utils.serializeEip712(req);
    const hash = await rpcCall(node.url, 'eth_sendRawTransaction', [raw]);
    let rc = null; for (let i = 0; i < 600 && !rc; i++) { rc = await rpcCall(node.url, 'eth_getTransactionReceipt', [hash]); if (!rc) await sleep(50); }
    const out = { hash, status: Number(rc.status), gasUsed: Number(rc.gasUsed), contractAddress: rc.contractAddress, calldata_bytes: (req.data.length - 2) / 2 };
    if (trace) out.trace = await rpcCall(node.url, 'debug_traceTransaction', [hash, { tracer: 'callTracer' }]);
    return out;
  }
  async function call(to, data) { try { return { ok: true, ret: await rpcCall(node.url, 'eth_call', [{ from: W[0].address, to, data }, 'latest']) }; } catch (e) { return { ok: false, err: String(e.message).slice(0, 200) }; } }
  return { tx, call, W };
}
module.exports = { start, session, feeRecords, rpcCall, wallets };
