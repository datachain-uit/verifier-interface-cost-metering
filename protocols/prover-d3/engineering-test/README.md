Engineering test only: `synthetic_test.py` builds SYNTHETIC tables with the real column schema (random values; no real
measurement is read) and runs `d3_reanalysis.py` on them, including an injected reconciliation mismatch that must be
reported. It was run in the cloud working copy before the freeze (B = 500 and B = 10,000). Its outputs are not evidence.
