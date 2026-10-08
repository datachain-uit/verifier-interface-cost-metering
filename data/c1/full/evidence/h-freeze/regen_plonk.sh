#!/bin/bash
# Pilot step 1: regenerate the deterministic PLONK proving keys from the FROZEN C1 sources and compare with circuits/CIRCUITS.csv.
set -u; PKG=$HOME/c1/pkg; W=$HOME/full/regen; cd $W
SJ="node --max-old-space-size=6000 $HOME/p0/node/node_modules/snarkjs/cli.js"; PT=$HOME/p0/research/pot16_final.ptau
echo "pot16 $(sha256sum $PT | cut -c1-64) expected 4a64b121623021d5bcb19eee0a716d50ecb936e04b2cd021e71e74a86441439e"
python3 - > expected.tsv <<PY
import csv
for r in csv.DictReader(open('$PKG/circuits/CIRCUITS.csv')): print(r['circuit'], r['r1cs_sha256'], r['plonk_zkey_sha256'], r['plonk_vkey_sha256'], r['plonk_verifier_sol_sha256'], sep='\t')
PY
while IFS=$'\t' read N R1 PZ PV PS; do
  mkdir -p b/$N; $HOME/p0/bin/circom-2.1.6 $PKG/circuits/src/$N.circom --r1cs -o b/$N -l $HOME/p0/node/node_modules/circomlib/circuits > b/$N/circom.log 2>&1
  r1=$(sha256sum b/$N/$N.r1cs | cut -c1-64)
  $SJ plonk setup b/$N/$N.r1cs $PT b/$N/plonk.zkey > b/$N/setup.log 2>&1
  pz=$(sha256sum b/$N/plonk.zkey | cut -c1-64)
  $SJ zkey export verificationkey b/$N/plonk.zkey b/$N/plonk.vkey.json >> b/$N/setup.log 2>&1; $SJ zkey export solidityverifier b/$N/plonk.zkey b/$N/plonkVerifier.sol >> b/$N/setup.log 2>&1
  pv=$(sha256sum b/$N/plonk.vkey.json | cut -c1-64); ps=$(sha256sum b/$N/plonkVerifier.sol | cut -c1-64)
  ok=MATCH; [ "$r1" = "$R1" ] && [ "$pz" = "$PZ" ] && [ "$pv" = "$PV" ] && [ "$ps" = "$PS" ] || ok=MISMATCH
  echo -e "$N\tr1cs=$r1\tplonk_zkey=$pz\tvkey=$pv\tsol=$ps\t$ok" | tee -a regen-result.tsv
  rm -f b/$N/plonk.zkey
done < expected.tsv
echo REGEN-DONE >> regen-result.tsv
