#!/bin/bash
# V2-C1 registered setup: circuits, Groth16 (phase 2 with one contribution + public beacon), PLONK (deterministic), verifiers.
set -u; cd ~/c1/circ
SJ="node --max-old-space-size=6000 $HOME/p0/node/node_modules/snarkjs/cli.js"; PT=$HOME/p0/research/pot16_final.ptau
CIRCOM=$HOME/p0/bin/circom-2.1.6; INC="-l $HOME/p0/node/node_modules/circomlib/circuits"
BEACON=$(printf 'V2-C1 Groth16 beacon 2026-10-04' | sha256sum | cut -c1-64)
declare -A SPEC=( [c1_k01]="v1 11" [c1_ctx_k02]="ctx 11 2" [c1_ctx_k04]="ctx 11 4" [c1_ctx_k06]="ctx 11 6" [c1_ctx_k08]="ctx 11 8" [c1_ctx_k12]="ctx 11 12" [c1_ctx_k16]="ctx 11 16" [c1_ctx_k24]="ctx 11 24" [c1_ctx_k32]="ctx 11 32" [c1_ctx_k64]="ctx 11 64" [c1_a4]="a4 11" [c1_a8]="a8 11" [c1_disc_k04]="disc 11 32 4 p16x2" )
ORDER="c1_k01 c1_ctx_k02 c1_ctx_k04 c1_ctx_k16 c1_ctx_k06 c1_ctx_k08 c1_ctx_k12 c1_ctx_k24 c1_ctx_k32 c1_a4 c1_a8 c1_disc_k04 c1_ctx_k64"
for N in ${@:-$ORDER}; do
  mkdir -p src build/$N keys/$N; python3 gen.py ${SPEC[$N]} src/$N.circom
  $CIRCOM src/$N.circom --r1cs --wasm --sym -o build/$N $INC > build/$N/circom.log 2>&1 || { echo "$N circom FAIL"; continue; }
  t0=$(date +%s)
  $SJ groth16 setup build/$N/$N.r1cs $PT keys/$N/g16_0.zkey > keys/$N/groth16-setup.log 2>&1 && \
  $SJ zkey contribute keys/$N/g16_0.zkey keys/$N/g16_1.zkey --name="C1 contribution" -e="$(head -c 64 /dev/urandom | base64)" >> keys/$N/groth16-setup.log 2>&1 && \
  $SJ zkey beacon keys/$N/g16_1.zkey keys/$N/groth16.zkey $BEACON 10 -n="C1 beacon" >> keys/$N/groth16-setup.log 2>&1 && \
  $SJ zkey verify build/$N/$N.r1cs $PT keys/$N/groth16.zkey >> keys/$N/groth16-verify.log 2>&1 && \
  $SJ zkey export verificationkey keys/$N/groth16.zkey keys/$N/groth16.vkey.json >> keys/$N/groth16-setup.log 2>&1 && \
  $SJ zkey export solidityverifier keys/$N/groth16.zkey keys/$N/groth16Verifier.sol >> keys/$N/groth16-setup.log 2>&1
  r1=$?; rm -f keys/$N/g16_0.zkey keys/$N/g16_1.zkey; t1=$(date +%s)
  $SJ plonk setup build/$N/$N.r1cs $PT keys/$N/plonk.zkey > keys/$N/plonk-setup.log 2>&1 && \
  $SJ zkey export verificationkey keys/$N/plonk.zkey keys/$N/plonk.vkey.json >> keys/$N/plonk-setup.log 2>&1 && \
  $SJ zkey export solidityverifier keys/$N/plonk.zkey keys/$N/plonkVerifier.sol >> keys/$N/plonk-setup.log 2>&1
  r2=$?; t2=$(date +%s)
  echo "$N groth16 rc=$r1 secs=$((t1-t0)) plonk rc=$r2 secs=$((t2-t1))" | tee -a ~/c1/logs/setup-summary.txt
done
echo SETUP-DONE >> ~/c1/logs/setup-summary.txt
