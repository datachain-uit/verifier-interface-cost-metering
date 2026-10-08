#!/usr/bin/env python3
"""Derivation of the reported values and data tables of the article from the frozen packages of this artifact.

Reads ONLY frozen packages; every package manifest and every file read is hash-checked; any mismatch stops the
run (fail closed). It extracts and reshapes values; it never refits, re-scores, changes a tolerance, recomputes a
registered outcome with modified logic, or reads P0 data. The recorded outcome labels of the registered tests
(ADJUDICATED below) are only cross-checked against the frozen scorer outputs.

usage:  python3 analysis/derive_values.py [--deep] [--check]
  --deep   also verify every file listed in every package manifest (otherwise: manifest hash + files read); files
           classified WITHHELD or REGENERABLE in provenance/OBJECT-CLASS.tsv are reported when absent, never read
  --check  build everything in memory and compare with generated/ byte for byte; write nothing
Outputs: generated/article-values.tex, generated/article-values.tsv, generated/data/*.csv, generated/MANIFEST.json
"""
import argparse, csv, hashlib, io, json, re, struct, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]          # artifact root
OBJECT_CLASS = ROOT / 'provenance' / 'OBJECT-CLASS.tsv'

# ---------------------------------------------------------------- frozen packages: artifact path, manifest, manifest SHA-256
PACKAGES = {
    'c1':          ('protocols/c1-preregistration', 'SHA256SUMS', '7dac8482aea1420a30b303c3d45b0c46627da67a976e578fa1d09d7c715bfc8f'),
    'pilot_record': ('data/c1/pilot/record', 'SHA256SUMS', '0d0d05ba19c21db8ac5c9d77d34c1ff1051f23adc671336887bfeaa3c0b271b0'),
    'full_record': ('data/c1/full/record', 'SHA256SUMS', '600815c03df9dd00da2d9e5e0bfbd842c6113e233efc69c774ea13245ca1a613'),
    'ff_record':   ('data/c1/fflonk/record', 'SHA256SUMS', '20eb4f47757f539a9a985cdb6971dc5c05343f35773c74836aa8cd152819066d'),
    'pilot_evidence': ('data/c1/pilot/evidence', 'SHA256SUMS', '08cc9f3afb6cd3b1bfaa0cff802001acb3ce3ee7d89f1d8311ba140893948e98'),
    'full_evidence': ('data/c1/full/evidence', 'SHA256SUMS', 'c267ebe2386c700a9c4aac59af86d558ee9075b0e1ba961f36a9b046b1909307'),
    'ff_evidence': ('data/c1/fflonk/evidence', 'SHA256SUMS', 'd0474fa14e72a7a56da1dc17a0dd6997eaa6608f4ec6fdb3b77817cb107aeddf'),
    'ff_artifacts': ('setup/fflonk', 'TRANSFER-SHA256SUMS', '67e46cc366f1609cd707ba0619037af0ba5d5db810d83fad672edba3ffca3953'),
    'ff_artifacts_cloud': ('setup/fflonk/compiled-verifiers', 'SHA256SUMS', 'cbd3312180ee3ade1786813469c687c56e7aa2729d47c19dde3a25f4499ac5e2'),
    'c2_stage1':   ('protocols/c2-forward-test/stage1', 'SHA256SUMS', 'dfea3a87a775c067ffaa250d05771fb065d32e6a779063eb43eb1561cc626652'),
    'c2_stage2':   ('protocols/c2-forward-test/stage2', 'SHA256SUMS', '9b4a38856f8e871e8e8b0707da6b6cfa673c1948a160524a79a56f76b752c010'),
    'audit':       ('data/posthoc/native-cost-audit', 'SHA256SUMS', '185bb4207a7593df944207dff5f7439d6b9c8f9783d74e6b119395cc9e9f5d1b'),
    'retrace_protocol': ('protocols/posthoc-heap-retrace', 'SHA256SUMS', '1d474ebc5efc2b81c9d070780a412d1059f6f9df54ed72c6f63ac0715673963d'),
    'retrace':     ('data/posthoc/heap-retrace', 'SHA256SUMS', '2144b9050caf38081cbde864e88396219c2cd99dfcc58839b39e174d151e3e94'),
    'd3_protocol': ('protocols/prover-d3', 'SHA256SUMS', 'cdbb72567997f285ee0b2cc4524cb7f894e14b37b92e55b797b9b898a149e62d'),
    'd3':          ('data/prover/d3/reanalysis', 'SHA256SUMS', '026e249b2446b7290cdb0d3e98e6187f41fef35bae1a5c1185f0de3f83701a3b'),
    'd2_prereg':   ('protocols/prover-d2/preregistration', 'SHA256SUMS', '97a05eca76af2083b304eb443f2067ffbaaac2398a2c94a1f25a7fd5765c72b4'),
    'd2_amendments': ('protocols/prover-d2/amendments', 'SHA256SUMS', 'e5158ee65b29dddda9d7fe030c70ca6b3fbb74b443d47cd85230fc208ae18ac3'),
    'd2_final':    ('protocols/prover-d2/final', 'SHA256SUMS', '7fcccbecc76079713fe0f5c4ea21667026c93ce28949421ba4795ba316fb864f'),
    'd2_timed':    ('data/prover/d2/timed', 'SHA256SUMS', '3e0121b14acb895d075878033cca1068689b77a448e47112ff1ba1dad3eee86f'),
    'd2_analysis': ('data/prover/d2/analysis', 'SHA256SUMS', 'c863a1143f15d0b548379b2cd98fa9ae1d23427972fdbdcc02932871c3e883fa'),
    'd1_protocol': ('protocols/prover-d1', 'SHA256SUMS', '12acbadfe805b6fd714f3f6536ca14d95738444f17a7bb08e1d67a1d5f824083'),
    'd1_evidence': ('data/prover/d1/evidence', 'SHA256SUMS', '1984894de8652131e3f70de45a0230eaefe81f4e9dee3b0b5fcf6d79ea407045'),
    'd1_analysis': ('data/prover/d1/analysis', 'SHA256SUMS', '4aa98d292e4fb66af22ba97d174631b6742f22cf4c7e6df5239bdfbc6b4a581e'),
}
SINGLE_FILES = {  # frozen single files outside a SHA256SUMS package
    'amd_ff1': ('protocols/c1-amendment-fflonk-setup/AMD-FF-1.md', '6c4c83d431a5b552ed030a30807c902b880c394d4f228db542c305101f4bf908'),
}

# Recorded outcomes of the registered tests (never recomputed here; cross-checked against the frozen scorer outputs below).
ADJUDICATED = {
    'H1': 'SUPPORTED', 'H2': 'SUPPORTED', 'H3': 'SUPPORTED',
    'H4': 'FALSIFIED', 'H5': 'SUPPORTED', 'H6': 'SUPPORTED',
    'H7': 'SUPPORTED', 'H8': 'FALSIFIED',
    'FP': 'MISSES VISIBLE (2 / 40 strictly unseen)', 'R': 'MISSES VISIBLE (seen-in-P0)',
    'C2': 'PASS, exact, within registered scope',
    'D1': 'VALIDATED - DOMAIN MECHANISM SUPPORTED (tested snarkjs PLONK configuration, Host A)',
}

# Reader-facing outcome wording for Table 3: display labels of the recorded outcomes above; the recorded labels stay
# unchanged in the 'status' column of t3_registered_tests.csv.
READER_OUTCOME = {
    'H1': 'Supported', 'H2': 'Supported', 'H3': 'Supported', 'H4': 'Falsified (F4)', 'H5': 'Supported', 'H6': 'Supported',
    'H7': 'Supported', 'H8': 'Falsified (F8)', 'FP': 'Misses visible', 'R': 'Misses visible (seen in P0)',
    'C2': 'Exact pass within registered scope (not source-complete)', 'D1': 'Supported (tested configuration, Host A)',
}
assert set(READER_OUTCOME) == set(ADJUDICATED)

# Values recorded with the registered outcomes (cross-checked against the generated values; a mismatch fails closed).
RECORDED = {
    'xo-evm-kstar': '14.28', 'xo-zkos-kstar': '3.52', 'xo-eravm27-kstar': '7.01', 'xo-eravm29-mhi': '1.30',
    'ac-total': '5,342', 'sg-match': '43', 'zc-g16-fail': '48', 'npg-meter-pass': '46',
    'npg-rank-match': '21', 'npg-gas-in': '41', 'sem-pass': '24', 'r-strict-pass': '32',
    'p-strict-pass': '38', 'ff-err-k32': '+0.731', 'ff-tau': '0.569', 'ff-h8-fail': '8',
    'c2-proofs': '32', 'c2-structures': '4', 'retrace-matches': '9', 'retrace-constant': '1,669,012',
    'npg-k4-flip-lo': '125', 'npg-k4-flip-hi': '138', 'd1-plonk-rpad': '1.963', 'd1-plonk-ranchor': '1.956',
    'd1-plonk-share': '1.008', 'd1-g16-rpad': '1.012', 'step-b-cpu8': '1.985', 'step-a-cpu8': '1.967',
}

