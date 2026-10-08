#!/bin/bash
# V2-C1 harness: fresh local ZKsync OS v32.0 (server v0.23.0) + fresh L1 (anvil 1.5.1, state decompressed from the pinned v32.0 gz) per cell.
# usage: zkos_node.sh <rundir> <npg>     (native price 0xf4240, pubdata price 0, ephemeral DB; DEBUG native line enabled)
set -u; D=$1; NPG=$2; SRC=$HOME/p0/zkos/src
for p in $(pgrep -x zksync-os-serve) $(pgrep -x anvil); do kill $p 2>/dev/null; done; sleep 2
for p in $(pgrep -x zksync-os-serve) $(pgrep -x anvil); do kill -9 $p 2>/dev/null; done; sleep 1
mkdir -p $D; gzip -dc $SRC/local-chains/v32.0/l1-state.json.gz > $D/l1-state.json
$HOME/p0/bin/foundry151/anvil --load-state $D/l1-state.json --port 8545 --block-time 0.25 --mixed-mining --slots-in-an-epoch 10 > $D/anvil.log 2>&1 &
for i in $(seq 1 60); do curl -s -m 2 localhost:8545 -X POST -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' >/dev/null 2>&1 && break; sleep 1; done
cd $SRC && env RUST_LOG="info,zksync_os_sequencer::execution::execute_block_in_vm=debug" NO_COLOR=1 general_ephemeral=true \
  fee_native_per_gas=$NPG fee_native_price_override=0xf4240 fee_pubdata_price_override=0x0 observability_log_use_color=false \
  $HOME/p0/bin/zkos/zksync-os-server --config ./local-chains/local_dev.yaml --config ./local-chains/v32.0/default/config.yaml > $D/server.log 2>&1 &
r=""; for i in $(seq 1 180); do r=$(curl -s -m 2 localhost:3050 -X POST -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null); [ -n "$r" ] && echo "$r" | grep -q result && break; sleep 1; done
sleep 5; echo "$r" | grep -q result && echo "ZKOS-UP npg=$NPG" || { echo "ZKOS-START-FAILED"; exit 3; }
