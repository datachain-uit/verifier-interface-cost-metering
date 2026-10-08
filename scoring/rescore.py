#!/usr/bin/env python3
"""Level-2 re-scoring and re-analysis runners.

Each family runs one frozen scorer or analysis script, unchanged, on the frozen evidence of this artifact and compares
its outputs with the frozen outputs byte for byte. Nothing inside the artifact is written: outputs go to a work
directory outside the artifact, and Python byte-code writing is disabled.

usage:
  python3 scoring/rescore.py --list
  python3 scoring/rescore.py [--work DIR] [--report FILE] FAMILY [FAMILY ...]
  python3 scoring/rescore.py [--work DIR] [--report FILE] --all
  python3 scoring/rescore.py --inputs-only (FAMILY ... | --all)    # check that every input and frozen output exists

Frozen scripts expect the directory layout of the environment they originally ran in: a home-directory layout for the
C1 model and the pinned ZKsync OS constant files, and a workspace-root layout for the D3 re-analysis. build_shim()
recreates those layouts in the work directory from files of this artifact (copies, never links into the artifact).

Families marked 'recorded' use the invocation recorded next to the frozen outputs; families marked 'usage' use the
argument order documented in the script's own usage line. Files listed under 'informational' contain run metadata
(timestamps, absolute paths) and are reported but never decide the outcome.

Comparison rule: every compared output must be byte-identical, with one exception. For c1-predictions, the frozen
predictor emits the same complete row multiset in p0_model_check.csv, but filesystem-dependent unsorted glob ordering can
permute row order; this specific output is therefore compared as an order-insensitive multiset (header exact; every
complete data row with its multiplicity) and reported as IDENTICAL-AS-ROW-MULTISET, while all other outputs retain
byte-identity checks. Neither the frozen predictor nor its frozen output is changed.
"""
import argparse, collections, filecmp, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

A = Path(__file__).resolve().parents[1]
PILOT = 'data/c1/pilot/evidence/V2-MPI-PILOT-01-records.jsonl'
FULL = 'data/c1/full/evidence/full/V2-MPI-FULL-01-records.jsonl'
BRIDGE = 'data/c1/full/evidence/bridge/V2-MPI-FULL-01-BRIDGE-records.jsonl'
FFL = 'data/c1/fflonk/evidence/fflonk/V2-MPI-FULL-01-FFLONK-records.jsonl'
C1SC = ['AC_checks.csv', 'CELL_summary.csv', 'NPG_ranking.csv', 'NPG_scoring.csv', 'P_scoring.csv', 'R_scoring.csv', 'SEM_scoring.csv',
        'SG_monotonicity.csv', 'SG_signs.csv', 'XO_crossovers.csv', 'ZC_scoring.csv', 'summary.json']

