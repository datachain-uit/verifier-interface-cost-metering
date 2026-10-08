# Environment

## Levels 1 and 2 (reference environment)

| Component | Reference version | Needed for |
|---|---|---|
| Linux, x86-64 or arm64 | Ubuntu 22.04 | all |
| Python | 3.10; the verified reference for byte identity is **Python 3.10.12** (the `python3` of Ubuntu 22.04) | Levels 1, 2 |
| matplotlib, numpy | 3.10.9, 2.2.6 (`requirements-level2.txt`) | Figs. 2–5 |
| Liberation Sans 2.1.5 | the four files `/usr/share/fonts/truetype/liberation2/LiberationSans-{Regular,Bold,Italic,BoldItalic}.ttf` whose SHA-256 values `figures/FIGURES-MANIFEST.json` records (Ubuntu 22.04 package `fonts-liberation2` 2.1.5-1); the build stops if a file is missing, and the figure check fails if a file differs | Figs. 2–5 |
| poppler-utils | `pdffonts`, `pdfimages` | figure vector gates |
| node, npm | node 18 or later | `scripts/regenerate-keys.sh` only (installs the pinned snarkjs 0.7.5 from `protocols/prover-d1/kit/package-lock.json` into a work directory) |

Setup on Ubuntu 22.04 (reference):

```
sudo apt-get install -y python3 python3-pip fonts-liberation2 poppler-utils
python3 -m pip install -r environment/requirements-level2.txt
```

### Python version

Byte identity of the Level 2 outputs is verified with Python 3.10.12. Python 3.13 was also tested and is not a reference
environment for exact reproduction: under Python 3.13 the D1, D2 and D3 analyses (`scoring/rescore.py d1 d2 d3`) differ
from the frozen outputs only in the last digit of some `sd` and `cv` values, because of runtime floating-point behaviour
of the standard-library `statistics` functions, and `rescore.py` reports these three families as DIFF; every other
Level 2 output was identical. On a system whose `python3` is not 3.10.12, create a virtual environment from a Python
3.10.12 interpreter and activate it, so that `python3` in the commands of this artifact is Python 3.10.12.

### Fonts on Ubuntu 24.04

On Ubuntu 24.04, `fonts-liberation2` is a transitional package: installing it does not by itself provide the files at
`/usr/share/fonts/truetype/liberation2/`, and the figure build stops (fail closed; no font is substituted). Install the
exact Liberation 2.1.5 files of the Ubuntu 22.04 package instead (the `.deb` has SHA-256
`787ae3c986eb6d61daa383aa7c3be2e55e4f9bf0f903047caeb4c066038ccaec`) and compare the font hashes with
`figures/FIGURES-MANIFEST.json`:

```
cd "$(mktemp -d)"
curl -fLO http://archive.ubuntu.com/ubuntu/pool/main/f/fonts-liberation2/fonts-liberation2_2.1.5-1_all.deb
sha256sum fonts-liberation2_2.1.5-1_all.deb
dpkg-deb -x fonts-liberation2_2.1.5-1_all.deb x
sudo mkdir -p /usr/share/fonts/truetype/liberation2
sudo cp x/usr/share/fonts/truetype/liberation2/LiberationSans-*.ttf /usr/share/fonts/truetype/liberation2/
sha256sum /usr/share/fonts/truetype/liberation2/LiberationSans-*.ttf
```

The four printed font hashes must equal the `fonts` entries of `figures/FIGURES-MANIFEST.json`.

Byte identity of the figure PDFs is expected only with matplotlib 3.10.9 and these font files; with other versions the
figures are equivalent but not byte-identical. Values and tables do not depend on any third-party package.

## Level 3

Experimental reruns need the pinned toolchain of `provenance/EXTERNAL-PINS.tsv` (binaries verified by SHA-256 against
`protocols/c1-preregistration/toolchain/PINS-C1.txt` and `data/p0-feasibility/toolchain/PINS.txt`), the npm lockfiles
shipped with each harness and kit, and, for the prover analyses, the pinned base image
`node:18.20.8-bookworm-slim@sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e`.
