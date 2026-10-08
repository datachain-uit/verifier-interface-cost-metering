#!/usr/bin/env python3
"""Assign every published file of this artifact to exactly one licence, following LICENSE.md, and audit the result.

Rules, in order (the first match decides; rule 1 wins over every path rule):
  0  LICENSES/*                                      licence texts, under their own terms
  1  file carries an SPDX-License-Identifier tag    the tagged licence (embedded notice)
  2  compiled verifier JSON                          GPL-3.0-or-later
  3  circom-emitted witness generators              GPL-3.0
  4  R1CS files, proving keys, verification keys     GPL-3.0
  5  ZKsync OS constant-file copies                  MIT OR Apache-2.0
  6  author code                                     MIT
  7  everything else                                 CC-BY-4.0
Audit: every published file classified exactly once; path rules 2-6 are disjoint (a file matching two of them is a
conflict); a file with several different SPDX identifiers is a conflict; a file whose embedded notice differs from the
path rule that would otherwise apply is reported (rule 1 decides) and counted as a conflict only when the notice is
unreadable or ambiguous.

usage: python3 scripts/classify_licences.py [--write | --check]   (default: print the audit; --write updates
       provenance/LICENSE-MAP.tsv; --check requires the table to be current and the audit to be clean)
"""
import csv, fnmatch, io, os, re, sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
TABLE = 'provenance/LICENSE-MAP.tsv'
SPDX = re.compile(rb'SPDX-License-Identifier:\s*([A-Za-z0-9.+-]+(?:\s+(?:OR|AND|WITH)\s+[A-Za-z0-9.+-]+)*)')
GENERATED_LATER = {'manifests/SHA256SUMS', 'provenance/OBJECT-CLASS.tsv', TABLE}


def m(path, *patterns):
    return any(fnmatch.fnmatchcase(path, p) for p in patterns)


PATH_RULES = [
    (2, 'GPL-3.0-or-later', lambda p: m(p, 'data/c1/*/evidence/compiled*/*.json', 'setup/fflonk/compiled-verifiers/compiled-fflonk/*.json')),
    (3, 'GPL-3.0', lambda p: '_js/' in p or p.endswith('.wasm')),
    (4, 'GPL-3.0', lambda p: p.endswith(('.r1cs', '.zkey')) or (p.endswith('.json') and 'vkey' in os.path.basename(p).lower())),
    (5, 'MIT OR Apache-2.0', lambda p: m(p, 'protocols/c1-preregistration/toolchain/zksync-os-v0.4.0-*.rs', 'data/p0-feasibility/toolchain/zksync-os-v0.3.2-*.rs')),
    (6, 'MIT', lambda p: '_js/' not in p and (p.endswith(('.py', '.js', '.cjs', '.mjs', '.sh', '.circom', '.sol'))
                                            or os.path.basename(p) in ('Dockerfile', '.dockerignore', 'compose.yaml', 'package.json', 'package-lock.json'))),
]


def files():
    out = set()
    for dp, dn, fn in os.walk(A):
        dn[:] = [d for d in dn if d != '.git']
        for f in fn:
            out.add(str((Path(dp) / f).relative_to(A)))
    return sorted(out | GENERATED_LATER)


def classify(p):
    """Return (licence, rule, note, conflicts)."""
    if p.startswith('LICENSES/'):
        return 'licence text', 0, '', []
    conflicts = []
    matches = [(r, lic) for r, lic, f in PATH_RULES if f(p)]
    if len({lic for _, lic in matches}) > 1:
        conflicts.append('path rules ' + ', '.join(f'{r}={lic}' for r, lic in matches))
    tags = set()
    f = A / p
    if f.is_file():
        tags = {t.decode() for t in SPDX.findall(f.read_bytes())}
    if len(tags) > 1:
        conflicts.append('several SPDX identifiers: ' + ', '.join(sorted(tags)))
    if tags:
        tag = sorted(tags)[0]
        path_lic = matches[0][1] if matches else 'CC-BY-4.0'
        note = '' if tag == path_lic else f'embedded notice decides (path rule would give {path_lic})'
        return tag, 1, note, conflicts
    if matches:
        return matches[0][1], matches[0][0], '', conflicts
    return 'CC-BY-4.0', 7, '', conflicts


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    rows = []; conflicts = []
    for p in files():
        lic, rule, note, c = classify(p)
        rows.append([p, lic, str(rule), note])
        conflicts += [f'{p}: {x}' for x in c]
    counts = {}
    for _, lic, rule, _ in rows:
        counts[(lic, rule)] = counts.get((lic, rule), 0) + 1
    out = io.StringIO(); w = csv.writer(out, delimiter='\t', lineterminator='\n')
    w.writerow(['path', 'licence', 'rule', 'note']); w.writerows(rows)
    text = out.getvalue()
    for (lic, rule), n in sorted(counts.items(), key=lambda x: int(x[0][1])):
        print(f'{n:6d}  rule {rule}  {lic}')
    print(f'{len(rows):6d}  files classified exactly once; {len(conflicts)} conflicts')
    for c in conflicts:
        print('CONFLICT', c)
    if mode == '--write':
        (A / TABLE).write_text(text, encoding='utf-8'); print('written', TABLE)
    elif mode == '--check':
        current = (A / TABLE).read_text(encoding='utf-8') if (A / TABLE).is_file() else ''
        if current != text:
            print('LICENCE CHECK FAIL: provenance/LICENSE-MAP.tsv is not current'); return 1
        print('LICENCE CHECK PASS' if not conflicts else 'LICENCE CHECK FAIL')
    return 1 if conflicts else 0


if __name__ == '__main__':
    sys.exit(main())