class Fail(Exception):
    pass

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

class Frozen:
    def __init__(self, deep):
        self.deep = deep; self.manifests = {}; self.inputs = {}; self.verified = {}; self.absent = {}
    def manifest(self, pkg):
        if pkg in self.manifests:
            return self.manifests[pkg]
        rel, mname, expected = PACKAGES[pkg]
        mpath = ROOT / rel / mname
        if not mpath.is_file():
            raise Fail(f'{pkg}: manifest missing: {rel}/{mname}')
        raw = mpath.read_bytes(); got = sha256_bytes(raw)
        if got != expected:
            raise Fail(f'{pkg}: manifest hash {got} != frozen {expected}')
        entries = {}
        for line in raw.decode().splitlines():
            m = re.match(r'^([0-9a-f]{64})\s+\*?(.+)$', line.strip())
            if m:
                name = m.group(2).strip()
                entries[name[2:] if name.startswith('./') else name] = m.group(1)
        if not entries:
            raise Fail(f'{pkg}: empty manifest')
        self.manifests[pkg] = entries
        self.verified[pkg] = {'path': rel, 'manifest': mname, 'manifest_sha256': got, 'entries': len(entries), 'deep_verified': False}
        return entries
    def read(self, pkg, rel):
        entries = self.manifest(pkg)
        if rel not in entries:
            raise Fail(f'{pkg}: {rel} not listed in the frozen manifest')
        b = (ROOT / PACKAGES[pkg][0] / rel).read_bytes(); got = sha256_bytes(b)
        if got != entries[rel]:
            raise Fail(f'{pkg}: {rel} hash {got} != manifest {entries[rel]}')
        self.inputs[f'{PACKAGES[pkg][0]}/{rel}'] = got
        return b
    def text(self, pkg, rel):
        return self.read(pkg, rel).decode('utf-8')
    def csv(self, pkg, rel):  # leading '#' comment lines (side-by-side files) are skipped
        return list(csv.DictReader(io.StringIO(''.join(l for l in self.text(pkg, rel).splitlines(True) if not l.startswith('#')))))
    def json(self, pkg, rel):
        return json.loads(self.text(pkg, rel))
    def single(self, key):
        rel, expected = SINGLE_FILES[key]
        got = sha256_file(ROOT / rel)
        if got != expected:
            raise Fail(f'{key}: {rel} hash {got} != frozen {expected}')
        self.inputs[rel] = got
    def deep_verify(self):
        cls = {}
        for line in OBJECT_CLASS.read_text('utf-8').splitlines()[1:]:
            f = line.split('\t')
            if f[1] in ('WITHHELD', 'REGENERABLE'):
                cls[f[0]] = (f[1], f[2])
        for pkg in PACKAGES:
            entries = self.manifest(pkg); base = ROOT / PACKAGES[pkg][0]
            for rel, h in entries.items():
                if not (base / rel).is_file():
                    c = cls.get(f'{PACKAGES[pkg][0]}/{rel}')
                    if c is None or c[1] != h:
                        raise Fail(f'{pkg}: deep verification failed at {rel} (absent and not classified)')
                    self.absent[c[0]] = self.absent.get(c[0], 0) + 1
                    continue
                if sha256_file(base / rel) != h:
                    raise Fail(f'{pkg}: deep verification failed at {rel}')
            self.verified[pkg]['deep_verified'] = True

# ---------------------------------------------------------------- deterministic formatting
def fint(n):
    return f'{int(round(n)):,}'
def ffix(x, d):
    return f'{x:.{d}f}'
def fsig(x, d):
    s = f'{abs(x):.{d}f}'
    return s if float(s) == 0 else ('\\ensuremath{+}' if x > 0 else '\\ensuremath{-}') + s
def fneg(x, d):
    s = f'{abs(x):.{d}f}'
    return ('\\ensuremath{-}' if x < 0 else '') + s
def fpct(rel, d, signed=True):
    return fsig(rel * 100, d) if signed else ffix(abs(rel) * 100, d)

class Values:
    def __init__(self):
        self.v = {}
    def put(self, key, tex, raw, unit, src):
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', key):
            raise Fail(f'bad key {key}')
        if key in self.v:
            raise Fail(f'duplicate key {key}')
        self.v[key] = (tex, raw, unit, src)

def write_csv(rows, header):
    out = io.StringIO(); w = csv.writer(out, lineterminator='\n'); w.writerow(header)
    for r in rows:
        w.writerow(list(r) if isinstance(r, (list, tuple)) else [r[h] for h in header])
    return out.getvalue()

def r1cs_constraints(b):
    if b[:4] != b'r1cs':
        raise Fail('not an r1cs file')
    off = 12; ns = struct.unpack_from('<I', b, 8)[0]
    for _ in range(ns):
        t, sz = struct.unpack_from('<IQ', b, off); off += 12
        if t == 1:
            fs = struct.unpack_from('<I', b, off)[0]
            return struct.unpack_from('<IIIIQI', b, off + 4 + fs)[5]
        off += sz
    raise Fail('r1cs header not found')

def zkey_domain(b):
    if b[:4] != b'zkey':
        raise Fail('not a zkey file')
    off = 12; ns = struct.unpack_from('<I', b, 8)[0]; secs = {}
    for _ in range(ns):
        t, sz = struct.unpack_from('<IQ', b, off); off += 12; secs[t] = off; off += sz
    o = secs[2]; n8q = struct.unpack_from('<I', b, o)[0]; o += 4 + n8q; n8r = struct.unpack_from('<I', b, o)[0]; o += 4 + n8r
    return struct.unpack_from('<III', b, o)[2]

# ---------------------------------------------------------------- derivation, part 1: C1 registered campaigns
S = 'scoring/'

def derive_c1_counts(F, V, D):
    pilot = F.json('pilot_record', 'campaign.json'); full = F.json('full_record', 'campaign.json'); ffc = F.json('ff_record', 'campaign.json')
    summ = F.json('full_record', S + 'summary.json')
    V.put('pilot-cells', fint(pilot['cells']), pilot['cells'], 'cells', 'pilot_record:campaign.json:cells')
    V.put('full-cells', fint(full['cells']['full_completed']), full['cells']['full_completed'], 'cells', 'full_record:campaign.json:cells.full_completed')
    V.put('bridge-cells', fint(full['cells']['bridge_completed']), full['cells']['bridge_completed'], 'cells', 'full_record:campaign.json:cells.bridge_completed')
    br = full['bridge_reproduction']
    V.put('bridge-identical', fint(br['identical']), br['identical'], 'per-proof values', 'full_record:campaign.json:bridge_reproduction.identical')
    V.put('bridge-compared', fint(br['compared']), br['compared'], 'per-proof values', 'full_record:campaign.json:bridge_reproduction.compared')
    devs = int(pilot['deviations']) + int(full['deviations'])
    V.put('deviations-pilot-full', fint(devs), devs, 'deviations', 'pilot_record + full_record:campaign.json:deviations')
    V.put('proofs-per-cell', fint(full['proofs_per_cell']), full['proofs_per_cell'], 'proofs', 'full_record:campaign.json:proofs_per_cell')
    V.put('ff-cells', fint(ffc['cells']['completed']), ffc['cells']['completed'], 'cells', 'ff_record:campaign.json:cells.completed')
    V.put('ff-measurements', fint(ffc['measurement_records']), ffc['measurement_records'], 'measurements', 'ff_record:campaign.json:measurement_records')
    V.put('ac-total', fint(summ['AC']['total']), summ['AC']['total'], 'checks', 'full_record:scoring/summary.json:AC.total')
    V.put('ac-failed', fint(summ['AC']['failed']), summ['AC']['failed'], 'checks', 'full_record:scoring/summary.json:AC.failed')
    if summ['AC']['failed'] != 0:
        raise Fail('AC failures present')
    c1n = len(F.manifest('c1'))
    V.put('c1-files', fint(c1n), c1n, 'files', 'c1:SHA256SUMS entry count')
    ac = F.csv('full_record', S + 'AC_checks.csv')
    def acount(prefix):
        rows = [r for r in ac if r['check'].startswith(prefix)]
        return len(rows), sum(r['ok'] != 'True' for r in rows)
    st_n = st_bad = 0
    for p in ('AC-STRUCT-EVM-precompile-counts', 'AC-STRUCT-EVM-transcript-rounds', 'AC-STRUCT-ERAVM-precompile-counts'):
        n, b = acount(p); st_n += n; st_bad += b
    V.put('ac-struct-total', fint(st_n), st_n, 'checks', 'full_record:scoring/AC_checks.csv:AC-STRUCT-*')
    V.put('ac-struct-failed', fint(st_bad), st_bad, 'checks', 'full_record:scoring/AC_checks.csv:AC-STRUCT-*')
    gn, gb = acount('AC-ZK-gas-rule')
    V.put('ac-gasrule-total', fint(gn), gn, 'checks', 'full_record:scoring/AC_checks.csv:AC-ZK-gas-rule')
    V.put('ac-gasrule-failed', fint(gb), gb, 'checks', 'full_record:scoring/AC_checks.csv:AC-ZK-gas-rule')
    mono = F.csv('full_record', S + 'SG_monotonicity.csv'); mpass = sum(r['verdict'] == 'PASS' for r in mono)
    V.put('mono-pass', fint(mpass), mpass, 'series', 'full_record:scoring/SG_monotonicity.csv')
    V.put('mono-total', fint(len(mono)), len(mono), 'series', 'full_record:scoring/SG_monotonicity.csv')

