#!/bin/bash
cd ~/p0/sweep; tag=$1; prio=$2; shift 2
for c in "$@"; do for b in ${BACKENDS:-groth16 plonk}; do timeout 600 node zkos_run.js $c $b $tag $prio >> ~/p0/out/zkos-batch-$tag.log 2>&1; done; done; echo "DONE $*" >> ~/p0/out/zkos-batch-$tag.log
