"""
Experiment 7 - Static accessibility and interaction audit of the React frontend
against WCAG 2.1 Level A/AA success criteria.

This is an automated inspection of source code. It involves no participants and
is NOT a substitute for user acceptance testing; it is reported as an
inspection-based evaluation of a kind that can be performed without human
subjects, and its limits are stated in the manuscript.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import re, glob, os, json, collections

SRC = glob.glob(paths.FRONTEND_SRC, recursive=True)
SRC = [f for f in SRC if 'node_modules' not in f]
print(f"React source files audited: {len(SRC)}")

checks = collections.Counter()
detail = collections.defaultdict(list)

RX = {
 # (criterion, regex to find violations)
 '1.1.1 Non-text content: <img> without alt':      re.compile(r'<img(?![^>]*\balt\s*=)[^>]*>'),
 '1.3.1 Info & relationships: <input> without id/aria-label':
        re.compile(r'<input(?![^>]*(?:aria-label|aria-labelledby|\bid\s*=))[^>]*>'),
 '1.3.1 Info & relationships: <select> without label':
        re.compile(r'<select(?![^>]*(?:aria-label|aria-labelledby|\bid\s*=))[^>]*>'),
 '2.1.1 Keyboard: onClick on non-interactive element':
        re.compile(r'<(div|span|li|td|tr)\b(?=[^>]*onClick)(?![^>]*(?:role\s*=|onKeyDown|onKeyPress|tabIndex))[^>]*>'),
 '4.1.2 Name/role/value: <button> with no text or aria-label':
        re.compile(r'<button(?![^>]*aria-label)[^>]*>\s*(?:<[^>]+/>\s*)?</button>'),
 '2.4.4 Link purpose: <a> without href':           re.compile(r'<a(?![^>]*\bhref)[^>]*>'),
}

total_elems = collections.Counter()
ELEM = {'<img': re.compile(r'<img\b'), '<input': re.compile(r'<input\b'),
        '<select': re.compile(r'<select\b'), '<button': re.compile(r'<button\b'),
        '<a': re.compile(r'<a\b')}

for f in SRC:
    try:
        s = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for k, rx in ELEM.items():
        total_elems[k] += len(rx.findall(s))
    for crit, rx in RX.items():
        hits = rx.findall(s)
        if hits:
            checks[crit] += len(hits)
            detail[crit].append((os.path.relpath(f, paths.REPO), len(hits)))

print("\nElement inventory: " + ', '.join(f"{k}={v}" for k, v in total_elems.items()))
print("\n" + "=" * 78)
print("WCAG 2.1 STATIC AUDIT RESULTS")
print("=" * 78)
for crit in RX:
    n = checks[crit]
    print(f"\n{crit}\n   violations: {n}")
    for fn, c in sorted(detail[crit], key=lambda t: -t[1])[:4]:
        print(f"      {c:3d}  {fn}")

# extra checks
alt_ratio = None
if total_elems['<img']:
    alt_ratio = 1 - checks['1.1.1 Non-text content: <img> without alt'] / total_elems['<img']
inp_ratio = None
if total_elems['<input']:
    inp_ratio = 1 - checks['1.3.1 Info & relationships: <input> without id/aria-label'] / total_elems['<input']

print("\n" + "-" * 78)
print(f"images with alt text        : "
      f"{alt_ratio:.1%}" if alt_ratio is not None else "no <img> elements")
print(f"inputs with a programmatic label: "
      f"{inp_ratio:.1%}" if inp_ratio is not None else "no <input> elements")
print(f"total Level A/AA violations : {sum(checks.values())}")
print(f"files containing >=1 violation: "
      f"{len({fn for v in detail.values() for fn, _ in v})}/{len(SRC)}")

json.dump(dict(files=len(SRC), elements=dict(total_elems),
               violations={k: checks[k] for k in RX},
               total_violations=sum(checks.values()),
               alt_ratio=alt_ratio, input_label_ratio=inp_ratio),
          open(paths.out('a11y.json'), 'w', encoding='utf-8'), indent=2)
print("\nsaved a11y.json")
