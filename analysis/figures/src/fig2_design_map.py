"""Fig. 2 - study design map. Input: generated/data/fig2_design_roles.csv (frozen C1 role matrix).
Shows the frozen roles exactly as registered; no role is merged or re-labelled (G16 and PLONK roles are checked equal per tile)."""
import re
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import figstyle as S

KS = [1, 2, 4, 6, 8, 12, 16, 24, 32, 64]
ROWS = [('evm-osaka', 'EVM Osaka', 'CORE'), ('eravm-29', 'EraVM v29', 'CORE'), ('zkos-v32@npg100', 'ZKsync OS v32\n(npg = 100)', 'CORE'),
        ('eravm-27', 'EraVM v27', 'VALIDATION'), ('evm-petersburg', 'EVM Petersburg', 'SUPPORTING')]
# role -> (letter, face, edge, hatch, linestyle, text colour, legend text)
ROLE = {
    'CALIBRATION':                ('C', '#3A3A3A', '#000000', None, '-', 'white', 'calibration'),
    'HELD-OUT-k/seen-in-P0':      ('S', '#A6A6A6', '#000000', None, '-', 'black', 'held-out k, seen in P0'),
    'HELD-OUT-k/strictly-unseen': ('U', '#FFFFFF', '#000000', None, '-', 'black', 'held-out k, strictly unseen'),
    'HELD-OUT-k':                 ('H', '#D9D9D9', '#000000', '....', '-', 'black', 'held-out k (ZKsync OS matrix role)'),
    'HELD-OUT-REGIME':            ('R', '#FFFFFF', '#000000', '////', '-', 'black', 'held-out regime (validation)'),
    'LIMIT-CHECK':                ('L', '#FFFFFF', '#000000', None, '--', 'black', 'limit check (descriptive)'),
    'SUPPORTING-CONTROL':         ('n', '#FFFFFF', '#A6A6A6', None, ':', '#808080', 'supporting control, specified, not run'),
}

def tile_roles(rows):
    t = defaultdict(lambda: defaultdict(set)); extra = defaultdict(set); sem = defaultdict(set); ff = {}
    for x in rows:
        reg, b, c, k, role = x['regime'], x['backend'], x['circuit'], int(x['k']), x['role']
        if reg not in dict((r[0], 1) for r in ROWS):
            continue
        if b == 'fflonk':
            ff[(reg, k)] = role; continue
        if c in ('c1_a4', 'c1_a8', 'c1_disc_k04'):
            sem[(reg, k)].add((c, role)); continue
        if role == 'CALIBRATION (base, c)':
            extra[(reg, k)].add('base, c'); continue
        t[(reg, k)][b].add(role)
    tiles = {}
    for key, by_b in t.items():
        if by_b.get('groth16') != by_b.get('plonk') or len(by_b['groth16']) != 1:
            raise SystemExit(f'Fig. 2: Groth16 / PLONK roles differ at {key}: {dict(by_b)} - tile would hide a frozen role')
        tiles[key] = next(iter(by_b['groth16']))
    return tiles, extra, sem, ff

