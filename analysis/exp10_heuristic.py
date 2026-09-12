"""
Experiment 10 - Inspection-based usability evaluation of the React frontend
against Nielsen's ten usability heuristics.

Heuristic evaluation is a discount usability method designed for situations in
which user testing is not available. It is normally conducted by expert raters
assigning severity scores, which is a subjective judgement. To avoid that
subjectivity, and because the authors are not disinterested evaluators of their
own interface, this implementation is evidence-based: each heuristic is operationalised
as the presence or absence of specific, detectable interface affordances in the
source, counted automatically. The result is therefore a structured conformance
audit against Nielsen's framework, not an expert severity rating, and it is
reported as such.

Detection is lexical and therefore conservative in both directions: an affordance
implemented under an unusual name will be missed, and a matching token inside a
comment will be counted. Counts should be read as indicative of coverage across
screens, not as exact.
"""
import os, re, sys, glob, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SRC = sorted(glob.glob(paths.FRONTEND_SRC, recursive=True))
SRC = [f for f in SRC if 'node_modules' not in f and not f.endswith('.test.js')]

# heuristic -> (label, regex for the affordance that evidences it)
H = [
 ("H1  Visibility of system status",
  r'\b(isLoading|loading|Spinner|progress|Loading\.\.\.)\b'),
 ("H2  Match with the real world",
  r'\b(placeholder\s*=)'),
 ("H3  User control and freedom",
  r'\b(onCancel|Cancel|goBack|handleBack|navigate\(-1\))\b'),
 ("H4  Consistency and standards",
  r'\b(className\s*=\s*["\'][^"\']*btn|Navbar|Footer)\b'),
 ("H5  Error prevention",
  r'\b(required\b|validate|validation|window\.confirm|disabled\s*=)'),
 ("H6  Recognition rather than recall",
  r'\b(label\s*=|<label|title\s*=)'),
 ("H7  Flexibility and efficiency",
  r'\b(onKeyDown|onKeyPress|shortcut|accessKey)\b'),
 ("H8  Aesthetic and minimalist design", None),          # not lexically detectable
 ("H9  Help users recover from errors",
  r'\b(setError|errorMessage|error\s*&&|catch\s*\()'),
 ("H10 Help and documentation",
  r'\b(help|Help|tooltip|Tooltip|instructions|guide)\b'),
]

rows = []
print("=" * 76)
print("HEURISTIC CONFORMANCE AUDIT  (Nielsen's ten heuristics)")
print("=" * 76)
print(f"React source files audited: {len(SRC)}\n")
print(f"{'heuristic':<40}{'files with evidence':>21}{'coverage':>12}")

texts = {}
for f in SRC:
    try:
        texts[f] = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        pass

for label, rx in H:
    if rx is None:
        print(f"{label:<40}{'not lexically detectable':>21}{'-':>12}")
        rows.append(dict(heuristic=label, files=None, coverage=None,
                         note='not assessable by code inspection'))
        continue
    hits = [f for f, s in texts.items() if re.search(rx, s)]
    cov = len(hits) / len(texts) if texts else 0
    print(f"{label:<40}{len(hits):>21}{cov:>11.1%}")
    rows.append(dict(heuristic=label, files=len(hits), coverage=cov))

# screens with NO status feedback at all: the most consequential single gap
status_rx = re.compile(r'\b(isLoading|loading|Spinner|progress)\b')
async_rx = re.compile(r'\b(fetch\(|axios\.|await\s)')
blind = [os.path.basename(f) for f, s in texts.items()
         if async_rx.search(s) and not status_rx.search(s)]
print(f"\nScreens performing async work with no visible status indicator: "
      f"{len(blind)}")
for b in sorted(blind)[:10]:
    print(f"    {b}")

recover_rx = re.compile(r'\b(setError|errorMessage|error\s*&&)')
silent = [os.path.basename(f) for f, s in texts.items()
          if re.search(r'catch\s*\(', s) and not recover_rx.search(s)]
print(f"\nScreens catching errors without surfacing them to the user: {len(silent)}")
for b in sorted(silent)[:10]:
    print(f"    {b}")

json.dump(dict(files=len(SRC), heuristics=rows,
               async_without_status=sorted(blind),
               silent_error_handling=sorted(silent)),
          open(paths.out('heuristic_audit.json'), 'w', encoding='utf-8'), indent=2)
print("\nsaved heuristic_audit.json")
