// Exact-match patcher: node patch.js <target> <patchfile.js>
// The patch file exports an array of [oldString, newString] pairs; each old
// string must occur exactly once in the target (fails loudly otherwise).
const fs = require('fs'), path = require('path');
const [target, patchFile] = process.argv.slice(2);
let s = fs.readFileSync(target, 'utf8');
const pairs = require(path.resolve(patchFile));
for (const [a, b] of pairs) {
  const n = s.split(a).length - 1;
  if (n !== 1) { console.error(`patch failed (${n} matches): ${a.slice(0, 90)}`); process.exit(1); }
  s = s.replace(a, () => b);
}
fs.writeFileSync(target, s);
console.log(`applied ${pairs.length} edits to ${target}`);
