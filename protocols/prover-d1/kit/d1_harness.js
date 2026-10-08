'use strict';
// V2-PRV-D1-01 container harness (Mac M5, Docker Desktop, linux/arm64, allocation cpu8 = VM vCPUs 1-8).
// One container = one round (kind preflight | dryrun | primary). Started only by kit/run-d1.sh.
//   node --expose-gc /opt/zcorp-d1/d1_harness.js --kind primary --round <r> --attempt <a>
// Mounts: /d1art (frozen artifacts, read-only), /d1keys (PLONK keys regenerated and hash-checked, read-only),
//         /results (writable). Env: ZCORP_CPUS=8, ZCORP_PROFILE=cpu8, ZCORP_SESSION_ID, ZCORP_IMAGE_ID.
// Metrics per config (v3 definitions): witness_ms = snarkjs.wtns.calculate; prove_ms = end-to-end proving call with the
// key path under a warm file cache (includes opening / parsing / reading the key); verify_ms = first verify with the
// in-memory vkey; wall_ms = witness start -> verify end. Inputs are frozen synthetic JSON files (no input stage).
const fs = require('fs'); const path = require('path'); const os = require('os'); const crypto = require('crypto');
const { performance } = require('perf_hooks');
const ENG = process.env.D1_ENGINEERING_TEST === '1';   // off-host engineering test only (never set by run-d1.sh): skips host/container assertions
const ART = ENG ? process.env.D1_ART : '/d1art', KEYS = ENG ? process.env.D1_KEYS : '/d1keys', OUT = ENG ? process.env.D1_OUT : '/results';
const CELLS = { d10: 'input_d10.json', p1150: 'input_pad.json', p1180: 'input_pad.json', d11: 'input_d11.json' };
const CONFIGS = Object.keys(CELLS).flatMap((c) => ['groth16', 'plonk'].map((b) => `${b}:${c}`));
const EXPECT = { cpuset: '1-8', cpus: 8, memory_max: '8589934592', swap_max: '0', arch: 'arm64', node: 'v18.20.8', snarkjs: '0.7.5', ffjavascript: '0.3.1' };
const arg = (n) => { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : undefined; };
const rd = (p) => { try { return fs.readFileSync(p, 'utf8').trim(); } catch (_) { return null; } };
const kv = (t) => Object.fromEntries((t || '').split('\n').filter(Boolean).map((l) => { const [k, v] = l.split(/\s+/); return [k, Number(v)]; }));
const cg = () => ({ cpuset: rd('/sys/fs/cgroup/cpuset.cpus.effective'), cpu_max: rd('/sys/fs/cgroup/cpu.max'), memory_max: rd('/sys/fs/cgroup/memory.max'),
  swap_max: rd('/sys/fs/cgroup/memory.swap.max'), memory_peak: Number(rd('/sys/fs/cgroup/memory.peak')) || null,
  oom_kill: kv(rd('/sys/fs/cgroup/memory.events')).oom_kill || 0, nr_throttled: kv(rd('/sys/fs/cgroup/cpu.stat')).nr_throttled || 0 });
