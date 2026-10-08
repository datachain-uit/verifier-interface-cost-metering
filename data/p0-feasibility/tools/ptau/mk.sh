#!/bin/bash
# Local feasibility ptau (single contribution + beacon). NOT a production ceremony.
P=$1; SJ="node --max-old-space-size=6000 $HOME/p0/node/node_modules/snarkjs/cli.js"; cd ~/p0/ptau
t0=$(date +%s)
$SJ powersoftau new bn128 $P p${P}_0.ptau > log$P.txt 2>&1
$SJ powersoftau contribute p${P}_0.ptau p${P}_1.ptau --name=p0 -e="p0 feasibility $(date)" >> log$P.txt 2>&1
$SJ powersoftau beacon p${P}_1.ptau p${P}_b.ptau 0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f 10 -n=beacon >> log$P.txt 2>&1
$SJ powersoftau prepare phase2 p${P}_b.ptau pot${P}_local.ptau >> log$P.txt 2>&1
echo "done p$P rc=$? secs=$(( $(date +%s)-t0 ))" >> log$P.txt
