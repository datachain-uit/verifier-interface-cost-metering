require('@nomicfoundation/hardhat-ethers');
// P0 feasibility EDR network (hardfork from env HF; default osaka as in V1).
const HF = process.env.HF || 'osaka';
const pre1559 = ['byzantium','constantinople','petersburg','istanbul','muirGlacier','berlin'].includes(HF);
const net = {
  hardfork: HF, chainId: 31337, blockGasLimit: 60000000, allowUnlimitedContractSize: false,
  allowBlocksWithSameTimestamp: false, initialDate: '2026-01-01T00:00:00.000Z', mining: { auto: true, interval: 0 },
  accounts: { mnemonic: 'test test test test test test test test test test test junk', path: "m/44'/60'/0'/0", count: 2, accountsBalance: '10000000000000000000000' },
  throwOnTransactionFailures: false, throwOnCallFailures: false, loggingEnabled: false,
};
if (!pre1559) net.initialBaseFeePerGas = 0;
module.exports = { solidity: '0.8.20', networks: { hardhat: net } };
