"""Fig. 5 - supporting prover evidence. D1 (Host A, cpu8, tested snarkjs configuration) dominates:
(a) median prove time per D1 cell with 95 % bootstrap interval of the median (PLONK; Groth16 control), PLONK domain
boundary between pad-below and pad-above; (b) D1 ratio contrast (median of per-round ratios, 95 % bootstrap interval);
(c) context: PLONK d11/d10 ratio of medians by host and allocation (D3 Host A, D2 Host B), never pooled.
Inputs: fig5_d1_cells.csv, fig5_d1_ratios.csv, fig5_step_ratios.csv. Display transforms only (ms -> s, ordering, labels)."""
import matplotlib.pyplot as plt
import figstyle as S

CELLS = [('d10', 'd10'), ('p1150', 'pad-below'), ('p1180', 'pad-above'), ('d11', 'd11')]
RATIOS = ['pad-above/pad-below', 'd11/d10', 'pad-below/d10', 'd11/pad-above']

def main():
    C = S.read_csv('fig5_d1_cells.csv'); Rt = S.read_csv('fig5_d1_ratios.csv'); St = S.read_csv('fig5_step_ratios.csv')
    cell = {(x['backend'], x['cell']): x for x in C}
    pw = [int(cell[('plonk', c)]['plonk_domain_power']) for c, _ in CELLS]
    if not (pw[0] == pw[1] and pw[2] == pw[3] and pw[2] == pw[1] + 1):
        raise SystemExit('Fig. 5: the PLONK domain boundary is not between pad-below and pad-above in the data')
    fig = plt.figure(figsize=(S.FULL_W, 60 * S.MM))
    a1 = fig.add_axes([0.105, 0.56, 0.255, 0.35]); a2 = fig.add_axes([0.105, 0.285, 0.255, 0.21])
    for ax, b, unit, conv in ((a1, 'plonk', 's', 1e-3), (a2, 'groth16', 'ms', 1.0)):
        st = S.BK[b]
        for i, (c, lab) in enumerate(CELLS):
            x = cell[(b, c)]; m = float(x['median_ms']) * conv; lo = float(x['boot_lo95_ms']) * conv; hi = float(x['boot_hi95_ms']) * conv
            ax.errorbar(i, m, yerr=[[m - lo], [hi - m]], fmt=st['marker'], ms=3.6, color=st['color'], mfc=st['color'], ecolor=st['color'], elinewidth=0.8, capsize=2)
        ax.axvline(1.5, color='#595959', lw=0.7, ls='--')
        ax.set_xlim(-0.5, 3.5); ax.set_xticks(range(4))
        ax.set_ylabel(f'{S.BACKEND[b]}\nprove time ({unit})', fontsize=6.5)
    a1.set_xticklabels([]); a1.set_ylim(8, 20.5)
    a1.text(1.5, 13.6, r'PLONK domain' + '\n' + r'$2^{15}\rightarrow 2^{16}$', ha='center', va='center', fontsize=6.0, bbox=dict(fc='white', ec='none', pad=0.6))
    lo2 = min(float(cell[('groth16', c)]['boot_lo95_ms']) for c, _ in CELLS); hi2 = max(float(cell[('groth16', c)]['boot_hi95_ms']) for c, _ in CELLS)
    a2.set_ylim(lo2 - 15, hi2 + 15); a2.text(3.45, hi2 + 12, 'control', ha='right', va='top', fontsize=6.0, style='italic')
    a2.set_xticklabels([f"{lab}\n{int(cell[('plonk', c)]['plonk_gates']):,}\n" + r'$2^{%d}$' % p for (c, lab), p in zip(CELLS, pw)], fontsize=5.9)
    a2.text(-0.62, -0.215, 'cell\nPLONK gates\nPLONK domain', transform=a2.get_xaxis_transform(), ha='right', va='top', fontsize=5.9, color='#404040', linespacing=1.2)
    S.panel_label(a1, 'a', x=-0.30, y=1.04)
    a1.set_title('D1 cells, Host A, cpu8 (median, 95 % CI)', fontsize=6.5, pad=3, loc='left')

    b = fig.add_axes([0.535, 0.285, 0.215, 0.625])
    b.axvline(1.0, color='#000000', lw=0.6)
    for j, bk in enumerate(('plonk', 'groth16')):
        st = S.BK[bk]
        for i, r in enumerate(RATIOS):
            x = [y for y in Rt if y['backend'] == bk and y['ratio'] == r and y['stage'] == 'prove_ms'][0]
            m, lo, hi = float(x['median']), float(x['boot_median_lo95']), float(x['boot_median_hi95'])
            yy = len(RATIOS) - 1 - i + (0.14 if bk == 'plonk' else -0.14)
            b.errorbar(m, yy, xerr=[[m - lo], [hi - m]], fmt=st['marker'], ms=3.6, color=st['color'], mfc=st['color'], elinewidth=0.8, capsize=2, label=S.BACKEND[bk] if i == 0 else None)
    b.set_yticks(range(len(RATIOS))); b.set_yticklabels(list(reversed(RATIOS)), fontsize=6.3)
    b.set_ylim(-0.6, len(RATIOS) - 0.4); b.set_xlim(0.7, 2.15); b.set_xlabel('prove-time ratio\n(median of per-round ratios, 95 % CI)', fontsize=6.3)
    b.legend(loc='lower right', fontsize=6.2, handletextpad=0.3, borderaxespad=0.2)
    b.set_title('D1 ratio contrast', fontsize=6.5, pad=3, loc='left'); S.panel_label(b, 'b', x=-0.50, y=1.0)

    c = fig.add_axes([0.83, 0.285, 0.16, 0.625])
    for h, mk, fc, dx in (('A', 'o', '#404040', -0.12), ('B', 's', 'white', 0.12)):
        rows = [x for x in St if x['host'] == h]
        al = [x['allocation'] for x in rows]
        if al != ['cpu2', 'cpu4', 'cpu8']:
            raise SystemExit(f'Fig. 5: unexpected allocations for host {h}: {al}')
        c.plot([i + dx for i in range(3)], [float(x['ratio_d11_over_d10']) for x in rows], ls='none', marker=mk, ms=3.8, mfc=fc, mec='#000000', mew=0.8,
               label=f'Host {h} ({"D3" if h == "A" else "D2"})')
    c.set_xticks(range(3)); c.set_xticklabels(['cpu2', 'cpu4', 'cpu8']); c.set_xlim(-0.5, 2.5); c.set_ylim(1.88, 2.02)
    c.set_xlabel('allocation', fontsize=6.5); c.set_ylabel('PLONK d11 / d10\n(ratio of medians)', fontsize=6.5)
    c.legend(loc='lower right', fontsize=6.0, handletextpad=0.2, borderaxespad=0.2)
    c.set_title('context, not pooled', fontsize=6.5, pad=3, loc='left'); S.panel_label(c, 'c', x=-0.55, y=1.0)
    return S.save(fig, 'Fig5')

if __name__ == '__main__':
    print(main(), S.inputs_read())
