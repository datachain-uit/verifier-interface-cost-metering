#!/usr/bin/env python3
"""Level 1: integrity of this artifact.

Checks, in order:
  1. every object in provenance/OBJECT-CLASS.tsv against its class:
       GIT          the file must be present with the recorded SHA-256                    -> PRESENT HASH-MATCH
       GIT-LFS      the object itself is present with the recorded SHA-256                -> PRESENT HASH-MATCH
                    absent (not fetched)                                                  -> GIT-LFS-PENDING
                    a valid Git LFS pointer whose oid is the recorded SHA-256 and whose
                    size is the recorded size (when the size is recorded)                -> GIT-LFS-PENDING
       REGENERABLE  absent (regenerate with scripts/regenerate-keys.sh)                   -> REGENERABLE
                    present (after regeneration) with the recorded SHA-256                -> PRESENT HASH-MATCH
       WITHHELD     must be absent                                                        -> WITHHELD
       EXTERNAL-PIN must be absent (obtained from its upstream source)                    -> EXTERNAL-PIN
     anything else is an ERROR: a missing GIT file, a wrong hash, a withheld or external file present, an invalid Git LFS
     pointer, a pointer whose oid or size differs from the recorded object, or a Git LFS pointer at a path that is not
     classified GIT-LFS.
     A pointer only shows that the repository representation is valid; it is never reported as PRESENT HASH-MATCH. Only
     the object bytes themselves, hashing to the recorded SHA-256, are;
  2. every file in the tree must be an object of the table (an unexpected file is an ERROR);
  3. every entry of every frozen package manifest in provenance/PACKAGES.tsv must be either present with the hash the
     manifest records, or an object classified WITHHELD, REGENERABLE or GIT-LFS (absent or a validated pointer) with that
     same hash; each manifest file must itself have its recorded SHA-256. The frozen manifests are never modified; this
     check gives them their meaning;
  4. manifests/SHA256SUMS (every published file) must match; a GIT-LFS object that is absent or a validated pointer is
     checked against provenance/OBJECT-CLASS.tsv instead.

usage: python3 scripts/verify_artifact.py [--quiet] [--report FILE]      exit code 0 = no ERROR
"""
import argparse, csv, hashlib, io, json, os, re, sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
SELF_EXEMPT = {'manifests/SHA256SUMS'}          # cannot list its own hash
TABLE_EXEMPT = {'manifests/SHA256SUMS', 'provenance/OBJECT-CLASS.tsv'}   # the object table cannot list itself
IGNORED_DIRS = {'.git'}
LFS_VERSION = b'version https://git-lfs.github.com/spec/v1'
LFS_MAX_POINTER = 1024                           # Git LFS pointer files are smaller than 1024 bytes


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def looks_like_pointer(p):
    with open(p, 'rb') as f:
        return f.read(len(LFS_VERSION)) == LFS_VERSION


def parse_pointer(p):
    """Return (oid, size) of a syntactically valid Git LFS pointer file, or None."""
    if p.stat().st_size >= LFS_MAX_POINTER:
        return None
    try:
        text = p.read_bytes().decode('ascii')
    except UnicodeDecodeError:
        return None
    if not text.endswith('\n'):
        return None
    lines = text[:-1].split('\n')
    if lines[0] != LFS_VERSION.decode():
        return None
    keys, kv = [], {}
    for line in lines[1:]:
        k, sep, v = line.partition(' ')
        if not sep or not re.fullmatch(r'[a-z0-9.-]+', k) or k in kv or k == 'version':
            return None
        keys.append(k); kv[k] = v
    if keys != sorted(keys) or 'oid' not in kv or 'size' not in kv:
        return None
    m = re.fullmatch(r'sha256:([0-9a-f]{64})', kv['oid'])
    if not m or not re.fullmatch(r'0|[1-9][0-9]*', kv['size']):
        return None
    return m.group(1), int(kv['size'])


def tsv(rel):
    return list(csv.DictReader(io.StringIO((A / rel).read_text('utf-8')), delimiter='\t'))