def derive_c1_ranking(F, V, D):
    sg = F.csv('full_record', S + 'SG_signs.csv'); cnt = {}
    for r in sg:
        cnt[r['sign_verdict']] = cnt.get(r['sign_verdict'], 0) + 1
    for key, lab in (('sg-match', 'MATCH'), ('sg-notscored', 'NOT-SCORED'), ('sg-falsified', 'FALSIFIED')):
        V.put(key, fint(cnt.get(lab, 0)), cnt.get(lab, 0), 'sign predictions', f'full_record:scoring/SG_signs.csv:{lab}')
    fig3a = [{'regime': r['env'], 'metric': r['metric'], 'k': r['k'], 'ratio_plonk_over_groth16': r['ratio'], 'measured_class': r['measured_class'],
              'predicted_sign': r['predicted_sign'], 'sign_verdict': r['sign_verdict'], 'ratio_in_frozen_interval': r['ratio_in_interval'],
              'limit_check': 'yes' if r['k'] == '64' else 'no'} for r in sg]
    D['fig3a_ratio_vs_k.csv'] = write_csv(fig3a, list(fig3a[0].keys()))
    def ratio(env, k):
        r = [x for x in sg if x['env'] == env and x['metric'] == 'Y_dir' and x['k'] == str(k)]
        if len(r) != 1:
            raise Fail(f'ratio {env} {k}')
        return float(r[0]['ratio'])
    for env, tag in (('evm-osaka', 'evm'), ('eravm-29', 'eravm29'), ('eravm-27', 'eravm27'), ('zkos-v32@npg100', 'zkos')):
        x = ratio(env, 1); V.put(f'ratio-{tag}-k1', ffix(x, 3), x, 'PLONK / Groth16', f'full_record:scoring/SG_signs.csv:{env},Y_dir,k=1')
    for env, tag in (('evm-osaka', 'evm'), ('eravm-29', 'eravm29'), ('zkos-v32@npg100', 'zkos')):
        x = ratio(env, 32); V.put(f'ratio-{tag}-k32', ffix(x, 3), x, 'PLONK / Groth16', f'full_record:scoring/SG_signs.csv:{env},Y_dir,k=32')
    xo = F.csv('full_record', S + 'XO_crossovers.csv'); ci = F.csv('c1', '09-numeric-predictions/crossover_intervals.csv')
    xp = sum(r['verdict'] == 'PASS' for r in xo)
    V.put('xo-pass', fint(xp), xp, 'crossovers', 'full_record:scoring/XO_crossovers.csv'); V.put('xo-total', fint(len(xo)), len(xo), 'crossovers', 'full_record:scoring/XO_crossovers.csv')
    cmap = {('evm-osaka', 'Y_dir'): ('evm-osaka', 'dir'), ('eravm-29', 'Y_dir'): ('eravm-29', 'dir'), ('eravm-27', 'Y_dir'): ('eravm-27', 'dir'),
            ('zkos-v32@npg100', 'N_dir'): ('zkos-v32', 'native'), ('zkos-v32@npg100', 'Y_dir'): ('zkos-v32@npg100', 'dir')}
    xrows = []
    for r in xo:
        env, met = cmap[(r['env'], r['metric'])]
        c = [x for x in ci if x['env'] == env and x['metric'] == met]
        if len(c) != 1 or r['verdict'] != 'PASS':
            raise Fail(f'crossover {env} {met}')
        c = c[0]; lohi = json.loads(r['measured_interval'])
        xrows.append({'regime': r['env'], 'metric': r['metric'], 'kstar_measured': r['kstar_measured'], 'measured_lo': repr(float(lohi[0])), 'measured_hi': repr(float(lohi[1])),
                      'frozen_point': c['kstar_point'], 'frozen_lo': c['kstar_lo'], 'frozen_hi': c['kstar_hi'], 'verdict': r['verdict']})
    D['crossovers.csv'] = write_csv(xrows, list(xrows[0].keys()))
    def xput(tag, regime, metric, interval=False):
        r = [x for x in xrows if x['regime'] == regime and x['metric'] == metric][0]
        src = f'full_record:scoring/XO_crossovers.csv:{regime},{metric}; c1:09-numeric-predictions/crossover_intervals.csv'
        if interval:
            V.put(f'xo-{tag}-mlo', ffix(float(r['measured_lo']), 2), float(r['measured_lo']), 'k', src)
            V.put(f'xo-{tag}-mhi', ffix(float(r['measured_hi']), 2), float(r['measured_hi']), 'k', src)
        else:
            V.put(f'xo-{tag}-kstar', ffix(float(r['kstar_measured']), 2), float(r['kstar_measured']), 'k', src)
        V.put(f'xo-{tag}-pred', r['frozen_point'], r['frozen_point'], 'k', src)
        lo = r['frozen_lo']
        V.put(f'xo-{tag}-lo', '\\ensuremath{\\le}1' if lo == '<=1' else ffix(float(lo), 2), lo, 'k', src)
        V.put(f'xo-{tag}-hi', ffix(float(r['frozen_hi']), 2), r['frozen_hi'], 'k', src)
    xput('evm', 'evm-osaka', 'Y_dir'); xput('eravm29', 'eravm-29', 'Y_dir', interval=True); xput('eravm27', 'eravm-27', 'Y_dir'); xput('zkos', 'zkos-v32@npg100', 'Y_dir')
    rn = [x for x in xrows if x['regime'] == 'zkos-v32@npg100' and x['metric'] == 'N_dir'][0]
    V.put('xo-zkos-native-kstar', ffix(float(rn['kstar_measured']), 2), float(rn['kstar_measured']), 'k', 'full_record:scoring/XO_crossovers.csv:zkos-v32@npg100,N_dir')