const sha = (p) => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const pkgDir = (name, from) => { let d = path.dirname(require.resolve(name, from ? { paths: [from] } : undefined)); while (!fs.existsSync(path.join(d, 'package.json'))) d = path.dirname(d); return d; };
const pkgv = (d) => JSON.parse(fs.readFileSync(path.join(d, 'package.json'), 'utf8')).version;
const now = () => new Date().toISOString();
let meta_versions = null;
const order = (r) => CONFIGS.slice().sort((a, b) => { const h = (c) => crypto.createHash('sha256').update(`V2-D1-order|round=${r}|${c}`).digest('hex'); return h(a) < h(b) ? -1 : 1; });
function manifest(file) { return fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((l) => { const m = /^([0-9a-f]{64})\s+\*?(.+)$/.exec(l); return m && { hash: m[1], rel: m[2].replace(/^\.\//, '') }; }).filter(Boolean); }

async function main() {
  const kind = arg('kind'); const round = Number(arg('round') || 0); const attempt = Number(arg('attempt') || 1);
  if (!['preflight', 'dryrun', 'primary'].includes(kind)) throw new Error('usage: --kind preflight|dryrun|primary --round r --attempt a');
  const session = process.env.ZCORP_SESSION_ID || 'none'; const started = now(); const fails = [];
  const need = (c, m) => { if (!c) fails.push(m); };
  const needHost = (c, m) => { if (!ENG) need(c, m); };
  const cg0 = cg(); const ad = globalThis.__zcorpCpuVisibility;
  needHost(cg0.cpuset === EXPECT.cpuset, `cpuset ${cg0.cpuset}`); needHost((cg0.cpu_max || '').startsWith('max'), `cpu quota ${cg0.cpu_max}`);
  needHost(cg0.memory_max === EXPECT.memory_max, `memory.max ${cg0.memory_max}`); needHost(cg0.swap_max === EXPECT.swap_max, `swap ${cg0.swap_max}`);
  needHost(cg0.oom_kill === 0 && cg0.nr_throttled === 0, 'oom/throttle before start');
  needHost(ad && ad.os_cpus_after_adapter === EXPECT.cpus && os.cpus().length === EXPECT.cpus && os.availableParallelism() === EXPECT.cpus, 'CPU-visibility adapter / affinity');
  needHost(process.arch === EXPECT.arch, `arch ${process.arch}`); needHost(process.version === EXPECT.node, `node ${process.version}`);
  // artifacts and regenerated keys must match the frozen manifests
  for (const { hash, rel } of manifest(path.join(ART, 'ARTIFACTS-SHA256SUMS'))) need(sha(path.join(ART, rel)) === hash, `artifact hash ${rel}`);
  for (const { hash, rel } of manifest(path.join(ART, 'KEYS-SHA256SUMS'))) need(sha(path.join(KEYS, rel)) === hash, `regenerated key hash ${rel}`);
  const files = (c, b) => ({ wasm: path.join(ART, c, 'circuit.wasm'), zkey: b === 'plonk' ? path.join(KEYS, c, 'plonk.zkey') : path.join(ART, c, 'groth16.zkey'), vkey: path.join(ART, c, `${b}.vkey.json`), input: path.join(ART, 'inputs', CELLS[c]) });
  for (const cfg of CONFIGS) { const [b, c] = cfg.split(':'); const f = files(c, b); fs.readFileSync(f.zkey); fs.readFileSync(f.wasm); }   // warm file cache
  const snarkjs = require('snarkjs');
  const sjDir = pkgDir('snarkjs'); const ffDir = pkgDir('ffjavascript', sjDir); meta_versions = { snarkjs: pkgv(sjDir), ffjavascript: pkgv(ffDir) };
  need(meta_versions.snarkjs === EXPECT.snarkjs, `snarkjs ${meta_versions.snarkjs}`); need(meta_versions.ffjavascript === EXPECT.ffjavascript, `ffjavascript ${meta_versions.ffjavascript}`);
  const meta = { engineering_test: ENG, campaign_id: 'V2-PRV-D1-01', session_id: session, kind, round, attempt, image_id: process.env.ZCORP_IMAGE_ID || null, versions: meta_versions, started_at_utc: started, adapter: ad || null, cgroup_before: cg0 };
  const outDir = path.join(OUT, 'raw'); fs.mkdirSync(outDir, { recursive: true });
  const tag = `${kind}-r${String(round).padStart(2, '0')}-a${attempt}`;
  const done = (status, extra = {}) => { Object.assign(meta, extra, { ended_at_utc: now(), status, failures: fails, cgroup_after: cg() }); fs.writeFileSync(path.join(outDir, `${tag}.meta.json`), JSON.stringify(meta, null, 1) + '\n'); };
  if (fails.length) { done('assertion-failed'); console.error('ASSERTIONS FAILED', fails); process.exit(3); }
  // in-process warm-up (discarded): one Groth16 and one PLONK pipeline at d10
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'd1-'));
  for (const b of ['groth16', 'plonk']) {
    const f = files('d10', b); const w = path.join(tmp, `warm-${b}.wtns`);
    await snarkjs.wtns.calculate(JSON.parse(fs.readFileSync(f.input)), f.wasm, w); const { proof, publicSignals } = await snarkjs[b].prove(f.zkey, w);
    if (!(await snarkjs[b].verify(JSON.parse(fs.readFileSync(f.vkey)), publicSignals, proof))) { fails.push(`warm-up ${b} invalid`); }
  }
  const conc = globalThis.curve_bn128 && globalThis.curve_bn128.tm ? globalThis.curve_bn128.tm.concurrency : null; meta.ffjavascript_concurrency = conc;
  needHost(conc === EXPECT.cpus, `ffjavascript concurrency ${conc}`);
  if (fails.length) { done('assertion-failed'); console.error('ASSERTIONS FAILED', fails); process.exit(3); }
  if (kind === 'preflight') { done('ok'); console.log('preflight ok'); process.exit(0); }
  // the round's configurations, in the frozen seeded order (recomputed and compared with the frozen schedule)
  const sched = fs.readFileSync(path.join(ART, 'schedule.csv'), 'utf8').split('\n').slice(1).filter(Boolean).map((l) => l.split(',')).find((x) => x[0] === kind && Number(x[1]) === round);
  const list = kind === 'dryrun' ? CONFIGS : order(round);
  if (kind === 'primary' && (!sched || sched[2] !== list.join(';'))) { fails.push('schedule mismatch'); done('assertion-failed'); process.exit(3); }
  const rows = []; let pos = 0;
  for (const cfg of list) {
    const [b, c] = cfg.split(':'); const f = files(c, b); const input = JSON.parse(fs.readFileSync(f.input)); const vk = JSON.parse(fs.readFileSync(f.vkey));
    const w = path.join(tmp, `${b}-${c}.wtns`); if (global.gc) global.gc(); const t0s = now();
    const t0 = performance.now(); await snarkjs.wtns.calculate(input, f.wasm, w); const t1 = performance.now();
    const { proof, publicSignals } = await snarkjs[b].prove(f.zkey, w); const t2 = performance.now();
    const ok = await snarkjs[b].verify(vk, publicSignals, proof); const t3 = performance.now(); const mu = process.memoryUsage();
    rows.push({ campaign_id: 'V2-PRV-D1-01', session_id: session, kind, round, attempt, position: ++pos, config: cfg, backend: b, cell: c, started_at_utc: t0s,
      witness_ms: +(t1 - t0).toFixed(3), prove_ms: +(t2 - t1).toFixed(3), verify_ms: +(t3 - t2).toFixed(3), wall_ms: +(t3 - t0).toFixed(3),
      proof_valid: ok ? 1 : 0, root_matches: (publicSignals.length === 1 && publicSignals[0] === input.root) ? 1 : 0, heap_used_mb: +(mu.heapUsed / 1048576).toFixed(1), rss_mb: +(mu.rss / 1048576).toFixed(1) });
  }
  const hdr = Object.keys(rows[0]); fs.writeFileSync(path.join(outDir, `${tag}.csv`), [hdr.join(','), ...rows.map((r) => hdr.map((h) => r[h]).join(','))].join('\n') + '\n');
  const cg1 = cg(); const bad = rows.filter((r) => !r.proof_valid || !r.root_matches).length;
  done(bad || cg1.oom_kill || cg1.nr_throttled ? 'failed' : 'ok', { rows: rows.length, invalid_rows: bad });
  console.log(`${tag}: ${rows.length} rows, invalid ${bad}, oom ${cg1.oom_kill}, throttled ${cg1.nr_throttled}`); process.exit(bad || cg1.oom_kill || cg1.nr_throttled ? 4 : 0);
}
main().catch((e) => { console.error(e); process.exit(1); });
