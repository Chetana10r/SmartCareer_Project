"""
Experiment 6 - Content-validity analysis of the interview question bank by
mapping to published frameworks rather than by surveying human experts.

Two established frameworks are applied as coding schemes:
  (1) Bloom's revised taxonomy (Anderson & Krathwohl, 2001) - the cognitive
      level demanded by each technical template, inferred from its stem verb,
      tested against the difficulty label the system assigns.
  (2) The behavioural/situational distinction from the structured-employment-
      interview literature - whether each HR template elicits a past-behaviour
      account (which STAR-based scoring assumes) or a hypothetical/dispositional
      answer (which it does not).

This is document analysis of the system's own configuration file. It involves
no human participants and no personal data.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import json, re, collections
import numpy as np

TPL = json.load(open(paths.QTEMPLATES, encoding='utf-8'))

# ---- Bloom's revised taxonomy levels, ordered ----
BLOOM = ['Remember', 'Understand', 'Apply', 'Analyse', 'Evaluate', 'Create']
BLOOM_RANK = {b: i + 1 for i, b in enumerate(BLOOM)}

# Stem-verb cues. Ordered most-specific first; first match wins.
CUES = [
 ('Create',    [r'\bdesign\b', r'\barchitect', r'\bconstruct\b', r'\bdevelop a\b']),
 ('Evaluate',  [r'\btrade-?offs?\b', r'\badvantages and disadvantages\b', r'\bbest choice\b',
                r'\bwhy should we\b', r'\bbest practices\b', r'\bjustify\b', r'\bassess\b']),
 ('Analyse',   [r'\bcompare\b', r'\bdifferences? between\b', r'\bbottlenecks?\b', r'\bdebug\b',
                r'\bcomplexity analysis\b', r'\bpitfalls?\b', r'\banalys', r'\bhow does .* handle\b']),
 ('Apply',     [r'\bhow would you implement\b', r'\bimplement\b', r'\bapply\b', r'\boptimi[sz]e\b',
                r'\buse case\b', r'\bapplications of\b', r'\bscenario\b', r'\btechniques can be applied\b']),
 ('Understand',[r'\bexplain\b', r'\bdescribe\b', r'\bhow does\b', r'\bpurpose of\b',
                r'\bhow .* work\b', r'\bimprove performance\b']),
 ('Remember',  [r'\bwhat is\b', r'\bwhat are the basic\b', r'\blist\b', r'\bdefine\b',
                r'\bwhat are the main\b']),
]

def bloom_of(q):
    ql = q.lower()
    for lvl, pats in CUES:
        if any(re.search(p, ql) for p in pats):
            return lvl
    return 'Understand'   # conservative default

LABEL_EXPECT = {'easy': (1, 2), 'medium': (3, 4), 'hard': (5, 6)}

print("=" * 78)
print("(A) BLOOM'S TAXONOMY MAPPING OF TECHNICAL TEMPLATES vs ASSIGNED DIFFICULTY")
print("=" * 78)
rows, agree, total = [], 0, 0
dist = collections.defaultdict(collections.Counter)
for lvl in ['easy', 'medium', 'hard']:
    for q in TPL['technical'][lvl]:
        b = bloom_of(q); r = BLOOM_RANK[b]
        lo, hi = LABEL_EXPECT[lvl]
        ok = lo <= r <= hi
        agree += ok; total += 1
        dist[lvl][b] += 1
        rows.append((lvl, b, ok, q))
print(f"\n{'label':<8}{'Bloom level distribution'}")
for lvl in ['easy', 'medium', 'hard']:
    d = dist[lvl]
    print(f"{lvl:<8}" + ', '.join(f"{k}={v}" for k, v in
          sorted(d.items(), key=lambda t: BLOOM_RANK[t[0]])))
print(f"\nLabel/level concordance: {agree}/{total} = {agree/total:.3f}")
print("\nTemplates whose Bloom level is inconsistent with their difficulty label:")
for lvl, b, ok, q in rows:
    if not ok:
        print(f"   [{lvl:<6} -> {b:<10}] {q}")

# monotonicity of mean cognitive demand
means = {lvl: np.mean([BLOOM_RANK[bloom_of(q)] for q in TPL['technical'][lvl]])
         for lvl in ['easy', 'medium', 'hard']}
print("\nMean Bloom rank by assigned difficulty: " +
      ', '.join(f"{k}={v:.2f}" for k, v in means.items()))
print("monotonically increasing:",
      means['easy'] < means['medium'] < means['hard'])

# ---- (B) behavioural vs non-behavioural HR templates ----
print("\n" + "=" * 78)
print("(B) HR TEMPLATES: PAST-BEHAVIOUR vs NON-BEHAVIOURAL STEMS")
print("=" * 78)
BEHAV = [r'\btell me about a time\b', r'\bdescribe a (situation|project|challenging)',
         r'\bdescribe how you', r'\bhow have you handled\b', r'\bdescribe a scenario\b']
res = {}
for lvl in ['easy', 'medium', 'hard']:
    qs = TPL['hr'][lvl]
    b = [q for q in qs if any(re.search(p, q.lower()) for p in BEHAV)]
    res[lvl] = (len(b), len(qs))
    print(f"  {lvl:<7} behavioural {len(b)}/{len(qs)} = {len(b)/len(qs):.2f}")
tot_b = sum(v[0] for v in res.values()); tot_n = sum(v[1] for v in res.values())
print(f"  overall behavioural: {tot_b}/{tot_n} = {tot_b/tot_n:.3f}")
print("\n  Non-behavioural stems in the 'easy' tier (scored by a STAR-based rubric):")
for q in TPL['hr']['easy']:
    if not any(re.search(p, q.lower()) for p in BEHAV):
        print("     ", q)

# ---- (C) role coverage ----
print("\n" + "=" * 78)
print("(C) ROLE COVERAGE OF THE ROLE-SPECIFIC BANK")
print("=" * 78)
roles_bank = set(TPL['role_specific'])
IT = {'ai engineer', 'cloud engineer', 'data scientist', 'software engineer', 'web developer'}
NONIT = {'accountant', 'business analyst', 'customer support representative',
         'market research analyst', 'operations manager'}
norm = {r.replace('_', ' ') for r in roles_bank}
print(f"  bank roles ({len(roles_bank)}): {sorted(norm)}")
print(f"  IT roles covered    : {sorted(IT & norm)}  -> {len(IT & norm)}/{len(IT)}")
print(f"  Non-IT roles covered: {sorted(NONIT & norm)} -> {len(NONIT & norm)}/{len(NONIT)}")
print(f"  classifier roles with NO role-specific questions: "
      f"{sorted((IT | NONIT) - norm)}")

json.dump(dict(bloom_concordance=agree/total, n_technical=total,
               bloom_means=means, behavioural_ratio=tot_b/tot_n,
               role_coverage=len((IT | NONIT) & norm) / len(IT | NONIT),
               uncovered_roles=sorted((IT | NONIT) - norm)),
          open(paths.out('qbank_validity.json'), 'w', encoding='utf-8'), indent=2)
print("\nsaved qbank_validity.json")