def derive_c1_heldout(F, V, D):
    R = F.csv('full_record', S + 'R_scoring.csv')
    def rcount(pred):
        rows = [x for x in R if pred(x)]; return sum(x['status'] == 'PASS' for x in rows), len(rows)
    for key, pred, lab in (('r-strict', lambda x: x['heldout'] == 'strictly-unseen', 'strictly-unseen'), ('r-seen', lambda x: x['heldout'] == 'seen-in-P0', 'seen-in-P0'),
                           ('r-v27', lambda x: x['env'] == 'eravm-27', 'eravm-27')):
        p, n = rcount(pred)
        V.put(f'{key}-pass', fint(p), p, 'cells', f'full_record:scoring/R_scoring.csv:{lab}'); V.put(f'{key}-total', fint(n), n, 'cells', f'full_record:scoring/R_scoring.csv:{lab}')
    rd = sum(x['status'] == 'DESCRIPTIVE FAIL' for x in R); V.put('r-limit-descfail', fint(rd), rd, 'cells', 'full_record:scoring/R_scoring.csv:DESCRIPTIVE FAIL')
    rfail = [x for x in R if x['status'] == 'FAIL']
    D['r_misses.csv'] = write_csv(rfail, list(R[0].keys()))
    V.put('r-fail', fint(len(rfail)), len(rfail), 'cells', 'full_record:scoring/R_scoring.csv:FAIL')
    # both registered R misses are reported; row identity and frozen role are verified, values read from the frozen scorer output.
    if sorted((x['env'], x['backend'], x['k'], x['metric'], x['heldout']) for x in rfail) != [('eravm-29', 'plonk', '32', 'Y_app', 'seen-in-P0'), ('eravm-29', 'plonk', '32', 'Y_dir', 'seen-in-P0')]:
        raise Fail('unexpected R failure set (identity or frozen role)')
    for metric in ('Y_dir', 'Y_app'):
        row = [x for x in rfail if x['metric'] == metric][0]; m = metric.replace('_', '').lower()
        src = f'full_record:scoring/R_scoring.csv:eravm-29,plonk,{metric},32,seen-in-P0'
        V.put(f'r-miss-eravm29-plonk-k32-{m}-err', fpct(float(row['err_rel']), 2), float(row['err_rel']), '%', src)
        V.put(f'r-miss-eravm29-plonk-k32-{m}-tau', fpct(float(row['tau']), 2, signed=False), float(row['tau']), '% (frozen tolerance)', src)
    P = F.csv('full_record', S + 'P_scoring.csv'); su = [x for x in P if x['role'] == 'HELD-OUT-k/strictly-unseen']
    sp = sum(x['status'] == 'PASS' for x in su)
    V.put('p-strict-pass', fint(sp), sp, 'cells', 'full_record:scoring/P_scoring.csv:strictly-unseen'); V.put('p-strict-total', fint(len(su)), len(su), 'cells', 'full_record:scoring/P_scoring.csv:strictly-unseen')
    D['p_misses.csv'] = write_csv([x for x in P if x['status'] in ('FAIL', 'DESCRIPTIVE FAIL')], list(P[0].keys()))
    pfl = sum(x['status'] == 'FAIL' for x in P); pdf = sum(x['status'] == 'DESCRIPTIVE FAIL' for x in P)
    V.put('p-fail', fint(pfl), pfl, 'cells', 'full_record:scoring/P_scoring.csv:FAIL'); V.put('p-descfail', fint(pdf), pdf, 'cells', 'full_record:scoring/P_scoring.csv:DESCRIPTIVE FAIL')
    want = {'eravm-29|groth16|c1_ctx_k24|Y_app': 'eravm29-g16-k24-app', 'zkos-v32|groth16|c1_ctx_k24|N_dir': 'zkos-g16-k24-native'}
    sm = [x for x in su if x['status'] == 'FAIL']
    if sorted(x['cell'] for x in sm) != sorted(want):
        raise Fail('unexpected strictly-unseen P misses')
    for x in sm:
        V.put(f'p-miss-{want[x["cell"]]}-err', fpct(float(x['err_rel']), 3), float(x['err_rel']), '%', f'full_record:scoring/P_scoring.csv:{x["cell"]}')
    v27 = [x for x in P if x['cell'].startswith('eravm-27') and x['role'].startswith('HELD-OUT-REGIME')]
    vp = sum(x['status'] == 'PASS' for x in v27)
    V.put('p-v27-pass', fint(vp), vp, 'cells', 'full_record:scoring/P_scoring.csv:eravm-27 HELD-OUT-REGIME'); V.put('p-v27-total', fint(len(v27)), len(v27), 'cells', 'full_record:scoring/P_scoring.csv:eravm-27 HELD-OUT-REGIME')
    hs = {}
    for name, rows, keyf in (('R', R, lambda x: (x['env'], x['metric'], x['heldout'])), ('P', P, lambda x: (x['cell'].split('|')[0], x['cell'].split('|')[-1], x['role']))):
        for x in rows:
            k = (name,) + keyf(x) + (x['status'],); hs[k] = hs.get(k, 0) + 1
    D['fig4_heldout_summary.csv'] = write_csv([list(k) + [v] for k, v in sorted(hs.items())], ['procedure', 'regime', 'metric', 'role', 'status', 'n'])

def derive_c1_zksync(F, V, D):
    ZC = F.csv('full_record', S + 'ZC_scoring.csv'); ZF = F.csv('ff_record', 'scoring-c1/ZC_scoring.csv')
    ffz = [x for x in ZF if x['backend'] == 'fflonk']
    if sorted((x['proof'], x['err_rel'], x['status']) for x in ZC) != sorted((x['proof'], x['err_rel'], x['status']) for x in ZF if x['backend'] != 'fflonk'):
        raise Fail('Groth16 / PLONK ZC rows differ between the FULL and FFLONK scorer runs')
    fig4 = []
    for x in ZC + ffz:
        e = float(x['err_rel']); t = float(x['tau_cond'])
        fig4.append({'test': 'C1-H8 (FFLONK)' if x['backend'] == 'fflonk' else 'C1-H4 (ZC)', 'proof': x['proof'], 'backend': x['backend'], 'k': x['k'], 'relation': x['relation'],
                     'err_rel': x['err_rel'], 'tau_cond': x['tau_cond'], 'err_over_tau': repr(round(e / t, 6)), 'status': x['status'], 'limit_check': 'yes' if x['k'] == '64' else 'no'})
    fig4.sort(key=lambda r: (r['backend'], int(r['k']), r['relation'], r['proof']))
    D['fig4_prediction_errors.csv'] = write_csv(fig4, list(fig4[0].keys()))
    g = [x for x in ZC if x['backend'] == 'groth16' and int(x['k']) <= 32]; pl = [x for x in ZC if x['backend'] == 'plonk' and int(x['k']) <= 32]
    gf = [x for x in g if x['status'] == 'FAIL']; gp = [x for x in g if x['status'] == 'PASS']; plp = [x for x in pl if x['status'] == 'PASS']
    if len(plp) != len(pl) or len(gf) + len(gp) != len(g):
        raise Fail('unexpected ZC status set')
    V.put('zc-g16-fail', fint(len(gf)), len(gf), 'proofs', 'full_record:scoring/ZC_scoring.csv:groth16,k<=32,FAIL')
    V.put('zc-g16-pass', fint(len(gp)), len(gp), 'proofs', 'full_record:scoring/ZC_scoring.csv:groth16,k<=32,PASS')
    V.put('zc-plonk-pass', fint(len(plp)), len(plp), 'proofs', 'full_record:scoring/ZC_scoring.csv:plonk,k<=32,PASS')
    V.put('zc-plonk-total', fint(len(pl)), len(pl), 'proofs', 'full_record:scoring/ZC_scoring.csv:plonk,k<=32')
    zd = sum(x['status'] == 'DESCRIPTIVE FAIL' for x in ZC); V.put('zc-descfail', fint(zd), zd, 'proofs', 'full_record:scoring/ZC_scoring.csv:DESCRIPTIVE FAIL (k = 64)')
    V.put('zc-g16-tau', fpct(float(g[0]['tau_cond']), 4, signed=False), float(g[0]['tau_cond']), '%', 'full_record:scoring/ZC_scoring.csv:groth16 tau_cond')
    V.put('zc-plonk-tau', fpct(float(pl[0]['tau_cond']), 3, signed=False), float(pl[0]['tau_cond']), '%', 'full_record:scoring/ZC_scoring.csv:plonk tau_cond')
    passk = sorted({int(x['k']) for x in gp if x['relation'] == 'ctx'}); failk = sorted({int(x['k']) for x in gf if x['relation'] == 'ctx'})
    if not max(passk) < min(failk):
        raise Fail('Groth16 ZC pass / fail k not separated')
    V.put('zc-g16-last-pass-k', str(max(passk)), max(passk), 'k', 'full_record:scoring/ZC_scoring.csv'); V.put('zc-g16-first-fail-k', str(min(failk)), min(failk), 'k', 'full_record:scoring/ZC_scoring.csv')
    for k in (8, 32):
        es = sorted({float(x['err_rel']) for x in gf if x['k'] == str(k) and x['relation'] == 'ctx'})
        if len(es) != 1:
            raise Fail(f'Groth16 ZC error not constant at k={k}')
        V.put(f'zc-g16-k{k}-err', fpct(es[0], 4), es[0], '%', f'full_record:scoring/ZC_scoring.csv:groth16,ctx,k={k}')
    e = max(float(x['err_rel']) for x in pl); V.put('zc-plonk-max-err', fpct(e, 4), e, '% (per-proof maximum)', 'full_record:scoring/ZC_scoring.csv:plonk,k<=32,max over proofs')
    fr = F.csv('ff_record', 'FFLONK-RESIDUALS-C1-H8-and-C2.csv')
    if len(fr) != 32:
        raise Fail('FFLONK residual rows != 32')
    fp = sum(x['H8_status'] == 'PASS' for x in fr); ff = sum(x['H8_status'] == 'FAIL' for x in fr)
    V.put('ff-h8-pass', fint(fp), fp, 'proofs', 'ff_record:FFLONK-RESIDUALS-C1-H8-and-C2.csv:H8_status'); V.put('ff-h8-fail', fint(ff), ff, 'proofs', 'ff_record:FFLONK-RESIDUALS-C1-H8-and-C2.csv:H8_status')
    V.put('ff-tau', fpct(float(fr[0]['C1_tau_cond_F']), 3, signed=False), float(fr[0]['C1_tau_cond_F']), '%', 'ff_record:FFLONK-RESIDUALS-C1-H8-and-C2.csv:C1_tau_cond_F')
    fk = sorted({int(x['k']) for x in fr if x['H8_status'] == 'FAIL'})
    V.put('ff-fail-k', ', '.join(map(str, fk)), fk, 'k', 'ff_record:FFLONK-RESIDUALS-C1-H8-and-C2.csv:H8_status')
    for k in (1, 4, 16, 32):
        es = {x['C1_ZC_err_rel'] for x in fr if x['k'] == str(k)}
        if len(es) != 1:
            raise Fail(f'FFLONK error not constant at k={k}')
        e = float(es.pop()); V.put(f'ff-err-k{k}', fpct(e, 3), e, '%', f'ff_record:FFLONK-RESIDUALS-C1-H8-and-C2.csv:k={k}')
    ffp = [x for x in F.csv('ff_record', 'scoring-c1/P_scoring.csv') if x['role'] == 'HELD-OUT-BACKEND']
    n = sum(x['status'] == 'PASS' for x in ffp)
    V.put('ff-setp-pass', fint(n), n, 'cells', 'ff_record:scoring-c1/P_scoring.csv:HELD-OUT-BACKEND'); V.put('ff-setp-total', fint(len(ffp)), len(ffp), 'cells', 'ff_record:scoring-c1/P_scoring.csv:HELD-OUT-BACKEND')
    return fr

