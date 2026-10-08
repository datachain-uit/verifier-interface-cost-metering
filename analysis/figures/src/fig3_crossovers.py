"""Fig. 3 - (a) within-regime PLONK/Groth16 cost ratio versus k with frozen and measured crossovers;
(b) native_per_gas intervention on ZKsync OS v32 (bytecode fixed). Inputs: fig3a_ratio_vs_k.csv, crossovers.csv,
fig3b_npg_ranking.csv, fig3b_npg_meters.csv, fig3b_switch_intervals.csv. Display transforms only: log2 axis, linear-in-k
visual guides between measured grid points (crossover values themselves are read from crossovers.csv), axis break for npg = 300."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, NullLocator
import figstyle as S

ORDER = ['eravm-29', 'zkos-v32@npg100', 'eravm-27', 'evm-osaka']           # by registered k* interval (left to right)
METRIC = {'evm-osaka': 'Y_dir', 'eravm-29': 'Y_dir', 'eravm-27': 'Y_dir', 'zkos-v32@npg100': 'Y_dir'}
KT = [1, 2, 4, 6, 8, 12, 16, 24, 32, 64]
npos = lambda n: n if n <= 175 else 190

def panel_a(ax, sx, R, X):
    ax.axhline(1.0, color='#000000', lw=0.7, zorder=1)
    handles = []
    for reg in ORDER:
        st = S.RG[reg]; rows = sorted((x for x in R if x['regime'] == reg and x['metric'] == METRIC[reg]), key=lambda x: int(x['k']))
        core = [x for x in rows if x['limit_check'] == 'no']; lim = [x for x in rows if x['limit_check'] == 'yes']
        k = np.array([int(x['k']) for x in core], float); r = np.array([float(x['ratio_plonk_over_groth16']) for x in core])
        kk = np.concatenate([np.linspace(a, b, 24) for a, b in zip(k[:-1], k[1:])]); rr = np.interp(kk, k, r)   # visual guide only
        ax.plot(kk, rr, color=st['color'], ls=st['ls'], lw=0.8, zorder=2)
        ax.plot(k, r, ls='none', marker=st['marker'], ms=3.6, mfc=st['color'] if st['role'] == 'CORE' else 'white', mec=st['color'], mew=0.9, zorder=3)
        for x in lim:
            ax.plot(int(x['k']), float(x['ratio_plonk_over_groth16']), ls='none', marker=st['marker'], ms=3.6, mfc='white', mec=st['color'], mew=0.7, zorder=3)
        handles.append(plt.Line2D([], [], color=st['color'], ls=st['ls'], lw=0.8, marker=st['marker'], ms=3.6,
                                  mfc=st['color'] if st['role'] == 'CORE' else 'white', mec=st['color'], mew=0.9,
                                  label=S.REGIME[reg] + (' (validation)' if st['role'] != 'CORE' else '') + (' (gas, npg = 100)' if reg.startswith('zkos') else '')))
        xo = [x for x in X if x['regime'] == reg and x['metric'] == METRIC[reg]][0]
        ax.plot(float(xo['kstar_measured']), 1.0, marker='|', ms=7, mew=1.4, color=st['color'], zorder=4)
    ax.set_xscale('log', base=2); ax.xaxis.set_major_locator(FixedLocator(KT)); ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([str(k) for k in KT]); ax.set_xlim(0.85, 90)
    ax.axvspan(45, 90, color='#F2F2F2', zorder=0, lw=0); ax.text(64, ax.get_ylim()[1] if False else 1.42, 'limit check\n(open)', ha='center', va='top', fontsize=5.8, style='italic', color='#595959')
    ax.set_ylim(0.4, 1.45); ax.set_ylabel('PLONK / Groth16 cost ratio\n(within regime)')
    ax.text(40, 1.008, 'parity', ha='right', va='bottom', fontsize=5.8, color='#595959')
    handles.append(plt.Line2D([], [], color='#000000', marker='|', ms=7, mew=1.4, ls='none', label='measured k* (on parity line)'))
    ax.legend(handles=handles, loc='upper right', bbox_to_anchor=(0.86, 1.0), fontsize=6.2, handlelength=2.6, ncol=1, borderaxespad=0.2)
    ax.tick_params(labelbottom=False)
    # strip: registered k* interval (bar) and frozen point (tick) vs measured k* (marker / interval)
    sx.set_xscale('log', base=2); sx.xaxis.set_major_locator(FixedLocator(KT)); sx.xaxis.set_minor_locator(NullLocator())
    sx.set_xticklabels([str(k) for k in KT]); sx.set_xlim(0.85, 90); sx.axvspan(45, 90, color='#F2F2F2', zorder=0, lw=0)
    for i, reg in enumerate(ORDER):
        st = S.RG[reg]; xo = [x for x in X if x['regime'] == reg and x['metric'] == METRIC[reg]][0]; y = len(ORDER) - 1 - i
        lo_open = xo['frozen_lo'].startswith('<=')
        lo = 0.86 if lo_open else float(xo['frozen_lo']); hi = float(xo['frozen_hi'])
        sx.add_patch(Rectangle((lo, y - 0.22), hi - lo, 0.44, fc=st['color'], ec='none', alpha=0.28 if st['role'] == 'CORE' else 0.18))
        if lo_open:
            sx.annotate('', xy=(0.86, y), xytext=(1.02, y), arrowprops=dict(arrowstyle='->', lw=0.6, color='#000000'))
        sx.plot([float(xo['frozen_point'])] * 2, [y - 0.26, y + 0.26], color='#000000', lw=0.7)
        mlo, mhi = float(xo['measured_lo']), float(xo['measured_hi'])
        if mhi > mlo:
            sx.plot([mlo, mhi], [y, y], color=st['color'], lw=2.2, solid_capstyle='butt')
        sx.plot(float(xo['kstar_measured']), y, marker=st['marker'], ms=3.6, mfc=st['color'] if st['role'] == 'CORE' else 'white', mec='#000000', mew=0.6, ls='none')
    sx.set_yticks(range(len(ORDER))); sx.set_yticklabels([S.REGIME[r] for r in reversed(ORDER)], fontsize=6)
    sx.set_ylim(-0.6, len(ORDER) - 0.4); sx.set_xlabel('verifier-visible interface size k (log scale)')
    sx.text(0.86, 0.80, 'k*: shaded = registered interval; tick = registered point;\nmarker / bar = measured (EraVM v29: k = 1 in the equality band)', transform=sx.transAxes, ha='right', va='center', fontsize=5.8, color='#404040')

def panel_b(axes, saxes, N, M, W):
    for j, k in enumerate((1, 4, 16)):
        ax, sx = axes[j], saxes[j]
        rows = sorted((x for x in N if int(x['k']) == k), key=lambda x: int(x['npg']))
        n = [npos(int(x['npg'])) for x in rows]; r = [float(x['ratio']) for x in rows]
        for a in (ax, sx):
            for b, fc in (('plonk', '#B9D7EC'), ('groth16', '#9A9A9A')):
                w = [x for x in W if x['backend'] == b and int(x['k']) == k][0]
                a.axvspan(float(w['npg_switch_lo']), float(w['npg_switch_hi']), fc=fc, ec='none', lw=0, zorder=0)
        ax.axhline(1.0, color='#000000', lw=0.7)
        ax.plot(n, r, color=S.RG['zkos-v32@npg100']['color'], lw=0.8, ls='-.', zorder=2)
        ax.plot(n, r, ls='none', marker='D', ms=3.2, mfc=S.RG['zkos-v32@npg100']['color'], mec='#000000', mew=0.4, zorder=3)
        cls = [x['measured_class'] for x in rows]
        for i in range(1, len(rows)):
            if cls[i] != cls[i - 1]:
                ax.annotate('', xy=(n[i], 0.93), xytext=(n[i - 1], 0.93), arrowprops=dict(arrowstyle='<->', lw=0.7, color='#000000'))
                ax.text((n[i] + n[i - 1]) / 2, 0.915, 'ranking reverses\n(measured class)', ha='center', va='top', fontsize=5.6)
        ax.set_title(f'k = {k}', fontsize=6.8, pad=2); ax.set_ylim(0.75, 1.42); ax.tick_params(labelbottom=False)
        if j == 0:
            ax.set_ylabel('PLONK / Groth16\ngas ratio')
        for i, b in enumerate(('plonk', 'groth16')):
            for x in (y for y in M if int(y['k']) == k and y['backend'] == b):
                nat = x['measured_meter'] == 'NATIVE'
                sx.plot(npos(int(x['npg'])), 1 - i, marker=S.BK[b]['marker'], ms=3.0, ls='none', mfc=S.BK[b]['color'] if nat else 'white', mec=S.BK[b]['color'], mew=0.7)
        sx.set_yticks([1, 0]); sx.set_yticklabels(['PLONK', 'Groth16'] if j == 0 else ['', ''], fontsize=6); sx.set_ylim(-0.6, 1.6)
        for a in (ax, sx):
            a.set_xlim(94, 196); a.set_xticks([100, 125, 150, 175, 190])
        sx.set_xticklabels(['100', '125', '150', '175', '300']); sx.text(182.5, -0.6, '//', ha='center', va='center', fontsize=6.5, bbox=dict(fc='white', ec='none', pad=0))
        if j == 1:
            sx.set_xlabel('native_per_gas (npg)', fontsize=6.8, labelpad=1)
        if j == 0:
            sx.set_ylabel('binding\nmeter', fontsize=6.2)

def main():
    R = S.read_csv('fig3a_ratio_vs_k.csv'); X = S.read_csv('crossovers.csv')
    N = S.read_csv('fig3b_npg_ranking.csv'); M = S.read_csv('fig3b_npg_meters.csv'); W = S.read_csv('fig3b_switch_intervals.csv')
    fig = plt.figure(figsize=(S.FULL_W, 132 * S.MM))
    ax = fig.add_axes([0.105, 0.635, 0.86, 0.34]); sx = fig.add_axes([0.105, 0.49, 0.86, 0.125])
    panel_a(ax, sx, R, X); S.panel_label(ax, 'a', x=-0.075, y=0.96)
    fig.patches.append(Rectangle((0.015, 0.008), 0.97, 0.388, transform=fig.transFigure, fc='#F7F7F7', ec='#808080', lw=0.6, zorder=-1))
    fig.text(0.06, 0.378, 'Metering intervention (ZKsync OS v32): bytecode, state and corpus fixed; only native_per_gas varied',
             fontsize=6.8, fontweight='bold', va='center')
    axes, saxes = [], []
    for j in range(3):
        x0 = 0.105 + j * 0.295
        axes.append(fig.add_axes([x0, 0.155, 0.255, 0.145])); saxes.append(fig.add_axes([x0, 0.068, 0.255, 0.068]))
    panel_b(axes, saxes, N, M, W); fig.text(0.025, 0.378, '(b)', fontsize=8, fontweight='bold', va='center')
    lg = fig.add_axes([0.105, 0.333, 0.86, 0.026]); lg.set_axis_off(); lg.set_xlim(0, 100); lg.set_ylim(0, 1)
    lg.add_patch(Rectangle((0, 0.1), 2.2, 0.8, fc='#B9D7EC', ec='none')); lg.text(2.8, 0.5, 'registered meter-switch interval, PLONK', va='center', fontsize=6)
    lg.add_patch(Rectangle((29, 0.1), 2.2, 0.8, fc='#9A9A9A', ec='none')); lg.text(31.8, 0.5, 'registered meter-switch interval, Groth16', va='center', fontsize=6)
    lg.plot(60, 0.5, marker='s', ms=3, mfc=S.BK['plonk']['color'], mec=S.BK['plonk']['color']); lg.plot(61.6, 0.5, marker='o', ms=3, mfc='#000000', mec='#000000')
    lg.text(63, 0.5, 'filled: native-bound', va='center', fontsize=6)
    lg.plot(78, 0.5, marker='s', ms=3, mfc='white', mec=S.BK['plonk']['color']); lg.plot(79.6, 0.5, marker='o', ms=3, mfc='white', mec='#000000')
    lg.text(81, 0.5, 'open: EVM-gas-bound', va='center', fontsize=6)
    return S.save(fig, 'Fig3')

if __name__ == '__main__':
    print(main(), S.inputs_read())
