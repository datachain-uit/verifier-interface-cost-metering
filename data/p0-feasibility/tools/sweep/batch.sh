#!/bin/bash
# usage: batch.sh <arm> <regime> <circuit:foreign>...
cd ~/p0/sweep; arm=$1; reg=$2; shift 2
for cf in "$@"; do c=${cf%%:*}; f=${cf#*:}; [ "$f" = "$c" ] && f=""
  for b in ${BACKENDS:-groth16 plonk}; do FOREIGN=$f timeout 900 node run.js $arm $c $b $reg >> ~/p0/out/batch-$arm-$reg.log 2>&1; done; done
echo "DONE $arm $reg $*" >> ~/p0/out/batch-$arm-$reg.log
