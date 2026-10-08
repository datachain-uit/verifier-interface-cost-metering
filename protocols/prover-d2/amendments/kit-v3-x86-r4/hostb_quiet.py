#!/usr/bin/env python3
"""V2-PRV-D2-01 (kit v3-x86) Host-B host-condition checks: the Linux replacement of the v3 P9 checks (macOS
pmset / caffeinate). Read-only: it reads /proc and /sys and counts running containers; it never changes any setting.

  hostb_quiet.py snap <out.json>                       one snapshot (per-CPU /proc/stat, load, containers, state, telemetry)
  hostb_quiet.py check <a.json> <b.json> --mode pre|during --alloc 1-8 [--frozen "<k=v ...>"]
                                                       compare two snapshots; prints one JSON line; exit 0 = accepted, 1 = violated
  hostb_quiet.py selftest                              negative/positive self-tests of the check logic (no host access)

Acceptance (frozen in D2-PREREGISTRATION.md §5; changeable only by a recorded amendment before the first timed round):
  pre    (2 s window right before a container): 0 running containers; load1 recorded (AMD-D2-1; not an acceptance condition); every allocated CPU and every SMT
         sibling of an allocated CPU busy <= PRE_CPU_MAX; all other logical CPUs together <= PRE_OTHER_MAX CPU-equivalents;
         frozen frequency / NUMA / THP state unchanged; sleep inhibitor held.
  during (container start -> end): 0 running containers before and after; every SMT sibling busy <= DURING_SIB_MAX;
         all non-allocated, non-sibling CPUs together <= DURING_OTHER_MAX CPU-equivalents; frozen state unchanged.
"""
import glob, json, os, subprocess, sys, time

LOAD1_MAX = float('inf') # AMD-D2-1: load1 recorded, not an acceptance condition
PRE_CPU_MAX = 0.10
PRE_OTHER_MAX = 1.0
DURING_SIB_MAX = 0.05
DURING_OTHER_MAX = 1.5
FROZEN_DEFAULT = 'intel_pstate=active governor=powersave no_turbo=0 numa_balancing=1 thp=madvise'


def rd(p):
    try:
        with open(p) as f:
            return f.read().strip()
    except OSError:
        return None


def cpus(spec):
    out = []
    for part in spec.split(','):
        if '-' in part:
            a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def siblings(alloc, topo=None):
    sib = set()
    for c in alloc:
        t = (topo or {}).get(c) if topo is not None else rd(f'/sys/devices/system/cpu/cpu{c}/topology/thread_siblings_list')
        if t:
            sib |= set(cpus(t))
    return sorted(sib - set(alloc))


def bracket(text):
    if not text:
        return None
    for w in text.split():
        if w.startswith('[') and w.endswith(']'):
            return w[1:-1]
    return text


