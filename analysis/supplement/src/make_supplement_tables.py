"""Supplementary-material tables as LaTeX fragments, rendered deterministically from frozen inputs only.

Usage: python3 analysis/supplement/src/make_supplement_tables.py [--check]
Output: tables/supplement/S*.tex and tables/supplement/SUPPLEMENT-MANIFEST.json (generator path relative to analysis/).

Scope (no new science): every table renders values that already exist in frozen protocol, scoring or evidence files,
or in the canonical generated data (generated/data/); counting is limited to the frozen control records (AC_checks.csv)
and package digests are copied from the manifests recorded in generated/MANIFEST.json. Display formatting only:
relative errors and tolerances are shown in percent by an exact decimal shift; ratios, percentages and timings are
rounded half-up; gas and native-unit magnitudes carry thousands separators and, in a column with any fractional value,
two decimals rounded half to even (the frozen scorer files' own rounding, so that one mean prints identically in every
table); negative values carry a math minus; interval bounds in a column that reaches four integer digits are separated
by '; '; frozen ledger strings (Table S2) are reproduced verbatim apart from documented label mappings. Every input is hash-checked against its own package manifest (SHA256SUMS) where one exists, and recorded in
SUPPLEMENT-MANIFEST.json; --check regenerates every table in memory and requires byte-identical outputs and unchanged
input and generator hashes.
"""
import csv
import hashlib
import io
import json
import sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]             # artifact root
REPO = ROOT
SUPP = ROOT / 'tables' / 'supplement'
OUT = SUPP
C1 = 'protocols/c1-preregistration'
FULL = 'data/c1/full/record'
FF = 'data/c1/fflonk/record'
D3 = 'data/prover/d3/reanalysis'
D3SRC = 'data/prover/d3/source'

INPUTS = {}


def _pkg_check(rel, digest):
    """Verify rel against generated/MANIFEST.json (generated data) or the nearest SHA256SUMS of its package."""
    if rel.startswith('generated/'):
        if rel == 'generated/MANIFEST.json':
            return None
        man = json.loads((ROOT / 'generated' / 'MANIFEST.json').read_text(encoding='utf-8'))
        if man['outputs'].get(rel) != digest:
            raise SystemExit(f'input {rel}: hash differs from generated/MANIFEST.json')
        return 'generated/MANIFEST.json'
    p = (REPO / rel).parent
    while p != REPO and p != p.parent:
        man = p / 'SHA256SUMS'
        if man.exists():
            sub = './' + str((REPO / rel).relative_to(p))
            for line in man.read_text(encoding='utf-8').splitlines():
                parts = line.split(None, 1)
                if len(parts) == 2 and parts[1].strip() in (sub, sub[2:]):
                    if parts[0] != digest:
                        raise SystemExit(f'input {rel}: hash differs from its package manifest')
                    return str(man.relative_to(REPO))
            raise SystemExit(f'input {rel}: not listed in {man.relative_to(REPO)}')
        p = p.parent
    return None


def read_bytes(rel):
    b = (REPO / rel).read_bytes()
    d = hashlib.sha256(b).hexdigest()
    INPUTS[rel] = {'sha256': d, 'package_manifest': _pkg_check(rel, d)}
    return b


def read_csv(rel):
    return list(csv.DictReader(io.StringIO(read_bytes(rel).decode('utf-8'))))


def read_json(rel):
    return json.loads(read_bytes(rel).decode('utf-8'))


def tex(s):
    s = str(s)
    for a, b in (('\\', '\\textbackslash{}'), ('&', '\\&'), ('%', '\\%'), ('_', '\\_'), ('#', '\\#'),
                 ('{', '\\{'), ('}', '\\}'), ('$', '\\$'), ('~', '\\textasciitilde{}'), ('^', '\\^{}')):
        s = s.replace(a, b)
    return s.replace('`', '').replace('**', '')


def _show(d):
    """Thousands separators (as in the article) and a math minus for negative values."""
    out = format(d, ',f')
    return '$-$' + out[1:] if out.startswith('-') else out


