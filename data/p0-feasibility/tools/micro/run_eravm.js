const fs = require('fs'); const HOME = process.env.HOME;
const { ethers } = require(HOME + '/p0/node/node_modules/ethers'); const E = require(HOME + '/p0/lib/eravm');
(async () => {
  const proto = Number(process.argv[2] || 29); const M = JSON.parse(fs.readFileSync(HOME + '/p0/micro/Micro.zk.json')); const I = new ethers.Interface(M.abi);
  const node = await E.start({ protocol: proto, port: 18800, logFile: `/tmp/micro-${proto}.log` }); const res = { proto, rows: [] };
  try {
    const s = await E.session(node); const d = await s.tx({ create: M, gasLimit: 400000000n }); res.deploy = d;
    const fnames = M.abi.filter((f) => f.type === 'function').map((f) => f.name);
    const X = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdefn, Y = 0x0fedcba987654321fedcba987654321fedcba987654321fedcba9876543210n;
    for (let rep = 0; rep < 2; rep++) for (const fn of fnames) {
      const args = fn === 'inv' ? [[X, 3n, 12345678901234567890n][rep % 3], 0n] : [X, Y];
      const t = await s.tx({ to: d.contractAddress, data: I.encodeFunctionData(fn, args), trace: rep === 0 && /ec|pair|keccak|nop|inv/.test(fn) });
      const c = await s.call(d.contractAddress, I.encodeFunctionData(fn, args));
      res.rows.push({ fn, rep, args: args.map(String), ...t, ret: c.ok ? c.ret : c.err });
    }
    for (const xv of [X, 3n, 12345678901234567890n, 0xabcdef0123456789abcdef0123456789abcdef0123456789abcdef01234567n, 987654321987654321987654321n])
      res.rows.push({ fn: 'inv', rep: 9, args: [String(xv)], ...(await s.tx({ to: d.contractAddress, data: I.encodeFunctionData('inv', [xv, 0n]) })), ret: (await s.call(d.contractAddress, I.encodeFunctionData('inv', [xv, 0n]))).ret });
    await new Promise((r) => setTimeout(r, 500));
  } finally { await node.stop(); }
  const fee = E.feeRecords(node); for (const r of res.rows) Object.assign(r, fee.get(r.hash) || {}); Object.assign(res.deploy, fee.get(res.deploy.hash) || {});
  fs.writeFileSync(HOME + `/p0/out/micro-eravm-${proto}.json`, JSON.stringify(res, null, 1));
  for (const r of res.rows.filter((x) => x.rep !== 1)) console.log(r.fn, r.rep, r.status, r.computational_gas, r.ret && String(r.ret).slice(0, 20));
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
