#!/bin/bash
for p in $(pgrep -x zksync-os-serve) $(pgrep -x anvil); do kill $p 2>/dev/null; done; sleep 2
for p in $(pgrep -x zksync-os-serve) $(pgrep -x anvil); do kill -9 $p 2>/dev/null; done; exit 0
