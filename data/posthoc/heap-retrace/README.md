# V2-M7B-A — direct heap-expansion-event re-trace (post hoc mechanism confirmation)

Protocol and prediction frozen before the re-trace: `research/csi/protocols/v2/V2-M7B-heap-retrace/M7B-A-PROTOCOL.md`
(`16012294…c7b8`, 2026-10-05T01:32:38Z). Not C1 confirmatory evidence; C1, F4 and H4 unchanged. No new proof, no
ZKsync OS run, no timing.

- `scripts/retrace.js`: deterministic EDR (osaka) re-trace of proof j0 of c1_k01 and c1_ctx_k02 … k64, Groth16 and PLONK
  (18 transactions), stack enabled; raw step logs `raw/*.structlogs.json.gz`; profile `retrace-summary.json`.
- `scripts/retrace_mem.js`: same transactions with memory enabled, per-step memory size only (`raw/*.memsize.json.gz`;
  DEV-M7B-A-1).
- `scripts/m7b_a_count.py`: determinism gate (re-trace profile == registered `evm_trace`), heap-event count under the
  ZKsync OS v0.4.0 resize rule (primary) and EDR memory-size increases (secondary), consistency checks, comparison with
  the prediction; outputs `out/M7B-A-summary.json`, `out/M7B-A-per-k.csv`, `out/M7B-A-per-proof.csv`,
  `out/M7B-A-events.csv` (every expansion: step, pc, opcode, heap before / after).

Result: determinism gate 18 / 18; 9 / 9 MATCH (observed PLONK − Groth16 = 22, 22, 24, 24, 28, 32, 40, 48, 80);
Groth16 7 events at every k; PLONK 29 … 87; ZKsync OS rule count = EVM expansion count for every proof (no opcode with
two expanding resizes); replayed heap size = EDR memory size at every step; final heap = M7A heap words; after
subtracting 35 × observed events the M7A remainder is one constant (1,669,012) for all 18 proofs. Verdict CONFIRMED.
