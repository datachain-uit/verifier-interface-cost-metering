// Standard-JSON compilation with native solc / zksolc; source unit names kept as in V1 (contracts/..., @openzeppelin/...).
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const { execFileSync } = require('child_process');
const BIN = process.env.HOME + '/p0/bin';
const NM = process.env.HOME + '/p0/node/node_modules';
const IMPORT_RE = /import\s+(?:[^'";]*?from\s+)?["']([^"']+)["']/g;
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
function collect(files, roots, extra = {}) {
  const src = {}; const q = [...files];
  const resolve = (k) => { if (k.startsWith('@openzeppelin/')) return path.join(NM, k); for (const r of roots) { const p = path.join(r, k); if (fs.existsSync(p)) return p; } throw new Error('cannot resolve ' + k); };
  while (q.length) { const k = q.shift(); if (src[k]) continue; const c = extra[k] ? extra[k].content : fs.readFileSync(resolve(k), 'utf8'); src[k] = c;
    for (const m of c.matchAll(IMPORT_RE)) { const i = m[1]; q.push(i.startsWith('.') ? path.posix.normalize(path.posix.join(path.posix.dirname(k), i)) : i); } }
  return Object.fromEntries(Object.keys(src).sort().map((k) => [k, { content: src[k] }]));
}
function evm(files, { roots, evmVersion = 'paris', runs = 200, optimizer = true, extraSources = {} } = {}) {
  const sources = { ...collect(files, roots, extraSources) };
  const input = { language: 'Solidity', sources, settings: { optimizer: { enabled: optimizer, runs }, evmVersion, outputSelection: { '*': { '*': ['abi', 'evm.bytecode.object', 'evm.deployedBytecode.object', 'evm.methodIdentifiers'] } } } };
  const out = JSON.parse(execFileSync(BIN + '/solc-0.8.20', ['--standard-json'], { input: JSON.stringify(input), maxBuffer: 1 << 30 }).toString());
  const errs = (out.errors || []).filter((e) => e.severity === 'error'); if (errs.length) throw new Error(errs.map((e) => e.formattedMessage).join('\n'));
  const res = {};
  for (const [f, by] of Object.entries(out.contracts)) for (const [n, c] of Object.entries(by)) {
    const bc = c.evm.bytecode.object; if (!bc) continue;
    res[n] = { source: f, abi: c.abi, bytecode: '0x' + bc, deployed: '0x' + c.evm.deployedBytecode.object, init_bytes: bc.length / 2, runtime_bytes: c.evm.deployedBytecode.object.length / 2,
      runtime_keccak: null, runtime_sha256: sha(Buffer.from(c.evm.deployedBytecode.object, 'hex')) };
  }
  return res;
}
function zk(files, { roots, extraSources = {}, settings } = {}) {
  const sources = { ...collect(files, roots, extraSources) };
  const st = settings || { optimizer: { enabled: true, mode: '3', fallback_to_optimizing_for_size: true }, codegen: 'yul', evmVersion: 'paris', outputSelection: { '*': { '*': ['abi', 'evm.methodIdentifiers', 'metadata'] } } };
  const dir = fs.mkdtempSync('/tmp/zk-'); const inPath = path.join(dir, 'in.json');
  fs.writeFileSync(inPath, JSON.stringify({ language: 'Solidity', sources, settings: st }));
  const raw = execFileSync(BIN + '/zksolc-1.5.15', ['--standard-json', inPath, '--solc', BIN + '/era-solc-0.8.20-1.0.2'], { maxBuffer: 1 << 30, cwd: dir });
  const out = JSON.parse(raw.toString());
  const errs = (out.errors || []).filter((e) => e.severity === 'error'); if (errs.length) throw new Error(errs.map((e) => e.formattedMessage || e.message).join('\n').slice(0, 3000));
  const res = {};
  for (const [f, by] of Object.entries(out.contracts || {})) for (const [n, c] of Object.entries(by)) {
    const o = c.evm && c.evm.bytecode && c.evm.bytecode.object; if (!o) continue;
    res[n] = { source: f, abi: c.abi, bytecode: '0x' + o.replace(/^0x/, ''), hash: '0x' + c.hash, bytes: o.replace(/^0x/, '').length / 2, sha256: sha(Buffer.from(o.replace(/^0x/, ''), 'hex')) };
  }
  return res;
}
module.exports = { evm, zk, collect, sha };