def derive_c1_intervention(F, V, D):
    NS = F.csv('full_record', S + 'NPG_scoring.csv'); NR = F.csv('full_record', S + 'NPG_ranking.csv'); SW = F.csv('c1', '09-numeric-predictions/zkos_switch_intervals.csv')
    mp = sum(x['meter_verdict'] == 'PASS' for x in NS); gi = sum(x['gas_in_interval'] == 'True' for x in NS); rm = sum(x['verdict'] == 'MATCH' for x in NR)
    V.put('npg-meter-pass', fint(mp), mp, 'cells', 'full_record:scoring/NPG_scoring.csv:meter_verdict'); V.put('npg-meter-total', fint(len(NS)), len(NS), 'cells', 'full_record:scoring/NPG_scoring.csv')
    V.put('npg-gas-in', fint(gi), gi, 'cells', 'full_record:scoring/NPG_scoring.csv:gas_in_interval')
    V.put('npg-rank-match', fint(rm), rm, 'comparisons', 'full_record:scoring/NPG_ranking.csv:verdict'); V.put('npg-rank-total', fint(len(NR)), len(NR), 'comparisons', 'full_record:scoring/NPG_ranking.csv')
    gm = [x for x in NS if x['gas_in_interval'] != 'True']
    if any((x['backend'], x['k']) != ('groth16', '16') for x in gm):
        raise Fail('unexpected npg gas-interval misses')
    V.put('npg-gas-miss', fint(len(gm)), len(gm), 'cells (all Groth16, k = 16)', 'full_record:scoring/NPG_scoring.csv:gas_in_interval')
    k4 = sorted([x for x in NR if x['k'] == '4'], key=lambda x: int(x['npg']))
    flip = [(a, b) for a, b in zip(k4, k4[1:]) if a['measured_class'] != b['measured_class']]
    if len(flip) != 1:
        raise Fail('k = 4 ranking does not reverse exactly once')
    V.put('npg-k4-flip-lo', flip[0][0]['npg'], int(flip[0][0]['npg']), 'npg', 'full_record:scoring/NPG_ranking.csv:k=4')
    V.put('npg-k4-flip-hi', flip[0][1]['npg'], int(flip[0][1]['npg']), 'npg', 'full_record:scoring/NPG_ranking.csv:k=4')
    for b, tag in (('groth16', 'g16'), ('plonk', 'plonk')):
        r = [x for x in SW if x['backend'] == b and x['k'] == '4'][0]
        for suf, col in (('', 'npg_switch'), ('-lo', 'npg_switch_lo'), ('-hi', 'npg_switch_hi')):
            V.put(f'npg-switch-{tag}-k4{suf}', r[col], float(r[col]), 'npg', 'c1:09-numeric-predictions/zkos_switch_intervals.csv:k=4')
    D['fig3b_npg_ranking.csv'] = write_csv(sorted(NR, key=lambda x: (int(x['k']), int(x['npg']))), list(NR[0].keys()))
    D['fig3b_npg_meters.csv'] = write_csv(sorted(NS, key=lambda x: (int(x['k']), int(x['npg']), x['backend'])), list(NS[0].keys()))
    D['fig3b_switch_intervals.csv'] = write_csv([x for x in SW if x['k'] in ('1', '4', '16')], list(SW[0].keys()))
    SE = F.csv('full_record', S + 'SEM_scoring.csv'); sp = sum(x['verdict'] == 'PASS' for x in SE)
    V.put('sem-pass', fint(sp), sp, 'comparisons', 'full_record:scoring/SEM_scoring.csv'); V.put('sem-total', fint(len(SE)), len(SE), 'comparisons', 'full_record:scoring/SEM_scoring.csv')
    RZ = F.json('full_record', 'post-registered/ZKOS-residual-vs-k.json')['line']
    V.put('resid-g16-slope', fneg(RZ['groth16']['slope_native_per_k'], 0), RZ['groth16']['slope_native_per_k'], 'native per public input', 'full_record:post-registered/ZKOS-residual-vs-k.json:line.groth16')
    V.put('resid-plonk-slope', fint(RZ['plonk']['slope_native_per_k']), RZ['plonk']['slope_native_per_k'], 'native per public input', 'full_record:post-registered/ZKOS-residual-vs-k.json:line.plonk')
    V.put('resid-g16-r2', ffix(RZ['groth16']['r2'], 4), RZ['groth16']['r2'], 'R^2', 'full_record:post-registered/ZKOS-residual-vs-k.json:line.groth16.r2')

def derive_posthoc_c2(F, V, D, fr):
    MA = F.json('audit', 'out/M7A-summary.json')
    V.put('audit-calldata-byte', fint(MA['constants']['calldata_byte']), MA['constants']['calldata_byte'], 'native per calldata byte', 'audit:out/M7A-summary.json:constants.calldata_byte')
    m = re.match(r'(\d+) per expansion event \+ (\d+) per byte', MA['constants']['heap'])
    if not m:
        raise Fail('audit heap constant format')
    V.put('audit-heap-event', m.group(1), int(m.group(1)), 'native per heap-expansion event', 'audit:out/M7A-summary.json:constants.heap')
    V.put('audit-heap-byte', m.group(2), int(m.group(2)), 'native per heap byte', 'audit:out/M7A-summary.json:constants.heap')
    V.put('audit-percall', fint(MA['k1_contrast_decomposition']['source_per_call']), MA['k1_contrast_decomposition']['source_per_call'], 'native per call', 'audit:out/M7A-summary.json:k1_contrast_decomposition.source_per_call')
    V.put('audit-proofs-per-backend', fint(MA['remainder_structure']['groth16']['n_proofs']), MA['remainder_structure']['groth16']['n_proofs'], 'proofs', 'audit:out/M7A-summary.json:remainder_structure.groth16.n_proofs')
    MB = F.json('retrace', 'out/M7B-A-summary.json')
    if MB['verdict'] != 'CONFIRMED' or not MB['P3_single_constant']:
        raise Fail('re-trace summary not CONFIRMED')
    V.put('retrace-matches', fint(MB['matches']), MB['matches'], 'k values', 'retrace:out/M7B-A-summary.json:matches'); V.put('retrace-total', fint(len(MB['per_k'])), len(MB['per_k']), 'k values', 'retrace:out/M7B-A-summary.json:per_k')
    V.put('retrace-proofs', fint(MB['proofs']), MB['proofs'], 'proofs', 'retrace:out/M7B-A-summary.json:proofs')
    V.put('retrace-g16-events', fint(MB['P2_groth16_event_counts'][0]), MB['P2_groth16_event_counts'][0], 'events', 'retrace:out/M7B-A-summary.json:P2_groth16_event_counts')
    V.put('retrace-constant', fint(MB['P3_remainder_minus_35E_values'][0]), MB['P3_remainder_minus_35E_values'][0], 'native', 'retrace:out/M7B-A-summary.json:P3_remainder_minus_35E_values')
    diffs = [p['observed_difference'] for p in MB['per_k']]
    V.put('retrace-diffs', ', '.join(map(str, diffs)), diffs, 'PLONK - Groth16 heap events at k = 1, 2, 4, 8, 12, 16, 24, 32, 64', 'retrace:out/M7B-A-summary.json:per_k.observed_difference')
    C2 = F.json('ff_record', 'scoring-c2/C2-SCORES.json')
    if C2['C2_PRIMARY'] != 'PASS' or C2['C2_EXACT'] != 'PASS' or set(C2['C2_XOVER'].values()) != {'MATCH'}:
        raise Fail('C2 scores not PASS / MATCH')
    V.put('c2-proofs', fint(C2['proofs']), C2['proofs'], 'proofs', 'ff_record:scoring-c2/C2-SCORES.json:proofs')
    ns = len({x['k'] for x in fr}); V.put('c2-structures', fint(ns), ns, 'verifier structures (one per k)', 'ff_record:FFLONK-RESIDUALS-C1-H8-and-C2.csv:k')
    V.put('c2-max-abs-err', ffix(C2['max_abs_rel'], 0), C2['max_abs_rel'], 'relative error', 'ff_record:scoring-c2/C2-SCORES.json:max_abs_rel')
    V.put('c2-tau', fpct(C2['tau'], 4, signed=False), C2['tau'], '%', 'ff_record:scoring-c2/C2-SCORES.json:tau')
    rk = sum(x['result'] == 'MATCH' for x in C2['C2_RANK'])
    V.put('c2-rank-match', fint(rk), rk, 'comparisons', 'ff_record:scoring-c2/C2-SCORES.json:C2_RANK'); V.put('c2-rank-total', fint(len(C2['C2_RANK'])), len(C2['C2_RANK']), 'comparisons', 'ff_record:scoring-c2/C2-SCORES.json:C2_RANK')
    cal = F.json('c2_stage1', 'calibration/C2-CALIBRATION.json')
    if cal['C_env'] != MB['P3_remainder_minus_35E_values'][0] or not cal['single_value']:
        raise Fail('C2 C_env differs from the re-trace constant')
    V.put('c2-cenv', fint(cal['C_env']), cal['C_env'], 'native', 'c2_stage1:calibration/C2-CALIBRATION.json:C_env')
    V.put('c2-calibration-proofs', fint(cal['calibration_proofs']), cal['calibration_proofs'], 'Groth16 / PLONK proofs', 'c2_stage1:calibration/C2-CALIBRATION.json:calibration_proofs')

