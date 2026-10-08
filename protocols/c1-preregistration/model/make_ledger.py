#!/usr/bin/env python3
# Builds 07-parameter-ledger.csv from static spec/source rows and the fitted values written by c1_predict.py.
import csv, json, os, sys
PKG = sys.argv[1]; F = json.load(open(os.path.join(PKG, '09-numeric-predictions', 'fitted_parameters_and_tolerances.json')))
P, T = F['parameters'], F['tolerances']; rows = []
def R(symbol, meaning, env, dep_b, dep_k, source_type, source, cal_cells, fitted, held_out_use, value, uncertainty, notes=''):
    rows.append(dict(symbol=symbol, meaning=meaning, environment=env, depends_on_backend=dep_b, depends_on_k=dep_k, source_type=source_type, source=source,
                     calibration_cells=cal_cells, fitted=fitted, used_for_held_out=held_out_use, value_P=value, uncertainty=uncertainty, notes=notes))
# template structure
R('n_ecMul(b,k)', 'ecMul precompile calls per verification', 'all', 'yes', 'G16 only', 'analytic (template)', 'snarkjs 0.7.5 verifier templates (hashes in PINS-C1)', '-', 'no', 'yes', 'G16: k; PLONK: 18; FFLONK: 5', 'exact; checked by L1-STRUCT')
R('n_ecAdd(b,k)', 'ecAdd precompile calls', 'all', 'yes', 'G16 only', 'analytic (template)', 'same', '-', 'no', 'yes', 'G16: k; PLONK: 18; FFLONK: 7', 'exact; checked')
R('n_pair(b)', 'pairing pairs (one call)', 'all', 'yes', 'no', 'analytic (template)', 'same', '-', 'no', 'yes', 'G16: 4; PLONK: 2; FFLONK: 2', 'exact; checked')
R('rho_b(k)', 'keccak-f rounds of the verifier transcript', 'all', 'yes', 'yes (PLONK, FFLONK)', 'analytic (template)', 'PLONK ceil((32(22+k)+1)/136)+7; FFLONK ceil((32(4+k)+1)/136)+7; G16 0', '-', 'no', 'yes', 'see formula', 'exact; checked against every P0 trace and by AC-STRUCT-EVM-transcript-rounds')
R('ncalls_b(k)', 'precompile calls per verification', 'zkos', 'yes', 'G16 only', 'analytic (template)', 'G16 2k+1; PLONK 37; FFLONK 13', '-', 'no', 'yes', 'see formula', 'exact')
R('cd(b,k,j)', 'calldata bytes / zero bytes of each registered transaction', 'EVM-type', 'yes', 'yes', 'analytic (frozen corpus)', 'corpus/corpus-calldata.json', '-', 'no', 'yes', 'per proof', 'exact')
# EVM schedule
for sym, mean, val, src in [('G_tx', 'intrinsic transaction gas', '21000', 'Yellow Paper'), ('G_cd', 'calldata gas per non-zero / zero byte', 'Osaka 16 / 4; Petersburg 68 / 4', 'EIP-2028'),
                            ('G_ecAdd', 'ecAdd precompile gas', 'Osaka 150; Petersburg 500', 'EIP-1108 / EIP-196'), ('G_ecMul', 'ecMul precompile gas', 'Osaka 6000; Petersburg 40000', 'EIP-1108 / EIP-196'),
                            ('G_pair', 'pairing gas', 'Osaka 45000 + 34000/pair; Petersburg 100000 + 80000/pair', 'EIP-1108 / EIP-197'), ('G_keccak', 'keccak gas', '30 + 6/word', 'Yellow Paper')]:
    R(sym, mean, 'evm-osaka / evm-petersburg', 'no', 'no', 'spec', src, '-', 'no', 'yes (Level 1 + decomposition)', val, 'exact')
