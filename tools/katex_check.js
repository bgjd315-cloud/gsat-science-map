// Parse every $…$ segment and formula field in detail2 / formula_cards JSON with KaTeX.
// Usage: node tools/katex_check.js tools/detail2/*.json tools/formula_cards.json
// Needs KaTeX 0.16.9: npm install katex@0.16.9 (here or in a folder given by KATEX_DIR).
const fs = require("fs"), path = require("path");
let katex;
try { katex = require(process.env.KATEX_DIR ? path.join(process.env.KATEX_DIR, "node_modules", "katex") : "katex"); }
catch (e) { console.error("找不到 katex：請先 npm install katex@0.16.9，或設定 KATEX_DIR"); process.exit(2); }

const errs = [];
function tryTex(tex, where) {
  try { katex.renderToString(tex, { output: "mathml", throwOnError: true, strict: "ignore" }); }
  catch (e) { errs.push(`${where}: ${String(e.message).replace(/^KaTeX parse error: /, "")} → ${tex.slice(0, 70)}`); }
}
function text(s, where) {
  if (typeof s !== "string" || !s) return;
  const parts = s.split("$");
  if (parts.length % 2 === 0) { errs.push(`${where}: $ 沒有成對`); return; }
  for (let i = 1; i < parts.length; i += 2) tryTex(parts[i], where);
}
function entry(x, tag) {
  ["idea", "answer", "approx", "check", "takeaway"].forEach(k => text(x[k], `${tag}.${k}`));
  (x.formulas || []).forEach((f, i) => {
    if (f.tex) tryTex(f.tex, `${tag}.formulas[${i}].tex`); text(f.name, `${tag}.formulas[${i}].name`); text(f.cond, `${tag}.formulas[${i}].cond`); text(f.text, `${tag}.formulas[${i}].text`);
    (f.vars || []).forEach((v, j) => { tryTex(String(v[0] || ""), `${tag}.formulas[${i}].vars[${j}]`); text(v[1], `${tag}.formulas[${i}].vars[${j}]`); });
  });
  (x.steps || []).forEach((s, i) => { text(s.q, `${tag}.steps[${i}].q`); text(s.why, `${tag}.steps[${i}].why`); (s.calc || []).forEach((c, j) => text(c, `${tag}.steps[${i}].calc[${j}]`)); });
  (x.wrong || []).forEach((w, i) => text(w.how, `${tag}.wrong[${i}]`));
  (x.tiers || []).forEach((t, i) => text(t[1], `${tag}.tiers[${i}]`));
}
for (const f of process.argv.slice(2)) {
  const j = JSON.parse(fs.readFileSync(f, "utf8"));
  if (Array.isArray(j)) j.forEach(x => entry(x, `${x.exam}${x.year}-${x.no}`));
  else for (const [u, cards] of Object.entries(j)) cards.forEach((c, i) => { tryTex(c.tex || "", `${u}[${i}] ${c.name}`); text(c.note, `${u}[${i}].note`); });
}
errs.forEach(e => console.log(e));
console.log(`KaTeX 解析錯誤共 ${errs.length} 個`);
process.exit(errs.length ? 1 : 0);
