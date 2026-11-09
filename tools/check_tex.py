"""Static checks for detail2 JSON files (see DETAIL_BRIEF.md).

Usage: python -I tools/check_tex.py tools/detail2/A115.json [more files...]
Prints one line per problem and a total; exit code 1 if any problem.
"""
import json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
UNI = set("√∛½⅓¼¾²³⁰¹⁴⁵⁶⁷⁸⁹⁻⁺₀₁₂₃₄₅₆₇₈₉→⇒⇔⇌⇄≤≥≠≈×÷±∓πθαβγδελμνρστφωΔΩΣΦΨΛΓ∠△⊥∥∞∫∑Σ∏·∈∉⊂⊆∪∩°′″℃")
TEXT_KEYS = ("idea", "answer", "approx", "check", "takeaway")

def split_math(s):
    """Return (outside_text, [math_segments]) or None if $ unbalanced."""
    parts = s.split("$")
    if len(parts) % 2 == 0:
        return None
    return "".join(parts[0::2]), parts[1::2]

def strip_allowed_slash(m):
    m = re.sub(r"\\text\{[^{}]*\}", "", m)
    # exponent groups ^{...} (one nesting level)
    m = re.sub(r"\^\{(?:[^{}]|\{[^{}]*\})*\}", "", m)
    return m

CTRL = re.compile(r"[\x00-\x1f]")  # includes \n: a non-raw "\ne" or "\nabla" turns into a newline

def check_ctrl(s, where, errs):
    if isinstance(s, str) and CTRL.search(s):
        errs.append(f"{where}: 含控制字元（多半是 Python 非 raw 字串把 \\t、\\f、\\r、\\b 吃掉了，例如 \\times、\\frac、\\right、\\begin）→ {s[:60]!r}")

def check_text(s, where, errs):
    if not isinstance(s, str):
        errs.append(f"{where}: 不是字串"); return
    check_ctrl(s, where, errs)
    sp = split_math(s)
    if sp is None:
        errs.append(f"{where}: $ 沒有成對 → {s[:60]}"); return
    out, maths = sp
    bad = sorted({c for c in out if c in UNI})
    if bad:
        errs.append(f"{where}: $…$ 外有數學符號 {''.join(bad)} → {s[:60]}")
    if re.search(r"(?<![A-Za-z])[0-9A-Za-z)\]]\s*/\s*[0-9A-Za-z(\[]", out) and "http" not in out:
        errs.append(f"{where}: $…$ 外有橫式分數 → {s[:60]}")
    for m in maths:
        check_math(m, where, errs)

def check_math(m, where, errs):
    check_ctrl(m, where, errs)
    if "/" in strip_allowed_slash(m):
        errs.append(f"{where}: $…$ 內有斜線（改用 \\dfrac）→ {m[:60]}")
    if "\\binom" in m:
        errs.append(f"{where}: 不用 \\binom，改用 C^n_r → {m[:60]}")
    if re.search(r"\\frac(?![a-z])", m):
        errs.append(f"{where}: 用 \\dfrac 取代 \\frac → {m[:60]}")
    bad = sorted({c for c in m if c in UNI})
    if bad:
        errs.append(f"{where}: $…$ 內有 Unicode 符號 {''.join(bad)}（改用 TeX 指令）→ {m[:60]}")

def check_entry(x, tag, errs):
    for k in ("exam", "year", "no", "idea", "steps", "answer"):
        if k not in x:
            errs.append(f"{tag}: 缺少欄位 {k}")
    for k in TEXT_KEYS:
        if k in x and x[k]:
            check_text(x[k], f"{tag}.{k}", errs)
    for i, f in enumerate(x.get("formulas", []) or []):
        w = f"{tag}.formulas[{i}]"
        if "$" in str(f.get("tex", "")):
            errs.append(f"{w}.tex: tex 欄不要含 $")
        check_math(str(f.get("tex", "")), w + ".tex", errs)
        check_text(str(f.get("name", "")), w + ".name", errs)
        for j, v in enumerate(f.get("vars", []) or []):
            if not (isinstance(v, (list, tuple)) and len(v) == 2):
                errs.append(f"{w}.vars[{j}]: 要是 [符號, 意義]"); continue
            if "$" in str(v[0]):
                errs.append(f"{w}.vars[{j}][0]: 符號欄不要含 $")
            check_math(str(v[0]), f"{w}.vars[{j}][0]", errs)
            check_text(str(v[1]), f"{w}.vars[{j}][1]", errs)
        if f.get("cond"):
            check_text(f["cond"], w + ".cond", errs)
        if f.get("text"):
            check_text(f["text"], w + ".text", errs)
        if not f.get("tex") and not f.get("text"):
            errs.append(f"{w}: 公式框要有 tex 或 text")
    steps = x.get("steps", []) or []
    if not steps:
        errs.append(f"{tag}: steps 是空的")
    for i, s in enumerate(steps):
        w = f"{tag}.steps[{i}]"
        check_text(str(s.get("q", "")), w + ".q", errs)
        if s.get("why"):
            check_text(s["why"], w + ".why", errs)
        calc = s.get("calc")
        if not isinstance(calc, list) or not calc:
            errs.append(f"{w}.calc: 要是非空的字串陣列"); continue
        for j, line in enumerate(calc):
            check_text(line, f"{w}.calc[{j}]", errs)
            if isinstance(line, str) and re.match(r"^\s*答[\s　:：]", line):
                errs.append(f"{w}.calc[{j}]: calc 內不要寫「答」")
    for i, wv in enumerate(x.get("wrong", []) or []):
        check_text(str(wv.get("how", "")), f"{tag}.wrong[{i}].how", errs)
    for i, t in enumerate(x.get("tiers", []) or []):
        if not (isinstance(t, (list, tuple)) and len(t) == 2):
            errs.append(f"{tag}.tiers[{i}]: 要是 [項目, 說明]"); continue
        check_text(str(t[1]), f"{tag}.tiers[{i}]", errs)
        if "級分" in str(t) or "學測" in str(t):
            errs.append(f"{tag}.tiers[{i}]: 分科分項說明不得出現「級分」「學測」")

def main(paths):
    errs = []
    for p in paths:
        try:
            arr = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            errs.append(f"{p}: 讀不到 JSON（{e}）"); continue
        for x in arr:
            check_entry(x, f"{x.get('exam')}{x.get('year')}-{x.get('no')}", errs)
    for e in errs:
        print(e)
    print(f"共 {len(errs)} 個問題")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