# Level 2/3 calibrated
for key, v in P.items():
    env, b, m = key.split('|')
    if env == 'zkos-v32' and b == 'shared':
        R('base_zk', 'per-transaction native not visible in the opcode trace', 'zkos-v32', 'no (shared)', 'no', 'smoke-calibrated (P); registered-calibrated (R)', v['source'], 'P: smoke v32c c1-equivalent k=1 G16+PLONK proof j0; R: registered c1_k01 G16+PLONK, j0..j7, npg100', 'yes', 'yes (all held-out ZKsync OS cells, FFLONK)', round(v['base']), 'exactly identified (2 eq., 2 unknowns)')
        R('c_zk', 'per precompile-call native not in the opcode table', 'zkos-v32', 'no (shared)', 'no', 'smoke-calibrated (P); registered-calibrated (R)', v['source'], 'same as base_zk', 'yes', 'yes', round(v['per_call'], 1), 'exactly identified')
        continue
    t = T.get(f'{env}|{b}|{m}', {}); tau = t.get('tau_noise', 0) + t.get('tau_struct', 0)
    cal = 'P0 k=1 and k=4 cells (P); registered k=1 and k=4 cells (R)' if env != 'eravm-27' else 'A: v27 k=1 cell; B: v29 B + v27-v29 per-call frame difference at k=1'
    if env == 'zkos-v32': cal = 'trace-model natives at k=1,4 (P0 traces x v0.4.0 + smoke constants); P only'
    R(f'A[{env},{b},{m}]', 'cost at k=1', env, 'yes', 'no', 'P0-calibrated' if env != 'zkos-v32' else 'derived (trace model)', v['source'], cal, 'yes', 'yes', round(v['A'], 1), f'tau={tau:.6f} (rel.)')
    R(f'B[{env},{b},{m}]', 'per-input increment', env, 'yes', 'no (slope)', 'P0-calibrated' if env != 'zkos-v32' else 'derived (trace model)', v['source'], cal, 'yes', 'yes', round(v['B'], 2), f'tau={tau:.6f} (rel., on Y)')
for env, val in (('eravm-29', '40'), ('eravm-27', '40'), ('zkos-v32', '3846 (=649*4+1250)')):
    R(f'K[{env}]', 'tariff per keccak-f round', env, 'no', 'no', 'P0-measured (EraVM frames 119+40/round)' if 'eravm' in env else 'source (v0.4.0)', 'eravm-frames.json' if 'eravm' in env else 'zksync-os v0.4.0 cost_constants.rs', '-', 'no', 'yes', val, 'exact')
R('K[evm]', 'tariff per keccak-f round', 'evm', 'no', 'no', 'spec', 'EVM prices keccak per word (in B)', '-', 'no', 'yes', '0', 'exact')
for sym, val in (('frame_ecAdd', 'v29 301; v27 28415'), ('frame_ecMul', 'v29 5496; v27 277372'), ('frame_pair', 'v29 4-pair 320954, 2-pair 160570; v27 4-pair 8244592, 2-pair 4787334')):
    R(sym, 'EraVM per-call precompile frame cost (callTracer)', 'eravm-29 / eravm-27', 'no', 'no', 'P0-measured (P); registered k=1 frames (R)', 'P0 eravm-frames.json, k=1', 'k=1 cells', 'no (measured)', 'yes (v27 transfer, decomposition)', val, 'v27 ecMul scalar-dependent (see tau v27)')
# ZKsync OS published constants
for sym, val in (('N_ecAdd', '58000 (=51400+1650*4)'), ('N_ecMul', '811000 (=647000+41000*4)'), ('N_pair', '6244000 + 6908000/pair (=5572000+334000*4)'), ('N_keccak', '1150 + 3846/round'), ('N_copy', '80 + 2/byte'), ('N_step', '20 per opcode'), ('N_op(op)', 'native_resource_constants.rs table')):
    R(sym, 'ZKsync OS VM v0.4.0 native price', 'zkos-v32', 'no', 'no', 'source code', 'zksync-os v0.4.0 @ 69bc4305 (toolchain/zksync-os-v0.4.0-*.rs)', '-', 'no', 'yes', val, 'exact (published); model adequacy covered by tau_cond')
for sym, val, note in (('npg', '100 default; intervention levels in 11-zksync-os-npg-levels.csv', 'operator config (factor)'), ('p_native', '0xf4240 (1e6 wei)', 'fixed override'), ('p_pubdata', '0', 'fixed override')):
    R(sym, 'ZKsync OS fee parameter', 'zkos-v32', 'no', 'no', 'configuration', 'server env', '-', 'no', 'yes', val, 'exact', note)
# tolerances
for key, t in T.items():
    R(f'tau[{key}]', 'pre-registered relative tolerance (noise + structural)', key.split('|')[0], 'yes', 'no', 'P0-derived', t.get('basis_noise', '') + ' | ' + t.get('basis_struct', ''), 'P0 cells at k in {2,16,32} (struct) and within-cell ranges (noise); never registered data', 'no', 'criterion', round(t['tau_noise'] + t['tau_struct'], 6), '-')
    if 'tau_cond' in t: R(f'tau_cond[{key}]', 'conditional-model tolerance (ZC test)', 'zkos-v32', 'yes', 'no', 'P0-derived (v31 transfer)', t['basis_cond'], 'P0 v31 cells', 'no', 'criterion', round(t['tau_cond'], 6), '-')
w = csv.DictWriter(open(os.path.join(PKG, '07-parameter-ledger.csv'), 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows); print(len(rows))
