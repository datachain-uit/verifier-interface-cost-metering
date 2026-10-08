// V2-C1 pilot harness: compile the frozen verifiers and the generated managers once (solc for EVM-type regimes, zksolc for EraVM).
// usage: node compile_all.js <outdir> <circuit:k> ...   -> <outdir>/<circuit>-<backend>.json  (bytecode + sha256; used by cell.js, hashed in the run manifest)
const fs = require('fs'); const path = require('path'); const HOME = process.env.HOME;
const S = require('./lib/solc'); const CT = require('./contracts');
const [outdir, ...specs] = process.argv.slice(2); fs.mkdirSync(outdir, { recursive: true });
const files = ['contracts/p0/Verifier.sol', 'contracts/p0/Manager.sol']; const roots = [HOME + '/p0/research'];
for (const spec of specs) {
  const [circuit, k] = spec.split(':');
  for (const backend of (process.env.BACKENDS || 'groth16,plonk').split(',')) {
    const src = CT.sources(circuit, backend, Number(k));
    const E = S.evm(files, { roots, extraSources: src.extra, evmVersion: 'paris' }); const Z = S.zk(files, { roots, extraSources: src.extra });
    const pick = (o) => ({ abi: o.abi, bytecode: o.bytecode, deployed: o.deployed, runtime_sha256: o.runtime_sha256, init_bytes: o.init_bytes, runtime_bytes: o.runtime_bytes, hash: o.hash, bytes: o.bytes, sha256: o.sha256 });
    const out = { circuit, backend, k: Number(k), vname: src.vname, mname: src.mname, verifier_source_sha256: S.sha(src.extra['contracts/p0/Verifier.sol'].content), manager_source_sha256: S.sha(src.extra['contracts/p0/Manager.sol'].content),
      base_source_sha256: S.sha(src.extra['contracts/p0/CredentialManagerBase.sol'].content), evm: { V: pick(E[src.vname]), M: pick(E[src.mname]) }, eravm: { V: pick(Z[src.vname]), M: pick(Z[src.mname]) } };
    fs.writeFileSync(path.join(outdir, `${circuit}-${backend}.json`), JSON.stringify(out));
    console.log(circuit, backend, 'evm V', out.evm.V.runtime_sha256.slice(0, 12), out.evm.V.runtime_bytes, 'eravm V', out.eravm.V.sha256.slice(0, 12), out.eravm.V.bytes);
  }
}
process.exit(0);