def tree():
    out = set()
    for dp, dn, fn in os.walk(A):
        dn[:] = [d for d in dn if d not in IGNORED_DIRS]
        for f in fn:
            out.add(str((Path(dp) / f).relative_to(A)))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--quiet', action='store_true'); ap.add_argument('--report'); a = ap.parse_args()
    objects = tsv('provenance/OBJECT-CLASS.tsv')
    by_path = {o['path']: o for o in objects}
    if len(by_path) != len(objects):
        print('ERROR duplicate paths in provenance/OBJECT-CLASS.tsv'); return 2
    present = tree()
    outcome = {}; errors = []; hashes = {}; pointers = []
    for o in objects:
        p, cls, h = o['path'], o['class'], o['sha256']
        f = A / p
        exists = p in present
        if exists and cls == 'GIT-LFS' and looks_like_pointer(f):
            ptr = parse_pointer(f)
            if ptr is None:
                errors.append(f'GIT-LFS object {p}: invalid Git LFS pointer'); outcome[p] = 'ERROR'
            elif ptr[0] != h:
                errors.append(f'GIT-LFS object {p}: Git LFS pointer oid differs from the recorded SHA-256'); outcome[p] = 'ERROR'
            elif o['bytes'] and ptr[1] != int(o['bytes']):
                errors.append(f'GIT-LFS object {p}: Git LFS pointer size differs from the recorded size'); outcome[p] = 'ERROR'
            else:
                outcome[p] = 'GIT-LFS-PENDING'; pointers.append(p)
            continue
        if exists:
            hashes[p] = got = sha256(f)
        if cls == 'GIT':
            r = 'PRESENT HASH-MATCH' if exists and got == h else 'ERROR'
        elif cls in ('GIT-LFS', 'REGENERABLE'):
            r = ('PRESENT HASH-MATCH' if got == h else 'ERROR') if exists else ('GIT-LFS-PENDING' if cls == 'GIT-LFS' else 'REGENERABLE')
        elif cls in ('WITHHELD', 'EXTERNAL-PIN'):
            r = 'ERROR' if exists else cls
        else:
            r = 'ERROR'
        outcome[p] = r
        if r == 'ERROR':
            if not exists:
                why = 'missing'
            elif cls in ('WITHHELD', 'EXTERNAL-PIN'):
                why = 'must not be present'
            elif looks_like_pointer(f):
                why = 'Git LFS pointer at a path not classified GIT-LFS'
            else:
                why = 'hash mismatch'
            errors.append(f'{cls} object {p}: {why}')
    unexpected = sorted(present - set(by_path) - TABLE_EXEMPT)
    errors += [f'unexpected file (not in provenance/OBJECT-CLASS.tsv): {p}' for p in unexpected]

    # frozen package manifests
    pk_rows = tsv('provenance/PACKAGES.tsv'); pk_report = {}
    for r in pk_rows:
        base = r['path']; mrel = f"{base}/{r['manifest']}" if base != '.' else r['manifest']
        if mrel not in present or (hashes.get(mrel) or sha256(A / mrel)) != r['manifest_sha256']:
            errors.append(f"package {r['package']}: manifest {mrel} missing or not the frozen manifest"); continue
        n = {'present': 0, 'classified': 0, 'lfs_pointer': 0}
        for line in (A / mrel).read_text('utf-8').splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                continue
            h, name = parts[0], parts[1].lstrip('*')
            name = name[2:] if name.startswith('./') else name
            pub = r['entry_prefix'] + name if r['entry_prefix'] else f'{base}/{name}'
            pub = r['remap'].split('=>')[1] if r['remap'] and name == r['remap'].split('=>')[0] else pub
            o = by_path.get(pub)
            if o is not None and o['sha256'] == h and outcome.get(pub) == 'GIT-LFS-PENDING':
                n['classified'] += 1                                     # absent, or a validated pointer: not the object bytes
                n['lfs_pointer'] += pub in present
            elif pub in present and o is not None and o['class'] in ('GIT', 'GIT-LFS', 'REGENERABLE') and o['sha256'] == h:
                if outcome.get(pub) == 'PRESENT HASH-MATCH':
                    n['present'] += 1
                else:
                    errors.append(f"package {r['package']}: {pub} not hash-matching")
            elif o is not None and o['sha256'] == h and outcome.get(pub) in ('WITHHELD', 'REGENERABLE'):
                n['classified'] += 1
            else:
                errors.append(f"package {r['package']}: entry {name} ({pub}) neither present with the frozen hash nor classified")
        pk_report[r['package']] = n

    # artifact-level manifest
    man = {}
    for line in (A / 'manifests/SHA256SUMS').read_text('utf-8').splitlines():
        h, name = line.split(None, 1); man[name.strip()] = h
    for name, h in man.items():
        if outcome.get(name) == 'GIT-LFS-PENDING':
            continue                                                     # absent or a validated pointer: see OBJECT-CLASS
        if name not in present:
            if outcome.get(name) == 'REGENERABLE':
                continue
            errors.append(f'manifests/SHA256SUMS: {name} missing')
        elif (hashes.get(name) or sha256(A / name)) != h:
            errors.append(f'manifests/SHA256SUMS: {name} hash mismatch')
    for p in sorted(present - set(man) - SELF_EXEMPT):
        o = by_path.get(p)
        ok = o is not None and ((o['class'] in ('REGENERABLE', 'GIT-LFS') and outcome.get(p) == 'PRESENT HASH-MATCH')
                                or (o['class'] == 'GIT-LFS' and outcome.get(p) == 'GIT-LFS-PENDING'))
        if not ok:
            errors.append(f'manifests/SHA256SUMS: {p} not listed')

    counts = {}
    for o in objects:
        k = f"{o['class']} -> {outcome[o['path']]}"
        counts[k] = counts.get(k, 0) + 1
    if not a.quiet:
        for k in sorted(counts):
            print(f'{counts[k]:6d}  {k}')
        if pointers:
            print(f'{len(pointers):6d}  of them Git LFS pointers (oid and recorded size match; object bytes not present)')
        print(f'{len(pk_report):6d}  frozen package manifests checked '
              f'({sum(v["present"] for v in pk_report.values())} entries present, {sum(v["classified"] for v in pk_report.values())} classified absent'
              + (f', of which {sum(v["lfs_pointer"] for v in pk_report.values())} as Git LFS pointers' if any(v["lfs_pointer"] for v in pk_report.values()) else '') + ')')
        print(f'{len(man):6d}  entries in manifests/SHA256SUMS')
    for e in errors[:200]:
        print('ERROR', e)
    if a.report:
        Path(a.report).write_text(json.dumps({'counts': counts, 'lfs_pointers': pointers, 'packages': pk_report, 'errors': errors}, indent=1) + '\n')
    print('LEVEL 1: PASS' if not errors else f'LEVEL 1: FAIL ({len(errors)} errors)')
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