def main():
    rows = S.read_csv('fig2_design_roles.csv')
    tiles, extra, sem, ff = tile_roles(rows)
    unknown = {r for r in tiles.values()} - set(ROLE)
    if unknown:
        raise SystemExit(f'Fig. 2: unmapped frozen roles {unknown}')
    fig = plt.figure(figsize=(S.FULL_W, 80 * S.MM))
    ax = fig.add_axes([0.135, 0.33, 0.545, 0.60]); ax.set_axis_off()
    tw, th, gap = 1.0, 0.78, 0.5     # tile width / height in axis units; extra gap before k = 64
    xs = {k: i * 1.08 + (gap if k == 64 else 0) for i, k in enumerate(KS)}
    for r, (reg, label, cls) in enumerate(ROWS):
        y = -r
        ax.text(-0.25, y + th / 2, label, ha='right', va='center', fontsize=6.8, linespacing=0.95)
        ax.text(-0.25, y + th / 2 - (0.34 if '\n' not in label else 0.52), cls.lower(), ha='right', va='center', fontsize=5.6, color='#595959', style='italic')
        for k in KS:
            role = tiles.get((reg, k))
            if role is None:
                continue
            let, fc, ec, hat, ls, tc, _ = ROLE[role]
            ax.add_patch(Rectangle((xs[k], y), tw, th, facecolor=fc, edgecolor=ec, hatch=hat, linestyle=ls, linewidth=0.7))
            txt = let if not extra.get((reg, k)) else f'{let}\n' + ', '.join(sorted(extra[(reg, k)]))
            ax.text(xs[k] + tw / 2, y + th / 2, txt, ha='center', va='center', fontsize=6.3 if '\n' not in txt else 4.6, color=tc,
                    fontweight='bold' if '\n' not in txt else 'normal', linespacing=0.9,
                    bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none') if hat else None)
            if (reg, k) in sem:
                ax.add_patch(Polygon([(xs[k] + tw - 0.2, y + th), (xs[k] + tw, y + th), (xs[k] + tw, y + th - 0.2)], closed=True, fc='#000000', ec='none'))
            if (reg, k) in ff:
                held = ff[(reg, k)] == 'HELD-OUT-BACKEND'
                ax.plot(xs[k] + 0.14, y + 0.15, marker='^', ms=3.6, mfc=S.BK['fflonk']['color'] if held else 'white', mec=S.BK['fflonk']['color'], mew=0.8)
    for k in KS:
        ax.text(xs[k] + tw / 2, 1.0, str(k), ha='center', va='bottom', fontsize=6.8)
    ax.text((xs[32] + xs[1] + tw) / 2, 1.42, 'verifier-visible interface size k (CORE grid)', ha='center', va='bottom', fontsize=7)
    ax.text(xs[64] + tw / 2, 1.42, 'limit', ha='center', va='bottom', fontsize=6.3, style='italic')
    ax.plot([xs[64] - gap / 2 - 0.04] * 2, [-len(ROWS) + 0.85, 1.35], color='#808080', lw=0.6, ls=':')
    ax.set_xlim(-0.1, xs[64] + tw + 0.1); ax.set_ylim(-len(ROWS) + 0.7, 1.9)
    S.panel_label(ax, 'a', x=-0.19, y=0.98)

    # (b) native_per_gas intervention cells (ZKsync OS v32; bytecode fixed); levels parsed from the frozen regime names
    bx = fig.add_axes([0.745, 0.415, 0.235, 0.38])
    lv = defaultdict(set)
    for x in rows:
        m = re.fullmatch(r'zkos-v32@npg(\d+)', x['regime'])
        if m and x['role'] == 'HELD-OUT-REGIME/INTERVENTION' and x['backend'] in ('groth16', 'plonk'):
            lv[int(x['k'])].add(int(m.group(1)))
    pos = lambda n: n if n <= 175 else 190
    for i, k in enumerate((1, 4, 16)):
        y = 2 - i
        bx.plot([pos(100)], [y], marker='s', ms=3.4, mfc='white', mec='#000000', mew=0.8, ls='none')
        ns = sorted(lv[k]); bx.plot([pos(n) for n in ns], [y] * len(ns), marker='s', ms=3.4, mfc=S.RG['zkos-v32@npg100']['color'], mec='#000000', mew=0.5, ls='none', alpha=None)
        bx.plot([pos(100), pos(ns[-1])], [y, y], color='#BFBFBF', lw=0.6, zorder=0)
    bx.set_yticks([2, 1, 0]); bx.set_yticklabels(['k = 1', 'k = 4', 'k = 16']); bx.set_ylim(-0.6, 2.6)
    bx.set_xticks([100, 125, 150, 175, 190]); bx.set_xticklabels(['100', '125', '150', '175', '300']); bx.set_xlim(94, 196)
    bx.text(182.5, -0.6, '//', ha='center', va='center', fontsize=7, clip_on=False, bbox=dict(fc='white', ec='none', pad=0))
    bx.set_xlabel('native_per_gas (npg)')
    bx.set_title('ZKsync OS v32: bytecode fixed,\nonly npg varied (open: CORE default)', fontsize=6.6, pad=3, loc='left')
    S.panel_label(bx, 'b', x=-0.12, y=1.20)

    # legend (shared)
    lg = fig.add_axes([0.02, 0.0, 0.96, 0.25]); lg.set_axis_off(); lg.set_xlim(0, 100); lg.set_ylim(0, 10)
    items = [r for r in ROLE if r in set(tiles.values())]
    for i, r in enumerate(items):
        let, fc, ec, hat, ls, tc, txt = ROLE[r]
        cx, cy = 1 + (i % 3) * 33, 8.4 - (i // 3) * 2.75
        lg.add_patch(Rectangle((cx, cy - 0.9), 2.2, 1.9, fc=fc, ec=ec, hatch=hat, ls=ls, lw=0.7))
        lg.text(cx + 1.1, cy + 0.05, let, ha='center', va='center', fontsize=5.8, color=tc, fontweight='bold', bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none') if hat else None)
        lg.text(cx + 3.0, cy + 0.05, txt, ha='left', va='center', fontsize=6.2)
    yb = 0.2
    lg.add_patch(Polygon([(1, yb + 1.0), (2.2, yb + 1.0), (2.2, yb - 0.2)], closed=True, fc='#000000'))
    lg.text(3.0, yb + 0.4, 'semantic anchors a4, disc (k = 4), a8 (k = 8)', ha='left', va='center', fontsize=6.2)
    lg.plot(34.6, yb + 0.4, marker='^', ms=3.6, mfc=S.BK['fflonk']['color'], mec=S.BK['fflonk']['color'], mew=0.8)
    lg.text(36.0, yb + 0.4, 'FFLONK, held-out backend', ha='left', va='center', fontsize=6.2)
    lg.plot(53.6, yb + 0.4, marker='^', ms=3.6, mfc='white', mec=S.BK['fflonk']['color'], mew=0.8)
    lg.text(55.0, yb + 0.4, 'FFLONK, descriptive (rank only)', ha='left', va='center', fontsize=6.2)
    lg.text(34.0, yb + 2.75 + 0.4 - 2.75 * 0 , '', fontsize=1)
    lg.text(67.0 + 3.0, 8.4 - 2 * 2.75 + 0.05, '"base, c": also calibrates base_zk, c_zk', ha='left', va='center', fontsize=6.2)

    return S.save(fig, 'Fig2')

if __name__ == '__main__':
    print(main(), S.inputs_read())
