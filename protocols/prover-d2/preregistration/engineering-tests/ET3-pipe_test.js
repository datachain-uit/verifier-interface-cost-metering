// off-host engineering test of kit v3-x86 pipeline/preflight root logic (no timing interpreted)
const path = require('path'); const K = process.env.ZCORP_HARNESS_DIR;
const { makeContext, runPipeline } = require(path.join(K, 'lib/pipeline.js'));
const { committedRoot, loadCorpusManifest, sha256File, REPO } = require(path.join(K, 'lib/common.js'));
(async () => {
  const snarkjs = require(path.join(K, 'node_modules/snarkjs'));
  const { generateInputForDepth } = require(path.join(REPO, 'scripts/setup/generate_input_depth.js'));
  const configs = [5, 8, 13, 15].map((d) => ({ backend: 'groth16', depth: d, key: `groth16:${d}` }));
  const ctx = makeContext({ snarkjs, generateInputForDepth, configs, zkeyHashes: {} });
  const corpus = loadCorpusManifest(); let bad = 0;
  for (const [rel, h] of corpus.map) if (sha256File(path.join(REPO, rel)) !== h) bad++;
  const res = [];
  for (const c of configs) { const r = await runPipeline(ctx, c); res.push({ cfg: c.key, proof_valid: r.proof_valid, root_matches: r.root_matches, input_matches_committed: r.input_matches_committed, expected_root_is_corpus: r.expected_root === committedRoot(c.depth) }); }
  console.log(JSON.stringify({ corpus_entries: corpus.map.size, corpus_bad: bad, res }));
  process.exit(res.every((x) => x.proof_valid && x.root_matches && x.input_matches_committed) && !bad ? 0 : 1);
})().catch((e) => { console.error(e); process.exit(1); });