def dec(s, places=4):
    """Ratios, timings and other decimals, rounded half-up for display; non-numeric strings are returned escaped."""
    try:
        d = Decimal(str(s).strip())
    except Exception:
        return tex(s)
    return _show(d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def pct(s, places=4):
    """Fraction -> percent by an exact decimal shift, rounded half-up for display."""
    if str(s).strip() == '':
        return '--'
    d = Decimal(str(s).strip()).scaleb(2)
    return _show(d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def _num(v):
    return Decimal(str(v).strip())


def colp(vals, places=2):
    """Decimals shown in a gas / native-unit column: `places` if any value in the column is fractional, else 0."""
    return places if any(_num(v) != _num(v).to_integral_value() for v in vals if str(v).strip()) else 0


def mag(s, places=0):
    """Gas / native-unit magnitude: thousands separators; `places` decimals rounded half to even, the rounding of the
    frozen scorer files, so that one mean prints identically in every table; math minus."""
    return _show(_num(s).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN))


def isep(vals):
    """Interval-bound separator of a column: '; ' when a bound reaches four integer digits (the comma separates
    thousands), ', ' otherwise."""
    return '; ' if any(abs(_num(v)) >= 1000 for v in vals if str(v).strip()) else ', '


REG = {'evm-osaka': 'EVM Osaka', 'eravm-29': 'EraVM v29', 'eravm-27': 'EraVM v27', 'zkos-v32': 'ZKsync OS v32',
       'evm-petersburg': 'EVM Petersburg', 'zkos-v32@npg100': 'ZKsync OS v32 (npg 100)'}
BK = {'groth16': 'Groth16', 'plonk': 'PLONK', 'fflonk': 'FFLONK'}


def reg(s):
    if s in REG:
        return REG[s]
    if s.startswith('zkos-v32@'):
        return 'ZKsync OS v32 (' + tex(s.split('@', 1)[1].replace('npg', 'npg ').replace('+priority_fee=1e8wei', ', priority fee')) + ')'
    return tex(s)


def brk(s):
    """Escape and allow line breaks after '/' in long role labels (display only)."""
    return tex(s).replace('/', '/\\allowbreak{}')


def head(cols, spec, caption_note=None, long=False):
    env = 'longtable' if long else 'tabular'
    lines = [f'\\begin{{{env}}}{{{spec}}}', '\\toprule', ' & '.join(cols) + ' \\\\', '\\midrule']
    if long:
        lines += ['\\endfirsthead', '\\toprule', ' & '.join(cols) + ' \\\\', '\\midrule', '\\endhead',
                  '\\bottomrule', '\\endfoot']
    return lines


def tail(long=False):
    return ['\\end{longtable}'] if long else ['\\bottomrule', '\\end{tabular}']


def stamp(src):
    return f'% GENERATED by supplement/src/make_supplement_tables.py from {src} -- do not edit'


# ----------------------------------------------------------------------------------------------- tables
# Display mapping of frozen toolchain cells (keys reproduce the frozen C1 04-toolchain-matrix.md text verbatim).
T1_DISPLAY = {
    'Poseidon, comparators (V1 templates byte-identical)':
        'Poseidon, comparators',
    'V1 `pot16_final.ptau`': '`pot16_final.ptau`',
    'Groth16 phase 2 base, PLONK setup (deterministic; k = 1 key byte-identical to V1)':
        'Groth16 phase 2 base, PLONK setup (deterministic)',
    'FFLONK d = 11 setup':
        'C1 primary path for the FFLONK d = 11 setup; not used in the executed setup, which used the registered fallback (SM-B)',
    'Verifiers and managers (V1 primary profile)':
        'Verifiers and managers',
    '`-O3`, size fallback, codegen Yul, EVM version Paris (V1 pins)':
        '`-O3`, size fallback, codegen Yul, EVM version Paris',
    '**0.6.11** (V1-compatible pin; sha256 match with V1)':
        '**0.6.11** (binary hashed in pins)',
}


def s_toolchain():
    rows = read_csv('generated/data/t1_toolchain_rows.csv')
    out = [stamp('generated/data/t1_toolchain_rows.csv')]
    out += head(['Role', 'Tool', 'Pinned version', 'Used for'],
                '@{}p{0.17\\linewidth}p{0.21\\linewidth}p{0.30\\linewidth}p{0.26\\linewidth}@{}')
    used = set()
    for r in rows:
        f = []
        for c in ('role', 'tool', 'version_pin', 'used_for'):
            v = r[c]
            if v in T1_DISPLAY:
                used.add(v)
                v = T1_DISPLAY[v]
            f.append(tex(v).replace('--load-state', '\\texttt{-{}-load-state}'))
        out.append(' & '.join(f) + ' \\\\')
    if used != set(T1_DISPLAY):
        raise SystemExit('toolchain display mapping out of date')
    return out + tail()


TARIFF_MEANINGS = ('ecMul precompile calls per verification', 'ecAdd precompile calls', 'pairing pairs (one call)',
                   'keccak-f rounds of the verifier transcript', 'precompile calls per verification', 'intrinsic transaction gas',
                   'calldata gas per non-zero / zero byte', 'ecAdd precompile gas', 'ecMul precompile gas', 'pairing gas', 'keccak gas',
                   'per-transaction native not visible in the opcode trace', 'per precompile-call native not in the opcode table',
                   'tariff per keccak-f round', 'EraVM per-call precompile frame cost (callTracer)', 'ZKsync OS VM v0.4.0 native price',
                   'ZKsync OS fee parameter')
VALUE_DISPLAY = {'npg': '100 (default); intervention levels in Table S4'}


def s_ledger():
    rows = read_csv(f'{C1}/07-parameter-ledger.csv')
    out = [stamp('C1 07-parameter-ledger.csv')]
    out += head(['Symbol', 'Meaning', 'Regime(s)', 'Frozen value', 'Source type'],
                '@{}p{0.13\\linewidth}p{0.25\\linewidth}p{0.14\\linewidth}p{0.28\\linewidth}p{0.14\\linewidth}@{}', long=True)
    for r in rows:
        if r['meaning'] not in TARIFF_MEANINGS:
            continue
        val = VALUE_DISPLAY.get(r['symbol'], r['value_P'])
        out.append(' & '.join([f"\\texttt{{{tex(r['symbol'])}}}", tex(r['meaning']), tex(r['environment']), tex(val),
                               tex(r['source_type'].replace('P0-measured', 'feasibility-measured (P0)').replace('smoke-calibrated', 'calibrated on the pre-C1 v32.0 diagnostic'))]) + ' \\\\')
    return out + tail(long=True)


def s_roles():
    rows = read_csv('generated/data/fig2_design_roles.csv')
    cells = {}
    for r in rows:
        key = (r['regime'], r['circuit'], int(r['k']), r['campaign'], r['design_class'])
        cells.setdefault(key, {})[r['backend']] = r['role']
    order = {'evm-osaka': 0, 'eravm-29': 1, 'zkos-v32@npg100': 2, 'eravm-27': 4, 'evm-petersburg': 5}
    def ok(k):
        return (order.get(k[0], 3), k[0], k[2], k[1])
    out = [stamp('generated/data/fig2_design_roles.csv')]
    out += head(['Regime', 'Relation', '$k$', 'Groth16', 'PLONK', 'FFLONK', 'Design class', 'Campaign'],
                '@{}P{0.11\\linewidth}P{0.10\\linewidth}rP{0.13\\linewidth}P{0.13\\linewidth}P{0.13\\linewidth}P{0.13\\linewidth}P{0.11\\linewidth}@{}',
                long=True)
    for k in sorted(cells, key=ok):
        b = cells[k]
        out.append(' & '.join([reg(k[0]), f'\\texttt{{{tex(k[1])}}}', str(k[2]), brk(b.get('groth16', '--')),
                               brk(b.get('plonk', '--')), brk(b.get('fflonk', '--')), tex(k[4]), tex(k[3].replace('FULL-IF-FFLONK-GATE-PASSES', 'FULL (FFLONK)'))]) + ' \\\\')
    return out + tail(long=True)


def s_npg_levels():
    rows = read_csv(f'{C1}/09-numeric-predictions/zkos_npg_levels.csv')
    out = [stamp('C1 09-numeric-predictions/zkos_npg_levels.csv')]
    out += head(['$k$', 'npg level', 'Purpose of the level'], '@{}rrl@{}')
    for r in rows:
        out.append(f"{r['k']} & {r['npg']} & {tex(r['purpose'])} \\\\")
    return out + tail()


def s_tolerances():
    rows = read_csv(f'{C1}/13-tolerances.csv')
    out = [stamp('C1 13-tolerances.csv')]
    out += head(['Regime', 'Backend', 'Metric', '$\\tau_{\\mathrm{noise}}$ (\\%)', '$\\tau_{\\mathrm{struct}}$ (\\%)',
                 '$\\tau$ (\\%)', '$\\tau_{\\mathrm{cond}}$ (\\%)'], '@{}lllrrrr@{}')
    for r in rows:
        if r['key'].startswith('equality_band'):
            continue
        env, b, m = r['key'].split('|')
        out.append(' & '.join([reg(env), BK[b], tex(m), pct(r['tau_noise']), pct(r['tau_struct']), pct(r['tau_total']),
                               pct(r['tau_cond'])]) + ' \\\\')
    return out + tail()


def s_bands():
    rows = read_csv(f'{C1}/09-numeric-predictions/equality_bands.csv')
    out = [stamp('C1 09-numeric-predictions/equality_bands.csv')]
    out += head(['Regime', '$h_{\\mathrm{G}}$ (\\%)', '$h_{\\mathrm{P}}$ (\\%)', '$\\varepsilon_E$ (\\%)'], '@{}lrrr@{}')
    for r in rows:
        out.append(' & '.join([reg(r['env']), pct(r['h_groth16']), pct(r['h_plonk']), pct(r['epsilon'])]) + ' \\\\')
    return out + tail()


CTRL = {'AC-CTRL-valid': 'valid proof (positive control)', 'AC-CTRL-tampered_proof': 'tampered proof',
        'AC-CTRL-perturb_pub': 'perturbation of each public input', 'AC-CTRL-out_of_field_pub': 'out-of-field public input',
        'AC-CTRL-foreign_vk_proof': 'proof for another key ($k \\in \\{4, 8\\}$)', 'AC-CTRL-replay': 'replay of the direct call',
        'AC-CTRL-unknown_root_tx': 'unknown root (application call)', 'AC-CTRL-cross_regime_identity': 'cross-regime proof identity'}
ACC = {'AC-EVM-trace-closure': 'EVM opcode-trace closure', 'AC-ERAVM-frame-closure': 'EraVM frame closure',
       'AC-STRUCT-EVM-precompile-counts': 'precompile counts (EVM)', 'AC-STRUCT-ERAVM-precompile-counts': 'precompile counts (EraVM)',
       'AC-STRUCT-EVM-transcript-rounds': 'transcript rounds (EVM)', 'AC-ZK-gas-rule': 'ZKsync OS gas rule ($\\pm 1$ gas)'}


def s_controls():
    rows = read_csv(f'{FULL}/scoring/AC_checks.csv')
    envs = ['evm-osaka', 'eravm-29', 'eravm-27', 'zkos-v32', 'other']
    def env_of(e):
        if e in envs:
            return e
        return 'zkos-v32' if e.startswith('zkos-v32') else 'other'
    count, fail = {}, {}
    for r in rows:
        c, e = r['check'], env_of(r['env'])
        count[(c, e)] = count.get((c, e), 0) + 1
        if r['ok'] != 'True':
            fail[c] = fail.get(c, 0) + 1
    used = [e for e in envs if any(k[1] == e for k in count)]
    out = [stamp('full-campaign scoring AC_checks.csv (counted)')]
    out += head(['Check'] + [reg(e) if e != 'other' else 'other' for e in used] + ['Total', 'Failed'],
                '@{}l' + 'r' * (len(used) + 2) + '@{}')
    for group in (CTRL, ACC):
        for c, label in group.items():
            per = [count.get((c, e), 0) for e in used]
            out.append(' & '.join([label] + [f'{x:,}' if x else '--' for x in per] + [f'{sum(per):,}', str(fail.get(c, 0))]) + ' \\\\')
        out.append('\\midrule' if group is CTRL else '')
    total = sum(count.values())
    out.append(' & '.join(['All checks'] + [f"{sum(v for k, v in count.items() if k[1] == e):,}" for e in used] +
                          [f'{total:,}', str(sum(fail.values()))]) + ' \\\\')
    return [l for l in out if l != ''] + tail()


PKG = [('c1', 'Internal pre-registration (C1)'), ('pilot_record', 'Pilot campaign: record and scoring'),
       ('pilot_evidence', 'Pilot campaign: evidence'), ('full_record', 'Full campaign: record and scoring'),
       ('full_evidence', 'Full campaign: evidence'), ('ff_record', 'FFLONK campaign: record, C1 and C2 scoring'),
       ('ff_evidence', 'FFLONK campaign: evidence'), ('ff_artifacts', 'FFLONK setup artifacts and research powers-of-tau records (generated on the workstation)'),
       ('ff_artifacts_cloud', 'FFLONK compiled verifiers and repeated off-chain proof check (separate build environment)'),
       ('c2_stage1', 'Separate prospective test C2: model, calibration, scoring rule'),
       ('c2_stage2', 'Separate prospective test C2: structural derivation and predictions'),
       ('audit', 'Post hoc source-level audit of the F4 residual'), ('retrace_protocol', 'Post hoc deterministic re-trace: protocol'),
       ('retrace', 'Post hoc deterministic re-trace: data'), ('d1_protocol', 'D1: protocol and frozen artifacts'),
       ('d1_evidence', 'D1: evidence'), ('d1_analysis', 'D1: frozen analysis'),
       ('d2_prereg', 'D2: internal pre-registration'), ('d2_amendments', 'D2: recorded amendments'),
       ('d2_final', 'D2: final protocol record'), ('d2_timed', 'D2: timed evidence'), ('d2_analysis', 'D2: analysis'),
       ('d3_protocol', 'D3: protocol'), ('d3', 'D3: descriptive re-analysis')]


def s_packages():
    m = read_json('generated/MANIFEST.json')
    pk = m['packages']
    if set(pk) != {k for k, _ in PKG}:
        raise SystemExit(f'package list changed: {sorted(set(pk) ^ {k for k, _ in PKG})}')
    out = [stamp('generated/MANIFEST.json (package manifests)')]
    out += head(['Package', 'Entries', 'Manifest SHA-256'], '@{}p{0.40\\linewidth}r>{\\ttfamily\\scriptsize}l@{}', long=True)
    for k, label in PKG:
        v = pk[k]
        out.append(f"{tex(label)} & {v['entries']:,} & {v['manifest_sha256']} \\\\")
    amd = [k for k in m['single_files'] if k.endswith('AMD-FF-1.md')]
    for k in amd:
        out.append(f"FFLONK gate record: registered fallback key path and gates G1--G4 (single file) & 1 & {m['single_files'][k]} \\\\")
    return out + tail(long=True)


def s_crossovers():
    rows = read_csv('generated/data/crossovers.csv')
    out = [stamp('generated/data/crossovers.csv')]
    out += head(['Regime', 'Metric', 'Measured $k^{*}$', 'Measured interval', 'Frozen point', 'Frozen interval', 'Verdict'],
                '@{}llrlrll@{}')
    for r in rows:
        lo, hi = dec(r['measured_lo'], 3), dec(r['measured_hi'], 3)
        mi = lo if lo == hi else f'[{lo}, {hi}]'
        flo = tex(r['frozen_lo']).replace('<=', '$\\le$')
        out.append(' & '.join([reg(r['regime']), tex(r['metric']), dec(r['kstar_measured'], 3), mi, tex(r['frozen_point']),
                               f"[{flo}, {tex(r['frozen_hi'])}]", tex(r['verdict'])]) + ' \\\\')
    return out + tail()


def s_heldout():
    rows = read_csv('generated/data/fig4_heldout_summary.csv')
    out = [stamp('generated/data/fig4_heldout_summary.csv')]
    out += head(['Procedure', 'Regime', 'Metric', 'Frozen role', 'Outcome', 'Cells'],
                '@{}llll p{0.24\\linewidth}r@{}', long=True)
    for r in rows:
        out.append(' & '.join([tex(r['procedure']), reg(r['regime']), tex(r['metric']), tex(r['role']), tex(r['status']), r['n']]) + ' \\\\')
    return out + tail(long=True)


def s_r_scoring():
    rows = read_csv(f'{FULL}/scoring/R_scoring.csv')
    out = [stamp('full-campaign scoring R_scoring.csv')]
    out += head(['Regime', 'Backend', 'Metric', '$k$', 'Predicted', 'Measured', 'Error (\\%)', '$\\tau$ (\\%)', 'Outcome', 'Role'],
                '@{}lllrrrrrll@{}', long=True)
    pp, pm = colp([r['pred'] for r in rows]), colp([r['measured'] for r in rows])
    for r in rows:
        out.append(' & '.join([reg(r['env']), BK[r['backend']], tex(r['metric']), r['k'], mag(r['pred'], pp), mag(r['measured'], pm),
                               pct(r['err_rel'], 3), pct(r['tau'], 3), tex(r['status']), tex(r['heldout'])]) + ' \\\\')
    return out + tail(long=True)


def _cell_split(cell):
    env, b, circ, metric = cell.split('|')
    return env, b, circ, metric


def s_p_scoring(src, label):
    rows = read_csv(src)
    out = [stamp(label)]
    out += head(['Regime', 'Backend', 'Relation', 'Metric', 'Role', 'Interval', 'Measured', 'Error (\\%)', 'Outcome'],
                '@{}P{0.11\\linewidth}lllP{0.13\\linewidth}lrrP{0.12\\linewidth}@{}', long=True)
    bounds = [r['lo'] for r in rows] + [r['hi'] for r in rows]
    pb, pm, sep = colp(bounds), colp([r['measured_mean'] for r in rows]), isep(bounds)
    for r in rows:
        env, b, circ, metric = _cell_split(r['cell'])
        out.append(' & '.join([reg(env), BK[b], f'\\texttt{{{tex(circ)}}}', tex(metric), brk(r['role']),
                               f"[{mag(r['lo'], pb)}{sep}{mag(r['hi'], pb)}]" if r['lo'] else '--',
                               mag(r['measured_mean'], pm) if r['measured_mean'] else '--',
                               pct(r['err_rel'], 3) if r['err_rel'] else '--', tex(r['status'])]) + ' \\\\')
    return out + tail(long=True)


def s_zc(src, label):
    rows = read_csv(src)
    out = [stamp(label)]
    out += head(['Proof', 'Backend', '$k$', 'Relation', 'Predicted', 'Measured', 'Error (\\%)', '$\\tau_{\\mathrm{cond}}$ (\\%)', 'Outcome'],
                '@{}lllrrrrrl@{}', long=True)
    pp, pm = colp([r['pred'] for r in rows]), colp([r['measured'] for r in rows])
    for r in rows:
        out.append(' & '.join([f"\\texttt{{{tex(r['proof'])}}}", BK[r['backend']], r['k'], tex(r['relation']), mag(r['pred'], pp),
                               mag(r['measured'], pm), pct(r['err_rel'], 4), pct(r['tau_cond'], 4), tex(r['status'])]) + ' \\\\')
    return out + tail(long=True)


def s_npg_ranking():
    rows = read_csv('generated/data/fig3b_npg_ranking.csv')
    out = [stamp('generated/data/fig3b_npg_ranking.csv')]
    out += head(['$k$', 'npg', 'Gas ratio P/G', 'Measured class', 'Predicted class', 'Ratio in interval', 'Verdict'], '@{}rrrlllr@{}')
    for r in rows:
        out.append(' & '.join([r['k'], r['npg'], dec(r['ratio'], 4), tex(r['measured_class']), tex(r['predicted_class']),
                               tex(r['ratio_in_interval']), tex(r['verdict'])]) + ' \\\\')
    return out + tail()


def s_switch():
    rows = read_csv('generated/data/fig3b_switch_intervals.csv')
    out = [stamp('generated/data/fig3b_switch_intervals.csv')]
    out += head(['Backend', '$k$', 'Predicted native', 'Predicted EVM gas', 'Predicted switch npg', 'Interval'], '@{}lrrrrl@{}')
    pn, pe = colp([r['native_pred'] for r in rows]), colp([r['evm_gas_pred'] for r in rows])
    sep = isep([r['npg_switch_lo'] for r in rows] + [r['npg_switch_hi'] for r in rows])
    for r in rows:
        out.append(' & '.join([BK[r['backend']], r['k'], mag(r['native_pred'], pn), mag(r['evm_gas_pred'], pe), dec(r['npg_switch'], 2),
                               f"[{dec(r['npg_switch_lo'], 2)}{sep}{dec(r['npg_switch_hi'], 2)}]"]) + ' \\\\')
    return out + tail()


def s_cells():
    rows = read_csv(f'{FULL}/scoring/CELL_summary.csv')
    out = [stamp('full-campaign scoring CELL_summary.csv')]
    out += head(['Regime', 'Backend', 'Relation', '$k$', 'Metric', '$n$', 'Mean', 'Min', 'Max', 'Half-range (\\%)'],
                '@{}lllrlrrrrr@{}', long=True)
    pa, pl, ph = (colp([r[c] for r in rows]) for c in ('mean', 'min', 'max'))
    for r in rows:
        out.append(' & '.join([reg(r['env']), BK[r['backend']], f"\\texttt{{{tex(r['circuit'])}}}", r['k'], tex(r['metric']), r['n'],
                               mag(r['mean'], pa), mag(r['min'], pl), mag(r['max'], ph), pct(r['half_range_rel'], 4)]) + ' \\\\')
    return out + tail(long=True)


def s_residual():
    rows = read_csv(f'{FULL}/post-registered/ZKOS-residual-vs-k.csv')
    out = [stamp('full-campaign post-registered ZKOS-residual-vs-k.csv (post hoc)')]
    out += head(['Backend', '$k$', 'Relation', 'Proofs', 'Mean residual (native)', 'Residual per extra input', 'Mean error (\\%)'],
                '@{}lrlrrrr@{}')
    pr = colp([r['mean_residual_native'] for r in rows])
    for r in rows:
        out.append(' & '.join([BK[r['backend']], r['k'], tex(r['relation']), r['n'], mag(r['mean_residual_native'], pr),
                               dec(r['residual_per_extra_input'], 1), dec(r['mean_err_rel_pct'], 4)]) + ' \\\\')
    return out + tail()


def s_c2_rank():
    j = read_json(f'{FF}/scoring-c2/C2-SCORES.json')
    out = [stamp('FFLONK campaign scoring-c2 C2-SCORES.json')]
    out += head(['$k$', 'Versus', 'FFLONK predicted', 'Comparator (registered)', 'Predicted difference', 'Band',
                 'Predicted sign', 'Measured sign', 'Result'], '@{}rlrrrrp{0.09\\linewidth}p{0.09\\linewidth}r@{}')
    rk = j['C2_RANK']
    pf, pc, pd = (colp([r[c] for r in rk]) for c in ('N_hat_fflonk_mean', 'N_registered_mean', 'predicted_difference'))
    for r in rk:
        out.append(' & '.join([str(r['k']), BK[r['versus']], mag(r['N_hat_fflonk_mean'], pf), mag(r['N_registered_mean'], pc),
                               mag(r['predicted_difference'], pd), dec(r['band'], 1), tex(r['predicted_sign']), tex(r['measured_sign']),
                               tex(r['result'])]) + ' \\\\')
    return out + tail()


def s_fflonk_proofs():
    rows = read_csv(f'{FF}/FFLONK-RESIDUALS-C1-H8-and-C2.csv')
    out = [stamp('FFLONK campaign FFLONK-RESIDUALS-C1-H8-and-C2.csv')]
    out += head(['Proof', '$k$', 'Measured native', 'C1 prediction', 'C1 error (\\%)', 'H8 outcome', 'C2 prediction', 'C2 error (\\%)'],
                '@{}lrrrrlrr@{}', long=True)
    pn, p1, p2 = (colp([r[c] for r in rows]) for c in ('N_measured', 'C1_ZC_pred', 'C2_N_hat'))
    for r in rows:
        out.append(' & '.join([f"\\texttt{{{tex(r['proof_id'])}}}", r['k'], mag(r['N_measured'], pn), mag(r['C1_ZC_pred'], p1),
                               pct(r['C1_ZC_err_rel'], 4), tex(r['H8_status']), mag(r['C2_N_hat'], p2), pct(r['C2_err_rel'], 4)]) + ' \\\\')
    return out + tail(long=True)


def s_d1_cells():
    rows = read_csv('generated/data/fig5_d1_cells.csv')
    out = [stamp('generated/data/fig5_d1_cells.csv')]
    out += head(['Backend', 'Cell', 'R1CS constraints', 'PLONK gates', 'PLONK domain', 'Groth16 domain', '$n$',
                 'Median (ms)', '95\\% interval (ms)'], '@{}llrrrrrrl@{}')
    sep = isep([r['boot_lo95_ms'] for r in rows] + [r['boot_hi95_ms'] for r in rows])
    for r in rows:
        out.append(' & '.join([BK[r['backend']], tex(r['cell']), mag(r['r1cs_constraints']), mag(r['plonk_gates']),
                               f"$2^{{{r['plonk_domain_power']}}}$", mag(r['groth16_domain_size']), r['n'], dec(r['median_ms'], 1),
                               f"[{dec(r['boot_lo95_ms'], 1)}{sep}{dec(r['boot_hi95_ms'], 1)}]"]) + ' \\\\')
    return out + tail()


def s_d1_ratios():
    rows = read_csv('generated/data/fig5_d1_ratios.csv')
    out = [stamp('generated/data/fig5_d1_ratios.csv')]
    out += head(['Backend', 'Ratio', '$n$', 'Median of per-round ratios', '95\\% interval', 'Min', 'Max'], '@{}llrrlrr@{}')
    for r in rows:
        out.append(' & '.join([BK[r['backend']], tex(r['ratio']), r['n'], dec(r['median'], 3),
                               f"[{dec(r['boot_median_lo95'], 3)}, {dec(r['boot_median_hi95'], 3)}]", dec(r['min'], 3), dec(r['max'], 3)]) + ' \\\\')
    return out + tail()


def s_steps():
    rows = read_csv('generated/data/fig5_step_ratios.csv')
    out = [stamp('generated/data/fig5_step_ratios.csv')]
    out += head(['Host', 'Source', 'Allocation', 'PLONK depth 10 median (ms)', 'PLONK depth 11 median (ms)', 'Ratio'], '@{}lllrrr@{}')
    for r in rows:
        src = 'D3 (descriptive)' if r['source'].startswith('d3') else ('D2 (qualitative)' if r['source'].startswith('d2') else tex(r['source']))
        out.append(' & '.join([f"Host {tex(r['host'])}", src, tex(r['allocation']), dec(r['plonk_d10_median_ms'], 1),
                               dec(r['plonk_d11_median_ms'], 1), dec(r['ratio_d11_over_d10'], 3)]) + ' \\\\')
    return out + tail()


def s_context():
    rows = read_csv('generated/data/fig5_d2_d3_context.csv')
    out = [stamp('generated/data/fig5_d2_d3_context.csv')]
    out += head(['Host', 'Quantity', 'Min', 'Max', '$n$', 'Source'], '@{}lp{0.45\\linewidth}rrrl@{}')
    for r in rows:
        src = 'D3' if r['source'].startswith('d3') else ('D2' if r['source'].startswith('d2') else 'derived')
        out.append(' & '.join([f"Host {tex(r['host'])}", tex(r['quantity'].replace('->', ' to ')), dec(r['min'], 3), dec(r['max'], 3), r['n'], src]) + ' \\\\')
    return out + tail()


def s_d3_inputs():
    rows = read_json(f'{D3}/out/D3-input-verification.json')
    out = [stamp('D3 package out/D3-input-verification.json')]
    out += head(['Source file', 'SHA-256', 'Verified'], '@{}l>{\\ttfamily\\scriptsize}ll@{}')
    for r in rows:
        name = d3_public(r['path'])
        if r['expected'] != r['actual']:
            raise SystemExit(f'D3 input {name}: expected and actual digests differ')
        if hashlib.sha256(read_bytes(f'{D3SRC}/{name}')).hexdigest() != r['actual']:
            raise SystemExit(f'D3 input {name}: published copy differs from the frozen verification record')
        out.append(f"\\texttt{{{tex(name)}}} & {r['actual']} & {'yes' if r['ok'] else 'no'} \\\\")
    return out + tail()


def d3_public(path):
    """Location, relative to data/prover/d3/source/, of a source file named in the frozen D3 input-verification record."""
    if 'postcorr-20260925/' in path:
        return path.split('postcorr-20260925/', 1)[1]
    if path.endswith('/generated/prover_per_round.csv'):
        return 'reconciliation/prover_per_round.csv'
    raise SystemExit(f'D3 input {path}: no published location')


TABLES = [
    ('S01-toolchain.tex', s_toolchain), ('S02-ledger-prices.tex', s_ledger), ('S03-role-matrix.tex', s_roles),
    ('S04-npg-levels.tex', s_npg_levels), ('S05-tolerances.tex', s_tolerances), ('S06-equality-bands.tex', s_bands),
    ('S07-controls.tex', s_controls), ('S08-packages.tex', s_packages), ('S09-crossovers.tex', s_crossovers),
    ('S10-heldout-summary.tex', s_heldout), ('S11-r-scoring.tex', s_r_scoring),
    ('S12-p-scoring.tex', lambda: s_p_scoring(f'{FULL}/scoring/P_scoring.csv', 'full-campaign scoring P_scoring.csv')),
    ('S13-zc-scoring.tex', lambda: s_zc(f'{FULL}/scoring/ZC_scoring.csv', 'full-campaign scoring ZC_scoring.csv')),
    ('S14-npg-ranking.tex', s_npg_ranking), ('S15-switch-intervals.tex', s_switch), ('S16-cell-summary.tex', s_cells),
    ('S17-fflonk-setp.tex', lambda: s_p_scoring(f'{FF}/scoring-c1/P_scoring.csv', 'FFLONK campaign scoring-c1 P_scoring.csv')),
    ('S18-fflonk-proofs.tex', s_fflonk_proofs), ('S19-residual-posthoc.tex', s_residual), ('S20-c2-rank.tex', s_c2_rank),
    ('S21-d1-cells.tex', s_d1_cells), ('S22-d1-ratios.tex', s_d1_ratios), ('S23-step-ratios.tex', s_steps),
    ('S24-d2-d3-context.tex', s_context), ('S25-d3-inputs.tex', s_d3_inputs),
]


def build():
    outs = {}
    for name, fn in TABLES:
        outs[name] = '\n'.join(fn()) + '\n'
    gen = hashlib.sha256(HERE.read_bytes()).hexdigest()
    manifest = {'generator': 'supplement/src/make_supplement_tables.py', 'generator_sha256': gen,
                'inputs': dict(sorted(INPUTS.items())),
                'outputs': {f'tables/supplement/{n}': hashlib.sha256(t.encode('utf-8')).hexdigest() for n, t in outs.items()}}
    return outs, json.dumps(manifest, indent=1, sort_keys=True) + '\n'


def main():
    check = '--check' in sys.argv[1:]
    outs, manifest = build()
    if check:
        bad = [n for n, t in outs.items() if not (OUT / n).exists() or (OUT / n).read_text(encoding='utf-8') != t]
        mf = SUPP / 'SUPPLEMENT-MANIFEST.json'
        if not mf.exists() or mf.read_text(encoding='utf-8') != manifest:
            bad.append('SUPPLEMENT-MANIFEST.json')
        extra = sorted(p.name for p in OUT.glob('*.tex') if p.name not in outs) if OUT.exists() else []
        if bad or extra:
            raise SystemExit(f'SUPPLEMENT CHECK FAIL: differs {bad}; unexpected {extra}')
        print(f'SUPPLEMENT CHECK PASS: {len(outs)} tables reproduce byte for byte; {len(INPUTS)} frozen inputs hash-checked '
              f'({sum(1 for v in INPUTS.values() if v["package_manifest"])} against their package manifests)')
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for n, t in outs.items():
        (OUT / n).write_text(t, encoding='utf-8')
    (SUPP / 'SUPPLEMENT-MANIFEST.json').write_text(manifest, encoding='utf-8')
    print(f'wrote {len(outs)} tables and SUPPLEMENT-MANIFEST.json ({len(INPUTS)} inputs)')


if __name__ == '__main__':
    main()