def derive_d1(F, V, D):
    DS = F.json('d1_analysis', 'D1-summary.json'); DR = F.csv('d1_analysis', 'D1-ratios.csv'); DC = F.csv('d1_analysis', 'D1-cells.csv')
    def drow(b, name):
        r = [x for x in DR if x['backend'] == b and x['stage'] == 'prove_ms' and x['ratio'] == name]
        if len(r) != 1:
            raise Fail(f'D1 ratio {b} {name}')
        return r[0]
    for b, tb in (('plonk', 'plonk'), ('groth16', 'g16')):
        for name, tn in (('pad-above/pad-below', 'rpad'), ('d11/d10', 'ranchor'), ('pad-below/d10', 'padbelow-d10'), ('d11/pad-above', 'd11-padabove')):
            r = drow(b, name); src = f'd1_analysis:D1-ratios.csv:{b},prove_ms,{name}'
            V.put(f'd1-{tb}-{tn}', ffix(float(r['median']), 3), float(r['median']), 'median of 20 per-round ratios', src)
            if b == 'plonk' or tn == 'rpad':
                V.put(f'd1-{tb}-{tn}-lo', ffix(float(r['boot_median_lo95']), 3), float(r['boot_median_lo95']), '95% bootstrap interval of the median', src)
                V.put(f'd1-{tb}-{tn}-hi', ffix(float(r['boot_median_hi95']), 3), float(r['boot_median_hi95']), '95% bootstrap interval of the median', src)
    sh = DS['share_of_anchor_step_reproduced']['plonk']
    V.put('d1-plonk-share', ffix(sh, 3), sh, 'share of the anchor step', 'd1_analysis:D1-summary.json:share_of_anchor_step_reproduced.plonk')
    V.put('d1-n', fint(DS['primary_contrast']['plonk']['n']), DS['primary_contrast']['plonk']['n'], 'accepted timed rounds', 'd1_analysis:D1-summary.json:primary_contrast.plonk.n')
    f5 = []
    for c, tc in (('d10', 'd10'), ('p1150', 'padbelow'), ('p1180', 'padabove'), ('d11', 'd11')):
        log = re.sub(r'\x1b\[[0-9;]*m', '', F.text('d1_protocol', f'build-records/{c}/plonk-setup.log')); m = re.search(r'Plonk constraints:\s*(\d+)', log)
        if not m:
            raise Fail(f'PLONK gate count not found for {c}')
        gates = int(m.group(1)); power = F.json('d1_protocol', f'artifacts/{c}/plonk.vkey.json')['power']
        r1c = r1cs_constraints(F.read('d1_protocol', f'artifacts/{c}/circuit.r1cs')); gdom = zkey_domain(F.read('d1_protocol', f'artifacts/{c}/groth16.zkey'))
        if (2 ** (power - 1) < gates <= 2 ** power) is False:
            raise Fail(f'{c}: gates {gates} inconsistent with PLONK power {power}')
        for b in ('plonk', 'groth16'):
            r = [x for x in DC if x['backend'] == b and x['cell'] == c and x['stage'] == 'prove_ms']
            if len(r) != 1:
                raise Fail(f'D1 cell {b} {c}')
            r = r[0]
            f5.append({'backend': b, 'cell': c, 'r1cs_constraints': r1c, 'plonk_gates': gates, 'plonk_domain_power': power, 'groth16_domain_size': gdom, 'n': r['n'], 'median_ms': r['median'],
                       'q1_ms': r['q1'], 'q3_ms': r['q3'], 'min_ms': r['min'], 'max_ms': r['max'], 'cv': r['cv'], 'boot_lo95_ms': r['boot_median_lo95'], 'boot_hi95_ms': r['boot_median_hi95']})
        V.put(f'd1-gates-{tc}', fint(gates), gates, 'PLONK gates', f'd1_protocol:build-records/{c}/plonk-setup.log')
        V.put(f'd1-power-{tc}', str(power), power, 'log2 PLONK domain size', f'd1_protocol:artifacts/{c}/plonk.vkey.json:power')
        V.put(f'd1-r1cs-{tc}', fint(r1c), r1c, 'R1CS constraints', f'd1_protocol:artifacts/{c}/circuit.r1cs')
        V.put(f'd1-g16dom-{tc}', fint(gdom), gdom, 'Groth16 domain size', f'd1_protocol:artifacts/{c}/groth16.zkey')
        pm = float([x for x in f5 if x['backend'] == 'plonk' and x['cell'] == c][0]['median_ms']); gm = float([x for x in f5 if x['backend'] == 'groth16' and x['cell'] == c][0]['median_ms'])
        V.put(f'd1-plonk-ms-{tc}', fint(pm), pm, 'ms (median, n = 20)', f'd1_analysis:D1-cells.csv:plonk,{c},prove_ms')
        V.put(f'd1-g16-ms-{tc}', ffix(gm, 1), gm, 'ms (median, n = 20)', f'd1_analysis:D1-cells.csv:groth16,{c},prove_ms')
    D['fig5_d1_cells.csv'] = write_csv(f5, list(f5[0].keys()))
    D['fig5_d1_ratios.csv'] = write_csv([x for x in DR if x['stage'] == 'prove_ms'], list(DR[0].keys()))
    V.put('d1-boundary', fint(2 ** 15), 2 ** 15, 'gates (2^15)', 'definition: PLONK domain 2^15 (d1_protocol:D1-PROTOCOL.md section 2)')