def snap():
    stat = {}
    for line in (rd('/proc/stat') or '').splitlines():
        if line.startswith('cpu') and line[3:4].isdigit():
            f = line.split(); v = list(map(int, f[1:9]))
            stat[int(f[0][3:])] = {'total': sum(v), 'idle': v[3] + v[4]}
    try:
        r = subprocess.run(['docker', 'ps', '-q'], capture_output=True, text=True, timeout=30)
        nc = len(r.stdout.split()) if r.returncode == 0 else -1  # -1: docker not reachable -> violation
    except Exception:
        nc = -1
    gov = {rd(p) for p in glob.glob('/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor')}
    temp = None
    for h in glob.glob('/sys/class/hwmon/hwmon*'):
        if rd(f'{h}/name') == 'coretemp':
            for lab in glob.glob(f'{h}/temp*_label'):
                if rd(lab) == 'Package id 0':
                    v = rd(lab.replace('_label', '_input')); temp = int(v) / 1000 if v else None
    try:
        inh = subprocess.run(['systemd-inhibit', '--list', '--no-pager', '--no-legend'], capture_output=True, text=True, timeout=10).stdout
        inhibit = 1 if 'zcorp-d2' in inh else 0
    except Exception:
        inhibit = -1
    topo = {c: rd(f'/sys/devices/system/cpu/cpu{c}/topology/thread_siblings_list') for c in stat}
    return {
        'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'mono': time.monotonic(),
        'stat': stat, 'topology': topo, 'loadavg': rd('/proc/loadavg'), 'running_containers': nc,
        'state': {'intel_pstate': rd('/sys/devices/system/cpu/intel_pstate/status'),
                  'governor': ','.join(sorted(g for g in gov if g)) or None,
                  'no_turbo': rd('/sys/devices/system/cpu/intel_pstate/no_turbo'),
                  'numa_balancing': rd('/proc/sys/kernel/numa_balancing'),
                  'thp': bracket(rd('/sys/kernel/mm/transparent_hugepage/enabled'))},
        'mhz': {c: (int(rd(f'/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq') or 0) // 1000) for c in range(1, 9)},
        'core_throttle': {c: rd(f'/sys/devices/system/cpu/cpu{c}/thermal_throttle/core_throttle_count') for c in range(1, 9)},
        'pkg_throttle': rd('/sys/devices/system/cpu/cpu1/thermal_throttle/package_throttle_count'),
        'pkg_temp_c': temp, 'inhibit': inhibit,
    }


def busy(a, b, c):
    dt = b['stat'][c]['total'] - a['stat'][c]['total']; di = b['stat'][c]['idle'] - a['stat'][c]['idle']
    return 0.0 if dt <= 0 else max(0.0, 1.0 - di / dt)


def check(a, b, mode, alloc, frozen):
    allc = sorted(set(a['stat']) & set(b['stat']))
    topo = {int(k): v for k, v in (b.get('topology') or {}).items()}
    sib = siblings(alloc, topo)
    other = [c for c in allc if c not in alloc and c not in sib]
    v = []
    st = b['state']; want = dict(x.split('=', 1) for x in frozen.split())
    for k, w in want.items():
        if str(st.get(k)) != w:
            v.append(f'state {k}={st.get(k)} (frozen {w})')
    if a['running_containers'] != 0 or b['running_containers'] != 0:
        v.append(f"running containers {a['running_containers']} / {b['running_containers']}")
    if b.get('inhibit') != 1:
        v.append(f"sleep inhibitor not held ({b.get('inhibit')})")
    bal = max([busy(a, b, c) for c in alloc] or [0.0]); bsib = max([busy(a, b, c) for c in sib] or [0.0])
    bother = sum(busy(a, b, c) for c in other)
    load1 = float((b.get('loadavg') or '0').split()[0])
    if mode == 'pre':
        if load1 > LOAD1_MAX: v.append(f'load1 {load1} > {LOAD1_MAX}')
        if bal > PRE_CPU_MAX: v.append(f'allocated CPU busy {bal:.3f} > {PRE_CPU_MAX}')
        if bsib > PRE_CPU_MAX: v.append(f'SMT sibling busy {bsib:.3f} > {PRE_CPU_MAX}')
        if bother > PRE_OTHER_MAX: v.append(f'other CPUs {bother:.2f} CPU-equiv > {PRE_OTHER_MAX}')
    else:
        if bsib > DURING_SIB_MAX: v.append(f'SMT sibling busy {bsib:.3f} > {DURING_SIB_MAX}')
        if bother > DURING_OTHER_MAX: v.append(f'other CPUs {bother:.2f} CPU-equiv > {DURING_OTHER_MAX}')
    return {'mode': mode, 'accepted': not v, 'violations': v, 'utc_a': a['utc'], 'utc_b': b['utc'],
            'seconds': round(b['mono'] - a['mono'], 3), 'loadavg': b.get('loadavg'), 'running_containers': b['running_containers'],
            'busy_alloc_max': round(bal, 4), 'busy_siblings_max': round(bsib, 4), 'busy_other_cpu_equiv': round(bother, 3),
            'siblings': ','.join(map(str, sib)), 'mhz_alloc': ' '.join(str(b['mhz'].get(str(c), b['mhz'].get(c))) for c in range(1, 9)),
            'pkg_temp_c': b.get('pkg_temp_c'), 'core_throttle_alloc': ' '.join(str(x) for x in b['core_throttle'].values()),
            'pkg_throttle': b.get('pkg_throttle'), **{k: st.get(k) for k in ('governor', 'no_turbo', 'numa_balancing', 'thp')},
            'intel_pstate': st.get('intel_pstate'), 'inhibit': b.get('inhibit')}


def load(p):
    with open(p) as f:
        d = json.load(f)
    d['stat'] = {int(k): v for k, v in d['stat'].items()}
    return d


def selftest():
    def mk(busy_map, nc=0, gov='powersave', inhibit=1, load='0.10 0.10 0.10 1/900 1'):
        a = {'utc': 'a', 'mono': 0.0, 'stat': {}, 'running_containers': nc, 'loadavg': load, 'state': {}, 'mhz': {}, 'core_throttle': {}, 'inhibit': inhibit}
        b = json.loads(json.dumps(a)); b['utc'] = 'b'; b['mono'] = 2.0; b['stat'] = {}; a['stat'] = {}
        topo = {}
        for c in range(112):
            a['stat'][c] = {'total': 0, 'idle': 0}
            u = busy_map.get(c, 0.0)
            b['stat'][c] = {'total': 1000, 'idle': int(1000 * (1 - u))}
            topo[c] = f'{c % 56},{c % 56 + 56}'
        b['topology'] = topo
        b['state'] = {'intel_pstate': 'active', 'governor': gov, 'no_turbo': '0', 'numa_balancing': '1', 'thp': 'madvise'}
        return a, b
    alloc = cpus('1-8'); ok = True
    cases = [('clean idle host accepted', mk({0: 0.2}), 'pre', True),
             ('busy SMT sibling rejected (pre)', mk({57: 0.5}), 'pre', False),
             ('busy SMT sibling rejected (during)', mk({60: 0.2}), 'during', False),
             ('busy other CPUs rejected', mk({c: 0.5 for c in range(20, 30)}), 'during', False),
             ('running container rejected', mk({}, nc=1), 'pre', False),
             ('changed governor rejected', mk({}, gov='performance'), 'pre', False),
             ('missing inhibitor rejected', mk({}, inhibit=0), 'pre', False),
             ('high load1 alone recorded, not rejected (AMD-D2-1)', mk({}, load='5.0 4.0 3.0 1/900 1'), 'pre', True),
             ('allocated CPUs busy during own container accepted', mk({c: 1.0 for c in alloc}), 'during', True)]
    for name, (a, b), mode, want in cases:
        got = check(a, b, mode, alloc, FROZEN_DEFAULT)['accepted']
        print(f"{'PASS' if got == want else 'FAIL'}: {name}"); ok &= got == want
    return 0 if ok else 1


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == 'selftest':
        sys.exit(selftest())
    if len(sys.argv) == 3 and sys.argv[1] == 'snap':
        with open(sys.argv[2], 'w') as f:
            json.dump(snap(), f)
        return
    if len(sys.argv) >= 4 and sys.argv[1] == 'check':
        a, b = load(sys.argv[2]), load(sys.argv[3]); args = sys.argv[4:]
        opt = lambda n, d=None: args[args.index(n) + 1] if n in args else d
        r = check(a, b, opt('--mode', 'pre'), cpus(opt('--alloc', '1-8')), opt('--frozen', FROZEN_DEFAULT))
        print(json.dumps(r)); sys.exit(0 if r['accepted'] else 1)
    print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()