# argv placeholders: {A} artifact root, {OUT} output directory, {H} shim home, {R} shim workspace root
FAMILIES = {
    'c1-full': dict(
        what='C1 registered scoring of the pilot and full campaigns (frozen scorer)', basis='recorded',
        cwd='protocols/c1-preregistration', home=True,
        argv=['scoring/score_c1.py', '09-numeric-predictions', '{OUT}', '{A}/' + PILOT, '{A}/' + FULL],
        stdout='scoring-stdout.json', stderr='scoring-stderr.txt',
        compare={f: 'data/c1/full/record/scoring/' + f for f in C1SC + ['scoring-stdout.json', 'scoring-stderr.txt']}),
    'c1-fflonk': dict(
        what='C1 registered scoring including the FFLONK cells (frozen scorer)', basis='recorded',
        cwd='protocols/c1-preregistration', home=True,
        argv=['scoring/score_c1.py', '09-numeric-predictions', '{OUT}', '{A}/' + PILOT, '{A}/' + FULL, '{A}/' + FFL],
        stdout='scoring-stdout.json', stderr='scoring-stderr.txt',
        compare={f: 'data/c1/fflonk/record/scoring-c1/' + f for f in C1SC + ['scoring-stdout.json', 'scoring-stderr.txt']}),
    'c2-score': dict(
        what='separate prospective test C2: frozen scorer', basis='recorded',
        cwd='protocols/c2-forward-test/stage1', home=True, env={'C2_ZKOS_SRC': '{H}/p0/zkos/vm-0.4.0'},
        argv=['-B', 'code/c2_score.py', '{A}/protocols/c2-forward-test/stage2', '{A}/protocols/c2-forward-test/stage2/fflonk-structural.jsonl',
              '{A}/' + PILOT, '{A}/' + FULL, '{A}/' + FFL, '--out', '{OUT}'],
        stdout='scoring-stdout.json', stderr='scoring-stderr.txt',
        compare={f: 'data/c1/fflonk/record/scoring-c2/' + f for f in ('C2-SCORES.json', 'scoring-stdout.json', 'scoring-stderr.txt')}),
    'c2-calibration': dict(
        what='C2 stage 1: calibration of the two environment constants', basis='usage',
        cwd='protocols/c2-forward-test/stage1', home=True, env={'C2_ZKOS_SRC': '{H}/p0/zkos/vm-0.4.0'},
        argv=['-B', 'code/c2_calibrate.py', 'calibration/calibration-structural.jsonl', '{A}/' + PILOT, '{A}/' + FULL,
              '{A}/data/posthoc/native-cost-audit/out/M7A-per-proof.csv', '{A}/data/posthoc/heap-retrace/out/M7B-A-per-proof.csv',
              '{A}/protocols/c1-preregistration/model', '{OUT}/C2-CALIBRATION.json'],
        compare={'C2-CALIBRATION.json': 'protocols/c2-forward-test/stage1/calibration/C2-CALIBRATION.json'}),
    'c2-internal-check': dict(
        what='C2 stage 1: internal consistency check', basis='usage',
        cwd='protocols/c2-forward-test/stage1', home=True, env={'C2_ZKOS_SRC': '{H}/p0/zkos/vm-0.4.0'},
        argv=['-B', 'code/c2_internal_check.py', 'calibration/check-structural.jsonl', '{A}/' + PILOT, '{A}/' + FULL,
              'calibration/C2-CALIBRATION.json', '{OUT}/C2-INTERNAL-CHECK.json'],
        compare={'C2-INTERNAL-CHECK.json': 'protocols/c2-forward-test/stage1/calibration/C2-INTERNAL-CHECK.json'}),
    'c2-predict': dict(
        what='C2 stage 2: frozen predictions from the structural derivation', basis='usage',
        cwd='protocols/c2-forward-test/stage1', home=True, env={'C2_ZKOS_SRC': '{H}/p0/zkos/vm-0.4.0'},
        argv=['-B', 'code/c2_predict.py', '{A}/protocols/c2-forward-test/stage2/fflonk-structural.jsonl', 'calibration/C2-CALIBRATION.json',
              '{A}/' + PILOT, '{A}/' + FULL, '{OUT}'],
        compare={f: 'protocols/c2-forward-test/stage2/' + f for f in ('C2-STAGE2-PREDICTIONS.csv', 'C2-STAGE2-PREDICTIONS.json')}),
    'c1-predictions': dict(
        what='C1 a-priori predictions from the P0 feasibility data (frozen prediction generator)', basis='usage',
        cwd='protocols/c1-preregistration', home=True,
        argv=['model/c1_predict.py', '{OUT}'],
        rows_as_multiset={'p0_model_check.csv'},   # only this output: row order follows the filesystem's listing order
        compare={f: 'protocols/c1-preregistration/09-numeric-predictions/' + f for f in (
            'crossover_intervals.csv', 'equality_bands.csv', 'fitted_parameters_and_tolerances.json', 'p0_model_check.csv', 'predictions_cells.csv',
            'predictions_signs.csv', 'zkos_npg_levels.csv', 'zkos_npg_predictions.csv', 'zkos_switch_intervals.csv')}),
    'c1-residual': dict(
        what='post hoc: ZKsync OS residual versus k (full campaign)', basis='usage',
        cwd='data/c1/full/record', home=True,
        argv=['tools/zkos_residual_vs_k.py', 'scoring', '{A}/' + PILOT, '{A}/' + FULL, '--', '{OUT}'],
        compare={f: 'data/c1/full/record/post-registered/' + f for f in ('ZKOS-residual-vs-k.csv', 'ZKOS-residual-vs-k.json')}),
    'c1-npg-per-proof': dict(
        what='post hoc: native-per-gas per proof (full campaign)', basis='usage',
        cwd='data/c1/full/record', home=True,
        argv=['tools/npg_per_proof.py', '{OUT}/npg-per-proof.csv', '{A}/' + PILOT, '{A}/' + FULL],
        compare={'npg-per-proof.csv': 'data/c1/full/record/post-registered/npg-per-proof.csv'}),
    'c1-bridge': dict(
        what='reproduction control: bridge cells against the pilot', basis='usage',
        cwd='data/c1/full/record', home=True,
        argv=['tools/bridge_check.py', '{A}/' + PILOT, '{A}/' + BRIDGE, '{OUT}'],
        compare='dir:data/c1/full/record/bridge-check'),
    'posthoc-audit': dict(
        what='post hoc source-level audit of the F4 residual', basis='usage',
        cwd='data/posthoc/native-cost-audit', home=True,
        argv=['m7a_f4_audit.py', '{A}/' + PILOT, '{A}/' + FULL, '{A}/data/c1/full/evidence/compiled', '{A}/data/c1/pilot/evidence/compiled',
              '{A}/data/c1/full/record/scoring/summary.json', '{OUT}'],
        compare={f: 'data/posthoc/native-cost-audit/out/' + f for f in ('M7A-per-proof.csv', 'M7A-cells.csv', 'M7A-summary.json')}),
    'posthoc-retrace-count': dict(
        what='post hoc deterministic re-trace: heap-event counting from the frozen traces', basis='usage',
        cwd='data/posthoc/heap-retrace', home=True,
        argv=['scripts/m7b_a_count.py', 'retrace-summary.json', 'retrace-mem-summary.json', 'raw', '{A}/' + PILOT, '{A}/' + FULL,
              '{A}/data/posthoc/native-cost-audit/out/M7A-per-proof.csv', '{OUT}'],
        compare={f: 'data/posthoc/heap-retrace/out/' + f for f in ('M7B-A-events.csv', 'M7B-A-per-k.csv', 'M7B-A-per-proof.csv', 'M7B-A-summary.json')}),
    'd1': dict(
        what='D1 prover analysis (Host A)', basis='usage',
        cwd='.', argv=['protocols/prover-d1/kit/d1_analysis.py', 'data/prover/d1/evidence', '{OUT}'], stdout='run-stdout.txt',
        compare={f: 'data/prover/d1/analysis/' + f for f in ('D1-cells.csv', 'D1-ratios.csv', 'D1-summary.json', 'run-stdout.txt')}),
    'd2': dict(
        what='D2 prover analysis (Host B, timed campaign)', basis='recorded',
        cwd='.', argv=['protocols/prover-d2/final/d2_analysis.py', '--campaign', 'data/prover/d2/timed/repo/results/V2-PRV-D2-01',
                       '--manifest', 'data/prover/d2/timed/SHA256SUMS', '--out', '{OUT}', '--mode', 'run'], stdout='console.txt',
        compare={f: 'data/prover/d2/analysis/run/' + f for f in ('D2-cell-stats.csv', 'D2-allocation-speedups.csv', 'D2-backend-ratios.csv',
                                                                 'D2-zkey-diagnostic.csv', 'D2-reconciliation.json')},
        informational={'D2-RUN-RECORD.json': 'data/prover/d2/analysis/run/D2-RUN-RECORD.json', 'console.txt': 'data/prover/d2/analysis/run/console.txt'}),
    'd3': dict(
        what='D3 descriptive re-analysis of the Host A prover data', basis='recorded',
        cwd='.', shim_root=True, argv=['protocols/prover-d3/d3_reanalysis.py', '--root', '{R}', '--out', '{OUT}', '--mode', 'run'],
        compare={f: 'data/prover/d3/reanalysis/out/' + f for f in ('D3-cell-stats.csv', 'D3-allocation-speedups.csv', 'D3-backend-ratios.csv',
                                                                   'D3-zkey-diagnostic.csv', 'D3-reconciliation.json', 'D3-input-verification.json')},
        informational={'D3-RUN-RECORD.json': 'data/prover/d3/reanalysis/out/D3-RUN-RECORD.json'}),
    'd2-side-by-side': dict(
        what='D2 / D3 side-by-side tables', basis='usage',
        cwd='.', argv=['data/prover/d2/analysis/side-by-side/d2_side_by_side.py', 'data/prover/d3/reanalysis/out', 'data/prover/d2/analysis/run', '{OUT}'],
        compare={f: 'data/prover/d2/analysis/side-by-side/' + f for f in ('side-by-side-allocation-speedups.csv', 'side-by-side-backend-ratios.csv',
                                                                          'side-by-side-cell-stats.csv', 'side-by-side-zkey-diagnostic.csv')}),
}

