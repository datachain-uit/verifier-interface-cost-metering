"""V2-C1 frozen model equations (shared by the prediction generator and the registered scoring procedure).

Level 1 (accounting, all environments): see 06-model-equations.md; checked in scoring, never fitted.
Level 2/3 (structural k-model, per environment E and template b):
    Y_E,b(k) = A_E,b + B_E,b * (k - 1) + K_E * (rho_b(k) - rho_b(1))
  A, B are calibrated on the calibration cells (k in CAL_K) only; rho_b is the analytic number of keccak-f rounds
  of the verifier transcript; K_E is the per-round keccak tariff of E (0 for EVM, whose keccak is priced per word).
  For EVM the modelled quantity is calldata-normalised execution gas Y_nc = gasUsed - 16*bytes + 12*zeroBytes;
  predicted gasUsed = Y_nc + calldata gas of the actual registered transaction (known from the frozen corpus).
Level 3 regime transfer (EraVM v27): A from the v27 calibration cell at k = 1; B = B_v29 + sum over per-input
  precompile calls of (frame_v27 - frame_v29), frames measured at k = 1 in each regime.
Level 4 (ZKsync OS, conditional on the EVM opcode trace of the same proof):
    N = T_v(trace) + base + c * ncalls_b(k)       (T_v: published VM native table; base, c: two shared constants)
    G = max(G_evm, floor(N * native_price / gas_price)) with gas_price = native_price * native_per_gas
"""
import math
CAL_K = (1, 4)
GRID = [1, 2, 4, 6, 8, 12, 16, 24, 32]; LIMIT = [64]
SEEN_NOT_FITTED = {2, 16, 32}; STRICT_UNSEEN = {6, 8, 12, 24}
K_ROUND = {'evm-osaka': 0, 'evm-petersburg': 0, 'eravm-29': 40, 'eravm-27': 40, 'zkos-v32': 649 * 4 + 1250}
def rho(b, k):
    if b == 'groth16': return 0
    if b == 'plonk': return math.ceil((32 * (22 + k) + 1) / 136) + 7
    if b == 'fflonk': return math.ceil((32 * (4 + k) + 1) / 136) + 7
    raise ValueError(b)
def fit(y1, y4, env, b):
    return y1, (y4 - y1 - K_ROUND[env] * (rho(b, 4) - rho(b, 1))) / 3
def kmodel(A, B, env, b, k):
    return A + B * (k - 1) + K_ROUND[env] * (rho(b, k) - rho(b, 1))
def ncalls(b, k): return {'groth16': 2 * k + 1, 'plonk': 37, 'fflonk': 13}[b]
def zk_gas(g_evm, native, npg): return max(g_evm, native // npg)
def crossing(ks, d):
    """first k (linear interpolation between consecutive evaluation points) where d changes sign from >0 to <=0 or <0 to >=0"""
    for i in range(len(ks) - 1):
        if d[i] == 0: return float(ks[i])
        if (d[i] > 0) != (d[i + 1] > 0) and d[i + 1] != 0 or d[i + 1] == 0:
            return ks[i] + (ks[i + 1] - ks[i]) * d[i] / (d[i] - d[i + 1])
    return None
def sign_class(lo_ratio, hi_ratio):
    if lo_ratio > 1: return 'PLONK_COSTLIER'
    if hi_ratio < 1: return 'PLONK_CHEAPER'
    return 'INDETERMINATE'
