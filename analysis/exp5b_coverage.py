"""
Experiment 5b - Skill-vocabulary coverage on the 220-resume annotated corpus.

The parser extracts skills by exact-substring matching against a fixed 40-term
list, so any ground truth derived by substring matching over the same text is
matched trivially (recall = 1.000 by construction, as Experiment 5 showed).
The informative question is therefore not "does the matcher fire correctly" but
"what fraction of the skills a human annotator actually marked can this
vocabulary represent at all". That is measured here.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import json, re, sys, collections
import numpy as np

from candidate_parser import CandidateParser

P = CandidateParser()
VOCAB = [s.lower() for s in P.tech_skills]

recs = []
for f in [paths.CORPUS220_TRAIN,
          paths.CORPUS220_TEST]:
    for l in open(f, encoding='utf-8'):
        l = l.strip()
        if l: recs.append(json.loads(l))

def spans(r, lab):
    return [p['text'] for a in (r.get('annotation') or [])
            if a.get('label') and a['label'][0] == lab for p in a['points']]

SPLIT = re.compile(r'[,\n;/|]+|\s{2,}')
NOISE = re.compile(r'^(languages?|tools?|databases?|skills?|technologies|web technologies|'
                   r'operating systems?|middleware|version control system|product\w*|'
                   r'frameworks?|other|others|programming|platforms?|additional information|'
                   r'technical skills?|skill set|areas? of expertise|core competenc\w*|'
                   r'expertise|proficient\w*|knowledge|experience|summary|environment|'
                   r'domain|others?)\s*:?\s*$', re.I)
YEARFRAG = re.compile(r'^(?:less\s+)?than\s*\d*\s*years?\)?$|^\d*\s*years?\)?$|^\)?$', re.I)

def mentions(span):
    out = []
    for chunk in SPLIT.split(span):
        c = chunk.strip().strip('.:•-').strip()
        c = re.sub(r'\((?:less than\s*)?[\d.]*\s*(?:year|month)s?\)', '', c, flags=re.I).strip()
        if not c or len(c) < 2 or len(c) > 40: continue
        if NOISE.match(c) or YEARFRAG.match(c): continue
        if c.replace('.', '').isdigit(): continue
        out.append(c.lower())
    return out

all_m = []
per_resume = []
for r in recs:
    ms = []
    for s in spans(r, 'Skills'):
        ms += mentions(s)
    ms = list(dict.fromkeys(ms))
    if ms:
        cov = sum(1 for m in ms if any(v in m for v in VOCAB))
        per_resume.append(cov / len(ms))
        all_m += ms

freq = collections.Counter(all_m)
covered = {m for m in freq if any(v in m for v in VOCAB)}
n_tok = sum(freq.values())
n_cov = sum(v for m, v in freq.items() if m in covered)

print("="*74)
print("SKILL-VOCABULARY COVERAGE ON 220 REAL, HUMAN-ANNOTATED RESUMES")
print("="*74)
print(f"resumes with annotated skills : {len(per_resume)}")
print(f"distinct skill mentions       : {len(freq)}")
print(f"total skill mentions          : {n_tok}")
print(f"\nType coverage  (distinct mentions representable by the 40-term vocabulary):"
      f" {len(covered)}/{len(freq)} = {len(covered)/len(freq):.3f}")
print(f"Token coverage (all mentions weighted by frequency):"
      f" {n_cov}/{n_tok} = {n_cov/n_tok:.3f}")
pr = np.array(per_resume)
print(f"Per-resume coverage: mean={pr.mean():.3f}  median={np.median(pr):.3f}  "
      f"sd={pr.std():.3f}  resumes with zero coverage={int((pr==0).sum())} "
      f"({(pr==0).mean()*100:.1f}%)")

print("\nMost frequent skills the vocabulary CANNOT represent:")
miss = [(m, c) for m, c in freq.most_common() if m not in covered]
for m, c in miss[:25]:
    print(f"   {c:4d}  {m}")

print(f"\nVocabulary terms never observed in any annotated skills section:")
never = [v for v in VOCAB if not any(v in m for m in freq)]
print("   " + (', '.join(never) if never else '(none)'))

json.dump(dict(resumes=len(per_resume), distinct=len(freq), tokens=n_tok,
               type_coverage=len(covered)/len(freq), token_coverage=n_cov/n_tok,
               per_resume_mean=float(pr.mean()), per_resume_median=float(np.median(pr)),
               zero_coverage_pct=float((pr==0).mean()*100),
               top_missing=[m for m, _ in miss[:25]], never_seen=never),
          open(paths.out('real220_coverage.json'), 'w', encoding='utf-8'), indent=2)
print("\nsaved real220_coverage.json")