ZKOS = {  # pinned ZKsync OS VM constant files (copies shipped in the C1 and P0 toolchain records)
    'p0/zkos/vm-0.4.0/basic_system/src/cost_constants.rs': 'protocols/c1-preregistration/toolchain/zksync-os-v0.4.0-cost_constants.rs',
    'p0/zkos/vm-0.4.0/evm_interpreter/src/native_resource_constants.rs': 'protocols/c1-preregistration/toolchain/zksync-os-v0.4.0-native_resource_constants.rs',
    'p0/zkos/vm-0.4.0/zk_ee/src/system/constants.rs': 'protocols/c1-preregistration/toolchain/zksync-os-v0.4.0-zk_ee_constants.rs',
    'p0/zkos/vm-0.3.2/basic_system/src/cost_constants.rs': 'data/p0-feasibility/toolchain/zksync-os-v0.3.2-cost_constants.rs',
    'p0/zkos/vm-0.3.2/evm_interpreter/src/native_resource_constants.rs': 'data/p0-feasibility/toolchain/zksync-os-v0.3.2-native_resource_constants.rs',
}
D3_LAYOUT = {  # D3 workspace-root layout expected by the frozen D3 script -> published location
    'research/results/postcorr-20260925': 'data/prover/d3/source',
    'research/submission/csi/generated/prover_per_round.csv': 'data/prover/d3/source/reconciliation/prover_per_round.csv',
}


