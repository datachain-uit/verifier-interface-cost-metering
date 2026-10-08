# V2-M7B-A deviations

**DEV-M7B-A-1 (method detail; before any count was computed).** The protocol assumed that EDR's step log carries
`memSize` with memory disabled. EDR 0.12.0-next.23 omits `memSize` in that mode (the registered `maxMem` field was
therefore always 0). The consistency check and the secondary count use a second deterministic re-trace of the same 18
transactions with memory enabled (`scripts/retrace_mem.js`): per step only memSize = 32 × (number of memory words) is
kept, plus a streamed sha256 over all memory words; the opcode sequence and total gas of both re-traces are checked to be
identical. The primary count (stack operands + ZKsync OS v0.4.0 resize rule) and the decision rule are unchanged.
