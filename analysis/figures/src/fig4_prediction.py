"""Fig. 4 - registered native-cost predictions on ZKsync OS v32 against frozen tolerances.
Input: generated/data/fig4_prediction_errors.csv (frozen ZC_scoring rows for H4; frozen C1 FFLONK residual columns for H8).
y = err_over_tau as generated (error / frozen tau_cond). Every proof is drawn; the proofs of a cell carry (nearly) identical
errors and overlap at the cell's k. Semantic-anchor relations are drawn beside their k (layout offset only).
C2 is a separate test and is not drawn on these axes."""
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator
import figstyle as S

PANELS = [('groth16', 'C1-H4 (ZC)', 'Groth16 — H4', 'held-out k'), ('plonk', 'C1-H4 (ZC)', 'PLONK — H4', 'held-out k'),
          ('fflonk', 'C1-H8 (FFLONK)', 'FFLONK — H8', 'held-out backend')]
KT = [1, 2, 4, 8, 16, 32, 64]
SEM_MARK = {'a4': 'D', 'a8': 'D', 'disc': 'P'}
SEM_OFF = {'ctx': 0.0, 'a4': 0.26, 'a8': 0.26, 'disc': 0.48}

def main():
    rows = S.read_csv('fig4_prediction_errors.csv')
    fig, axs = plt.subplots(1, 3, figsize=(S.FULL_W, 62 * S.MM), sharey=True)
    fig.subplots_adjust(left=0.075, right=0.995, top=0.80, bottom=0.30, wspace=0.08)
    for ax, (b, test, title, role) in zip(axs, PANELS):
        pr = [x for x in rows if x['backend'] == b and x['test'] == test]
        taus = sorted({x['tau_cond'] for x in pr})
        if len(taus) != 1:
            raise SystemExit(f'Fig. 4: {b}: more than one frozen tolerance in the panel')
        ax.axhspan(-1, 1, color=S.GREY['band'], lw=0, zorder=0); ax.axhline(0, color='#808080', lw=0.5, zorder=1)
        ax.axvspan(45, 95, color='#F2F2F2', lw=0, zorder=0)
        st = S.BK[b]; fails = defaultdict(list)
        for x in pr:
            k = int(x['k']); rel = x['relation']; y = float(x['err_over_tau'])
            xpos = k * 2 ** SEM_OFF[rel]
            mk = st['marker'] if rel == 'ctx' else SEM_MARK[rel]
            if x['status'] == 'PASS':
                kw = dict(mfc=st['color'], mec=st['color'], mew=0.5)
            elif x['status'] == 'FAIL':
                kw = dict(mfc='white', mec=st['color'], mew=1.1); fails[k].append(y)
            elif x['status'] == 'DESCRIPTIVE FAIL' and x['limit_check'] == 'yes':
                kw = dict(mfc='white', mec='#808080', mew=0.8)
            else:
                raise SystemExit(f'Fig. 4: unexpected status / role {x["status"]} {x["limit_check"]}')
            ax.plot(xpos, y, ls='none', marker=mk, ms=3.2 if mk != 'P' else 3.6, zorder=3, **kw)
        if fails:
            kf = sorted(fails); tag = 'F4' if b != 'fflonk' else 'F8'
            if b == 'fflonk':
                ax.annotate(f'{tag}: outside frozen\ntolerance (k = {kf[-1]})', xy=(kf[-1], min(fails[kf[-1]])), xytext=(14, -2.3), textcoords='data',
                            ha='center', va='top', fontsize=6.3, fontweight='bold', arrowprops=dict(arrowstyle='->', lw=0.7, color='#000000', shrinkB=3))
            else:
                ax.annotate(f'{tag}: outside frozen\ntolerance', xy=(kf[-1], min(fails[kf[-1]])), xytext=(-6, -10), textcoords='offset points',
                            ha='right', va='top', fontsize=6.3, fontweight='bold')
        tau_pct = float(taus[0]) * 100
        ax.set_title(f'{title}\n({role}; ' + r'$\tau_{\mathrm{cond}}$' + f' = {tau_pct:.3g} %)', fontsize=6.8, pad=3)
        ax.set_xscale('log', base=2); ax.xaxis.set_major_locator(FixedLocator(KT)); ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xticklabels([str(k) for k in KT]); ax.set_xlim(0.8, 95)
        ax.text(64, -2.0, 'limit\ncheck', ha='center', va='center', fontsize=5.8, style='italic', color='#595959')
        ax.set_xlabel('k')
    axs[0].set_ylim(-4.6, 1.65); axs[0].set_ylabel('prediction error / frozen ' + r'$\tau_{\mathrm{cond}}$')
    axs[0].text(0.85, 1.0, '±1 = frozen\nacceptance bound', ha='left', va='center', fontsize=5.8, color='#404040')
    for i, s in enumerate('abc'):
        S.panel_label(axs[i], s, x=-0.02 if i else -0.17, y=1.20)
    lg = fig.add_axes([0.075, 0.0, 0.92, 0.12]); lg.set_axis_off(); lg.set_xlim(0, 100); lg.set_ylim(0, 1)
    items = [(1, 'o', '#000000', '#000000', 0.5, 'inside tolerance (filled)'), (22, 'o', 'white', '#000000', 1.1, 'outside tolerance: registered fail (open, heavy)'),
             (56, 'o', 'white', '#808080', 0.8, 'k = 64 limit check, descriptive (grey)'), (81, 'D', '#000000', '#000000', 0.5, 'anchors a4, a8')]
    for x0, m, fc, ec, mew, t in items:
        lg.plot(x0, 0.5, marker=m, ms=3.4, mfc=fc, mec=ec, mew=mew, ls='none'); lg.text(x0 + 1.5, 0.5, t, va='center', fontsize=6.1)
    lg.plot(93.0, 0.5, marker='P', ms=3.8, mfc='#000000', mec='#000000', ls='none'); lg.text(94.5, 0.5, 'disc', va='center', fontsize=6.1)
    return S.save(fig, 'Fig4')

if __name__ == '__main__':
    print(main(), S.inputs_read())
