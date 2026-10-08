#!/bin/bash
# Fresh local ZKsync OS (v0.23.0 server, protocol v31.0 local chain) + fresh L1 anvil 1.5.1. Env: NPG (native_per_gas), NATIVE_PRICE, PUBDATA_PRICE, TAG
set -u; cd ~/p0/zkos
for p in $(pgrep -x zksync-os-serve) $(pgrep -x anvil); do kill $p 2>/dev/null; done; sleep 2
for p in $(pgrep -x zksync-os-serve) $(pgrep -x anvil); do kill -9 $p 2>/dev/null; done
TAG=${TAG:-run}; mkdir -p run/$TAG
~/p0/bin/foundry151/anvil --load-state run/l1-state-v31.json --port 8545 --block-time 0.25 --mixed-mining --slots-in-an-epoch 10 > run/$TAG/anvil.log 2>&1 &
for i in $(seq 1 60); do curl -s -m 2 localhost:8545 -X POST -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' >/dev/null 2>&1 && break; sleep 1; done
cd src && env RUST_LOG="info,zksync_os_sequencer::execution::execute_block_in_vm=debug" NO_COLOR=1 general_ephemeral=true \
  fee_native_per_gas=${NPG:-100} fee_native_price_override=${NATIVE_PRICE:-0xf4240} fee_pubdata_price_override=${PUBDATA_PRICE:-0x0} \
  observability_log_use_color=false \
  ~/p0/bin/zkos/zksync-os-server --config ./local-chains/local_dev.yaml --config ./local-chains/v31.0/default/config.yaml > ../run/$TAG/server.log 2>&1 &
for i in $(seq 1 120); do r=$(curl -s -m 2 localhost:3050 -X POST -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null); [ -n "$r" ] && echo "$r" | grep -q result && break; sleep 1; done
sleep 5; echo "started $TAG: $r"
