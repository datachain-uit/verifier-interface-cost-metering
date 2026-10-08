"""Shared visual style and I/O for the article figures (Figs. 2-5).

Rule: plotting code is not analysis code. Scripts read only canonical CSVs from
generated/data/ (through read_csv, which records the file hash), and may apply only display transforms (unit
conversion, normalisation by an already generated frozen tolerance, ordering, layout, formatting, visual
interpolation where the crossover quantity is already generated). No scientific quantity is computed here.
"""
import csv, hashlib, io
from pathlib import Path
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

ROOT = Path(__file__).resolve().parents[3]          # artifact root
DATA = ROOT / 'generated' / 'data'
FIGDIR = ROOT / 'figures'
MM = 1 / 25.4
FULL_W = 173.8 * MM      # cas-dc \textwidth  (494.5 pt)
COL_W = 83.7 * MM        # cas-dc \columnwidth (238.3 pt)

# ---- font: Liberation Sans 2.x (Arial-metric; Fig. 1 uses Arial in draw.io), embedded as TrueType (no Type 3)
FONT_DIR = Path('/usr/share/fonts/truetype/liberation2')
FONT_FILES = {s: FONT_DIR / f'LiberationSans-{s}.ttf' for s in ('Regular', 'Bold', 'Italic', 'BoldItalic')}
for f in FONT_FILES.values():
    if not f.exists():
        raise SystemExit(f'required font missing: {f} (fail closed; do not substitute silently)')
fm.fontManager.ttflist = [e for e in fm.fontManager.ttflist if e.name != 'Liberation Sans']
for f in FONT_FILES.values():
    fm.fontManager.addfont(str(f))
assert Path(fm.findfont(fm.FontProperties(family='Liberation Sans'))).parent == FONT_DIR

BASE = 7.0
plt.rcParams.update({
    'font.family': 'Liberation Sans', 'font.size': BASE, 'axes.labelsize': BASE, 'axes.titlesize': BASE,
    'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5, 'legend.fontsize': 6.5, 'legend.frameon': False,
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans', 'mathtext.it': 'Liberation Sans:italic',
    'mathtext.bf': 'Liberation Sans:bold', 'mathtext.sf': 'Liberation Sans', 'mathtext.cal': 'Liberation Sans', 'mathtext.tt': 'Liberation Sans', 'mathtext.default': 'it',
    'axes.unicode_minus': True, 'axes.linewidth': 0.6, 'axes.edgecolor': '#000000', 'axes.labelcolor': '#000000',
    'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'xtick.minor.width': 0.4, 'ytick.minor.width': 0.4,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'xtick.direction': 'out', 'ytick.direction': 'out',
    'axes.spines.top': False, 'axes.spines.right': False, 'lines.linewidth': 1.0, 'lines.markersize': 4,
    'hatch.linewidth': 0.5, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'svg.hashsalt': 'article-figures',
    'figure.dpi': 100, 'savefig.dpi': 600, 'path.simplify': False,
})

# ---- fixed names
BACKEND = {'groth16': 'Groth16', 'plonk': 'PLONK', 'fflonk': 'FFLONK'}
REGIME = {'evm-osaka': 'EVM Osaka', 'eravm-29': 'EraVM v29', 'zkos-v32@npg100': 'ZKsync OS v32', 'zkos-v32': 'ZKsync OS v32',
          'eravm-27': 'EraVM v27', 'evm-petersburg': 'EVM Petersburg'}

# ---- backend encoding (grayscale-safe: marker shape + line style + fill, colour only reinforces)
BK = {'groth16': dict(color='#000000', marker='o', ls='-'),
      'plonk':   dict(color='#0072B2', marker='s', ls='--'),
      'fflonk':  dict(color='#D55E00', marker='^', ls=':')}
# ---- regime encoding for ratio plots (colour + marker + line style + direct labels)
RG = {'evm-osaka':       dict(color='#000000', marker='o', ls='-',  lw=1.0, role='CORE'),
      'eravm-29':        dict(color='#E69F00', marker='s', ls='--', lw=1.0, role='CORE'),
      'zkos-v32@npg100': dict(color='#009E73', marker='D', ls='-.', lw=1.0, role='CORE'),
      'eravm-27':        dict(color='#CC79A7', marker='^', ls=':',  lw=1.0, role='VALIDATION')}
GREY = {'band': '#E6E6E6', 'light': '#D9D9D9', 'mid': '#A6A6A6', 'dark': '#595959'}

_inputs = {}

def read_csv(name):
    """Read a canonical CSV from generated/data/ only, recording its sha256."""
    p = (DATA / name).resolve()
    if p.parent != DATA.resolve():
        raise SystemExit(f'figure scripts may read generated/data/ only: {name}')
    b = p.read_bytes(); _inputs[name] = hashlib.sha256(b).hexdigest()
    return list(csv.DictReader(io.StringIO(b.decode('utf-8'))))

def inputs_read():
    return dict(sorted(_inputs.items()))

def panel_label(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, f'({s})', transform=ax.transAxes, fontsize=8, fontweight='bold', ha='right', va='bottom')

def save(fig, stem):
    """Write vector PDF + SVG with deterministic metadata; refuse rasterized artists."""
    for a in fig.findobj():
        if getattr(a, 'get_rasterized', lambda: False)():
            raise SystemExit(f'{stem}: rasterized artist {a!r}')
    out = {}
    for ext, meta in (('pdf', {'CreationDate': None, 'ModDate': None, 'Producer': None}), ('svg', {'Date': None})):
        p = FIGDIR / f'{stem}.{ext}'
        fig.savefig(p, format=ext, metadata=meta, bbox_inches=None)
        out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    plt.close(fig)
    return out