def build_shim(work):
    """Home-directory and workspace-root layouts expected by the frozen scripts, built from files of this artifact."""
    H = work / 'home'; R = work / 'root'
    if not H.exists():
        for dst, src in ZKOS.items():
            (H / dst).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(A / src, H / dst)
        for d in ('c1/model', 'c1/pkg/model'):
            shutil.copytree(A / 'protocols/c1-preregistration/model', H / d, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(A / 'protocols/c1-preregistration/corpus', H / 'c1/corpus', ignore=shutil.ignore_patterns('proofs', 'inputs'))
        shutil.copytree(A / 'data/p0-feasibility/results/raw', H / 'p0/out')
        # ZKsync OS v32.0 version-selection smoke runs: each run is written under the file name it records
        vs = json.loads((A / 'protocols/c1-preregistration/version-selection/zkos-v32.0-smoke-runs.json').read_text())
        for run in vs['runs']:
            (H / 'p0/out' / run['file']).write_text(json.dumps(run))
    if not R.exists():
        for dst, src in D3_LAYOUT.items():
            (R / dst).parent.mkdir(parents=True, exist_ok=True)
            (shutil.copytree if (A / src).is_dir() else shutil.copy2)(A / src, R / dst)
    return H, R


def fill(s, out, H, R):
    return s.replace('{A}', str(A)).replace('{OUT}', str(out)).replace('{H}', str(H)).replace('{R}', str(R))


def frozen_pairs(fam, out):
    c = fam['compare']
    if isinstance(c, str):
        d = A / c.split(':', 1)[1]
        return {p.name: str(p.relative_to(A)) for p in sorted(d.iterdir()) if p.is_file()}
    return c


def same_row_multiset(a, b):
    """Header identical and the data rows identical as a multiset of complete rows (duplicates counted)."""
    ra, rb = Path(a).read_bytes().split(b'\n'), Path(b).read_bytes().split(b'\n')
    return ra[0] == rb[0] and collections.Counter(ra[1:]) == collections.Counter(rb[1:])


def run(name, work, inputs_only=False):
    fam = FAMILIES[name]; out = work / 'out' / name
    H, R = (work / 'home', work / 'root') if inputs_only else build_shim(work)
    res = {'family': name, 'what': fam['what'], 'basis': fam['basis'], 'compared': {}, 'informational': {}}
    missing = [x for x in [fill(a, out, H, R) for a in fam['argv']] if x.startswith(str(A)) and not Path(x).exists() and '{OUT}' not in x]
    missing += [rel for rel in frozen_pairs(fam, out).values() if not (A / rel).exists()]
    if missing:
        res['status'] = 'ERROR'; res['missing'] = missing; return res
    if inputs_only:
        res['status'] = 'INPUTS-PRESENT'; return res
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0')
    if fam.get('home'):
        env['HOME'] = str(H)
    for k, v in fam.get('env', {}).items():
        env[k] = fill(v, out, H, R)
    cmd = [sys.executable] + [fill(a, out, H, R) for a in fam['argv']]
    p = subprocess.run(cmd, cwd=A / fam['cwd'], env=env, capture_output=True)
    if fam.get('stdout'):
        (out / fam['stdout']).write_bytes(p.stdout)
    if fam.get('stderr'):
        (out / fam['stderr']).write_bytes(p.stderr)
    res['exit_code'] = p.returncode
    if p.returncode != 0:
        res['status'] = 'ERROR'; res['stderr_tail'] = p.stderr.decode(errors='replace')[-2000:]; return res
    for o, f in frozen_pairs(fam, out).items():
        if (out / o).is_file() and filecmp.cmp(out / o, A / f, shallow=False):
            res['compared'][o] = 'IDENTICAL'
        elif o in fam.get('rows_as_multiset', ()) and (out / o).is_file() and same_row_multiset(out / o, A / f):
            res['compared'][o] = 'IDENTICAL-AS-ROW-MULTISET'
        else:
            res['compared'][o] = 'DIFFERENT'
    for o, f in fam.get('informational', {}).items():
        res['informational'][o] = 'IDENTICAL' if (out / o).is_file() and filecmp.cmp(out / o, A / f, shallow=False) else 'DIFFERENT (run metadata)'
    n = sum(v == 'IDENTICAL' for v in res['compared'].values())
    m = sum(v == 'IDENTICAL-AS-ROW-MULTISET' for v in res['compared'].values())
    res['byte_identical'], res['identical_as_row_multiset'] = n, m
    res['status'] = 'PASS' if n + m == len(res['compared']) else 'DIFF'
    res['summary'] = f'{n} / {len(res["compared"])} outputs byte-identical' + (f', {m} identical as a row multiset' if m else '')
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('families', nargs='*'); ap.add_argument('--all', action='store_true'); ap.add_argument('--list', action='store_true')
    ap.add_argument('--inputs-only', action='store_true'); ap.add_argument('--work'); ap.add_argument('--report')
    a = ap.parse_args()
    if a.list:
        for k, v in FAMILIES.items():
            print(f'{k:24s} [{v["basis"]}] {v["what"]}')
        return 0
    names = list(FAMILIES) if a.all else a.families
    unknown = [n for n in names if n not in FAMILIES]
    if unknown or not names:
        ap.error(f'unknown or no families: {unknown}')
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix='rescore-'))
    if A in work.resolve().parents or work.resolve() == A:
        ap.error('the work directory must be outside the artifact')
    work.mkdir(parents=True, exist_ok=True)
    results = [run(n, work, a.inputs_only) for n in names]
    for r in results:
        print(f"{r['status']:15s} {r['family']:24s} {r.get('summary', '')}{' missing: ' + str(r['missing']) if 'missing' in r else ''}")
        for o, s in r['compared'].items():
            if s != 'IDENTICAL':
                print(f'    {s}: {o}')                       # IDENTICAL-AS-ROW-MULTISET is shown, and counts as identical
        if r['status'] == 'ERROR' and 'stderr_tail' in r:
            print('    ' + r['stderr_tail'].strip().replace('\n', '\n    ')[-800:])
    if a.report:
        Path(a.report).write_text(json.dumps(results, indent=1) + '\n')
    tot = sum(len(r['compared']) for r in results)
    if tot:
        print(f"outputs: {sum(r.get('byte_identical', 0) for r in results)} / {tot} byte-identical, "
              f"{sum(r.get('identical_as_row_multiset', 0) for r in results)} identical as a row multiset")
    print(f'work directory: {work}')
    return 0 if all(r['status'] in ('PASS', 'INPUTS-PRESENT') for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
