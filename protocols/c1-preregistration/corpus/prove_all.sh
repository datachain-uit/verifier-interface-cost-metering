#!/bin/bash
while ! grep -q SETUP-DONE ~/c1/logs/setup-summary.txt 2>/dev/null; do sleep 20; done
cd ~/c1/corpus
for r in v1 ctx_k2 ctx_k4 ctx_k16 ctx_k6 ctx_k8 ctx_k12 ctx_k24 ctx_k32 a4 a8 disc_k4 ctx_k64; do
  node --max-old-space-size=6000 prove_corpus.js $r groth16,plonk >> ~/c1/logs/prove.out 2>&1 || echo "FAIL $r" >> ~/c1/logs/prove.out
done
echo PROVE-DONE >> ~/c1/logs/prove.out