def derive_d2_d3(F, V, D):
    A = F.csv('d3', 'out/D3-cell-stats.csv'); B = F.csv('d2_analysis', 'run/D2-cell-stats.csv')
    def med(rows, alloc, depth):
        r = [x for x in rows if x['allocation_profile'] == alloc and x['backend'] == 'plonk' and x['depth'] == str(depth) and x['stage'] == 'prove_ms' and x['rounds'] == '1-5']
        if len(r) != 1:
            raise Fail(f'cell stats {alloc} plonk {depth}: {len(r)} rows')
        return float(r[0]['median'])
    steps = []
    for host, rows, src in (('A', A, 'd3:out/D3-cell-stats.csv'), ('B', B, 'd2_analysis:run/D2-cell-stats.csv')):
        for alloc in ('cpu2', 'cpu4', 'cpu8'):
            m10 = med(rows, alloc, 10); m11 = med(rows, alloc, 11); r = m11 / m10
            steps.append({'host': host, 'source': src, 'allocation': alloc, 'plonk_d10_median_ms': repr(m10), 'plonk_d11_median_ms': repr(m11), 'ratio_d11_over_d10': repr(round(r, 6))})
            V.put(f'step-{host.lower()}-{alloc}', ffix(r, 3), r, 'ratio of frozen medians, PLONK prove d11 / d10', f'{src}:plonk,{alloc},rounds 1-5')
    D['fig5_step_ratios.csv'] = write_csv(steps, list(steps[0].keys()))
    m10 = med(A, 'cpu8', 10); m11 = med(A, 'cpu8', 11)
    V.put('d3-plonk-cpu8-d10-s', ffix(m10 / 1000, 2), m10, 's (median)', 'd3:out/D3-cell-stats.csv:cpu8,plonk,10'); V.put('d3-plonk-cpu8-d11-s', ffix(m11 / 1000, 2), m11, 's (median)', 'd3:out/D3-cell-stats.csv:cpu8,plonk,11')
    ctx = []
    for host, pkg, rs, rr in (('A', 'd3', 'out/D3-allocation-speedups.csv', 'out/D3-backend-ratios.csv'), ('B', 'd2_analysis', 'run/D2-allocation-speedups.csv', 'run/D2-backend-ratios.csv')):
        SP = F.csv(pkg, rs); BR = F.csv(pkg, rr)
        for b, tb in (('groth16', 'g16'), ('plonk', 'plonk')):
            v = [float(x['median']) for x in SP if x['backend'] == b and x['stage'] == 'prove_ms' and x['allocation_from'] == 'cpu2' and x['allocation_to'] == 'cpu8']
            if len(v) != 11:
                raise Fail(f'speedups {host} {b}: {len(v)} depths')
            V.put(f'speedup-{host.lower()}-{tb}-min', ffix(min(v), 2), min(v), 'cpu2 -> cpu8 prove speedup, min over d = 5..15', f'{pkg}:{rs}')
            V.put(f'speedup-{host.lower()}-{tb}-max', ffix(max(v), 2), max(v), 'cpu2 -> cpu8 prove speedup, max over d = 5..15', f'{pkg}:{rs}')
            ctx.append({'host': host, 'quantity': f'{b} prove speedup cpu2->cpu8 (median per depth)', 'min': repr(min(v)), 'max': repr(max(v)), 'n': len(v), 'source': f'{pkg}:{rs}'})
        for alloc in ('cpu2', 'cpu4', 'cpu8'):
            v = [float(x['median']) for x in BR if x['allocation_profile'] == alloc and x['stage'] == 'prove_ms']
            if len(v) != 11:
                raise Fail(f'backend ratios {host} {alloc}: {len(v)}')
            V.put(f'pg-{host.lower()}-{alloc}-min', ffix(min(v), 1), min(v), 'PLONK / Groth16 prove ratio, min over d', f'{pkg}:{rr}')
            V.put(f'pg-{host.lower()}-{alloc}-max', ffix(max(v), 1), max(v), 'PLONK / Groth16 prove ratio, max over d', f'{pkg}:{rr}')
            ctx.append({'host': host, 'quantity': f'PLONK/Groth16 within-round prove ratio {alloc} (median per depth)', 'min': repr(min(v)), 'max': repr(max(v)), 'n': len(v), 'source': f'{pkg}:{rr}'})
    SB = F.csv('d2_analysis', 'side-by-side/side-by-side-backend-ratios.csv')
    q = [float(x['hostB_median']) / float(x['hostA_median']) for x in SB if x['stage'] == 'prove_ms']
    if len(q) != 33:
        raise Fail(f'side-by-side backend ratios: {len(q)}')
    V.put('pg-b-over-a-min', ffix(min(q), 2), min(q), 'Host B / Host A ratio of PLONK / Groth16 medians', 'd2_analysis:side-by-side/side-by-side-backend-ratios.csv')
    V.put('pg-b-over-a-max', ffix(max(q), 2), max(q), 'Host B / Host A ratio of PLONK / Groth16 medians', 'd2_analysis:side-by-side/side-by-side-backend-ratios.csv')
    ctx.append({'host': 'B/A', 'quantity': 'ratio of PLONK/Groth16 prove-ratio medians (33 cells)', 'min': repr(min(q)), 'max': repr(max(q)), 'n': 33, 'source': 'd2_analysis:side-by-side/side-by-side-backend-ratios.csv'})
    D['fig5_d2_d3_context.csv'] = write_csv(ctx, ['host', 'quantity', 'min', 'max', 'n', 'source'])

def derive_design_tables(F, V, D):
    HM = F.csv('c1', '08-calibration-heldout-matrix.csv'); f2 = {}
    for x in HM:
        p = x['cell_id'].split('|')
        if len(p) != 3:
            raise Fail(f'cell id {x["cell_id"]}')
        k = (p[0], p[1], p[2], x['k'], x['role'], x['design_class'], x['campaign']); f2[k] = f2.get(k, 0) + 1
    D['fig2_design_roles.csv'] = write_csv([list(k) + [v] for k, v in sorted(f2.items())], ['regime', 'backend', 'circuit', 'k', 'role', 'design_class', 'campaign', 'n_metric_rows'])
    LG = F.csv('c1', '07-parameter-ledger.csv')
    t2 = [x for x in LG if x['symbol'] in ('n_ecMul(b,k)', 'n_ecAdd(b,k)', 'n_pair(b)', 'rho_b(k)', 'ncalls_b(k)', 'cd(b,k,j)')]
    if len(t2) != 6:
        raise Fail(f'operation-structure rows: {len(t2)}')
    D['t2_operation_structure.csv'] = write_csv(t2, ['symbol', 'meaning', 'environment', 'depends_on_backend', 'depends_on_k', 'source_type', 'source', 'value_P', 'uncertainty'])
    t1 = []
    for line in F.text('c1', '04-toolchain-matrix.md').splitlines():
        if line.startswith('| ') and not line.startswith('| Role') and not line.startswith('|---'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) == 5:
                t1.append(dict(zip(['role', 'tool', 'version_pin', 'used_for', 'class'], cells)))
    if len(t1) < 10:
        raise Fail('toolchain table not parsed')
    D['t1_toolchain_rows.csv'] = write_csv(t1, ['role', 'tool', 'version_pin', 'used_for', 'class'])

def derive_t3(V, D):
    v = lambda k: V.v[k][0].replace('\\ensuremath{-}', '-').replace('\\ensuremath{+}', '+').replace('\\ensuremath{\\le}', '<=')
    n = lambda k: V.v[k][1]
    checks = {'H1': n('ac-struct-failed') == 0 and n('mono-pass') == n('mono-total'), 'H2': n('sg-falsified') == 0 and n('xo-pass') == n('xo-total'),
              'H3': n('ac-failed') == 0 and n('xo-pass') == n('xo-total'), 'H4': n('zc-g16-fail') > 0,
              'H5': n('npg-meter-pass') == n('npg-meter-total') and n('npg-rank-match') == n('npg-rank-total') and n('ac-gasrule-failed') == 0,
              'H6': n('sem-pass') == n('sem-total'), 'H7': n('r-v27-pass') == n('r-v27-total') and n('p-v27-pass') == n('p-v27-total'),
              'H8': n('ff-h8-fail') > 0, 'FP': n('p-strict-pass') < n('p-strict-total'), 'R': n('r-fail') > 0,
              'C2': n('c2-max-abs-err') == 0 and n('c2-rank-match') == n('c2-rank-total')}
    for h, ok in checks.items():
        if not ok:
            raise Fail(f'{h}: frozen outputs inconsistent with the recorded outcome {ADJUDICATED[h]}')
    # values recorded with the registered outcomes must equal the generated values (no threshold is applied anywhere)
    for key, recorded in RECORDED.items():
        if plain(V.v[key][0]).replace('\u2212', '-') != recorded:
            raise Fail(f'{key}: generated {plain(V.v[key][0])} != recorded value {recorded}')
    t3 = [
        ('H1', 'RQ1', 'PRIMARY', 'pre-registered (C1)', 'F1a / F1b', f"structure checks {v('ac-struct-total')}, {v('ac-struct-failed')} failed; ratio monotone in {v('mono-pass')} / {v('mono-total')} series"),
        ('H2', 'RQ1', 'PRIMARY', 'pre-registered (C1)', 'F2a / F2b', f"signs {v('sg-match')} match, {v('sg-falsified')} falsified, {v('sg-notscored')} not scored (frozen-scorer aggregate over the EVM Osaka, EraVM v29, historical EraVM v27, ZKsync OS gas and ZKsync OS native series; incl. four k = 64 limit-check comparisons, descriptive); crossovers {v('xo-pass')} / {v('xo-total')} inside frozen intervals (incl. the historical EraVM v27 validation crossover)"),
        ('H3', 'RQ2', 'PRIMARY', 'pre-registered (C1)', 'F3', f"accounting and control checks {v('ac-total')}, {v('ac-failed')} failed; component-model crossovers inside frozen intervals (ranking / crossover level)"),
        ('H4', 'RQ3', 'PRIMARY', 'pre-registered (C1)', 'F4', f"Groth16: {v('zc-g16-fail')} held-out proofs outside tau_cond {v('zc-g16-tau')} % (from k = {v('zc-g16-first-fail-k')}); PLONK {v('zc-plonk-pass')} / {v('zc-plonk-total')} inside {v('zc-plonk-tau')} %"),
        ('H5', 'RQ2', 'PRIMARY', 'pre-registered (C1; interventional)', 'F5a / F5b / F5c', f"binding meter {v('npg-meter-pass')} / {v('npg-meter-total')}; gas rule {v('ac-gasrule-total')} checks, {v('ac-gasrule-failed')} failed; ranking {v('npg-rank-match')} / {v('npg-rank-total')}; gas interval {v('npg-gas-in')} / {v('npg-meter-total')}"),
        ('H6', 'RQ1', 'VALIDATION', 'pre-registered (C1)', 'F6', f"semantic anchors {v('sem-pass')} / {v('sem-total')}"),
        ('H7', 'RQ2', 'VALIDATION', 'pre-registered (C1)', 'F7', f"EraVM v27: R {v('r-v27-pass')} / {v('r-v27-total')}; P {v('p-v27-pass')} / {v('p-v27-total')}; crossover {v('xo-eravm27-kstar')} inside [{v('xo-eravm27-lo')}, {v('xo-eravm27-hi')}]"),
        ('H8', 'RQ3', 'VALIDATION', 'pre-registered (C1, conditional)', 'F8', f"FFLONK: {v('ff-h8-fail')} proofs outside tau_cond (FFLONK) {v('ff-tau')} % at k = {v('ff-fail-k')}; {v('ff-h8-pass')} inside"),
        ('FP', 'RQ3', 'PRIMARY', 'pre-registered (C1)', 'FP', f"strictly unseen {v('p-strict-pass')} / {v('p-strict-total')}; {v('p-fail')} registered misses over all frozen roles (incl. the two k = 64 ZKsync OS gas cells, which keep their held-out role); {v('p-descfail')} descriptive out-of-interval limit checks (k = 64)"),
        ('R', 'RQ3', 'PRIMARY', 'pre-registered (C1)', 'interpretation rules 1-2', f"strictly unseen {v('r-strict-pass')} / {v('r-strict-total')}; seen in P0 {v('r-seen-pass')} / {v('r-seen-total')} (both registered misses: EraVM v29 PLONK k = 32, " + r"$Y_{\mathrm{dir}}$ and secondary $Y_{\mathrm{app}}$" + f"); {v('r-limit-descfail')} out-of-tolerance limit checks (k = 64), reported descriptively"),
        ('C2', 'RQ3', 'VALIDATION', 'prospective, post-F4; outside C1', 'C2-PRIMARY / EXACT / RANK / XOVER', f"{v('c2-proofs')} proof instances = {v('c2-structures')} verifier structures x {v('proofs-per-cell')} (not independent structural tests); max |e| = {v('c2-max-abs-err')}; rank {v('c2-rank-match')} / {v('c2-rank-total')}; not source-complete"),
        ('D1', 'supporting', 'SUPPORTING', 'pre-registered protocol (D1)', 'reading guide (no threshold)', f"PLONK R_pad {v('d1-plonk-rpad')}, R_anchor {v('d1-plonk-ranchor')}, share {v('d1-plonk-share')}; Groth16 control R_pad {v('d1-g16-rpad')}"),
    ]
    rows = [{'test': t, 'rq': rq, 'class': c, 'registration': reg, 'falsifier_or_criterion': fal, 'result': res, 'status': ADJUDICATED[t],
             'reader_outcome': READER_OUTCOME[t]} for t, rq, c, reg, fal, res in t3]
    D['t3_registered_tests.csv'] = write_csv(rows, list(rows[0].keys()))

VERIFY_ONLY = ('d1_evidence', 'd2_timed', 'd2_prereg', 'd2_amendments', 'd2_final', 'd3_protocol', 'retrace_protocol', 'c2_stage2', 'pilot_evidence', 'full_evidence', 'ff_evidence', 'ff_artifacts', 'ff_artifacts_cloud')

def derive(F):
    V = Values(); D = {}
    derive_c1_counts(F, V, D); derive_c1_ranking(F, V, D); derive_c1_heldout(F, V, D)
    fr = derive_c1_zksync(F, V, D); derive_c1_intervention(F, V, D); derive_posthoc_c2(F, V, D, fr)
    derive_d1(F, V, D); derive_d2_d3(F, V, D); derive_design_tables(F, V, D); derive_t3(V, D)
    for pkg in VERIFY_ONLY:
        F.manifest(pkg)
    return V, D

# ---------------------------------------------------------------- outputs
def macro_file(V):
    out = ['%% Article values -- GENERATED by analysis/derive_values.py; do not edit by hand.',
           '%% Usage: \\vval{key}. Sources and raw values in generated/article-values.tsv.',
           '\\makeatletter',
           '\\newcommand{\\vval}[1]{\\ifcsname avl@#1\\endcsname\\csname avl@#1\\endcsname\\else\\PackageError{articlevalues}{Undefined value key #1}{See generated/article-values.tsv}\\fi}']
    out += [f'\\@namedef{{avl@{k}}}{{{V.v[k][0]}}}' for k in sorted(V.v)]
    out.append('\\makeatother')
    return '\n'.join(out) + '\n'

def values_tsv(V):
    lines = ['key\tlatex\traw\tunit\tsource']
    lines += ['\t'.join([k, V.v[k][0], json.dumps(V.v[k][1]), V.v[k][2], V.v[k][3]]) for k in sorted(V.v)]
    return '\n'.join(lines) + '\n'

def plain(tex):
    return tex.replace('\\ensuremath{-}', '−').replace('\\ensuremath{+}', '+').replace('\\ensuremath{\\le}', '≤')

def build(deep):
    F = Frozen(deep)
    F.single('amd_ff1')
    V, D = derive(F)
    if deep:
        F.deep_verify()
    files = {'generated/article-values.tex': macro_file(V), 'generated/article-values.tsv': values_tsv(V)}
    files.update({f'generated/data/{k}': D[k] for k in sorted(D)})
    man = {'generator': 'analysis/derive_values.py', 'generator_sha256': sha256_file(HERE),
           'value_keys': len(V.v), 'data_outputs': len(D),
           'rules': 'read-only; frozen hashes checked fail-closed; no refit, no rescoring, no tolerance change, no P0 input; recorded outcome labels cross-checked against the frozen scorer outputs',
           'packages': {k: {x: y for x, y in F.verified[k].items() if x != 'deep_verified'} for k in sorted(F.verified)},
           'single_files': {SINGLE_FILES[k][0]: SINGLE_FILES[k][1] for k in sorted(SINGLE_FILES)},
           'inputs_read': {k: F.inputs[k] for k in sorted(F.inputs)}, 'outputs': {k: sha256_bytes(files[k].encode('utf-8')) for k in sorted(files)}}
    files['generated/MANIFEST.json'] = json.dumps(man, indent=1, sort_keys=True, ensure_ascii=False) + '\n'
    return files, len(V.v), len(D), len(F.inputs), (all(F.verified[p]['deep_verified'] for p in F.verified) if deep else False), F.absent

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--deep', action='store_true'); ap.add_argument('--check', action='store_true'); a = ap.parse_args()
    try:
        files, nv, nd, ni, deep_ok, absent = build(a.deep)
    except Fail as e:
        print(f'FAIL CLOSED: {e}', file=sys.stderr); return 2
    mode = 'deep (every listed file of every package re-hashed' + ''.join(f'; {n} {c} absent as classified' for c, n in sorted(absent.items())) + ')' if deep_ok else 'standard (manifests + every file read)'
    if a.check:
        bad = [rel for rel, content in files.items() if not (ROOT / rel).is_file() or (ROOT / rel).read_text('utf-8') != content]
        extra = sorted(f'generated/data/{p.name}' for p in (ROOT / 'generated' / 'data').glob('*') if f'generated/data/{p.name}' not in files)
        if bad or extra:
            print('CHECK FAILED: ' + ', '.join(bad + extra), file=sys.stderr); return 3
        print(f'CHECK PASS [{mode}]: {len(files)} files reproduce byte for byte; {nv} values; {nd} data files; {ni} frozen inputs')
        return 0
    for rel, content in files.items():
        p = ROOT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, 'utf-8')
    print(f'OK [{mode}]: {nv} values, {nd} data files, {ni} frozen inputs read; {len(files)} files written')
    return 0

if __name__ == '__main__':
    sys.exit(main())
