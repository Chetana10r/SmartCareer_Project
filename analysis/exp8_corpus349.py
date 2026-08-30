"""
Experiment 8 - Skill-vocabulary coverage on the Resume Corpus Dataset
(349 real resumes, 36 annotated entity types, released for academic and
research use). Replaces the earlier unlicensed corpus as the primary external
validation set.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import json, glob, re, sys, collections
import numpy as np

from candidate_parser import CandidateParser

# ---------------------------------------------------------------------------
# Redaction pass. Both corpora are redacted at source but the redaction is
# incomplete (1.4% and 2.3% of documents retain a direct identifier). Apply
# this before any analysis, and never write the raw text to an output file.
# ---------------------------------------------------------------------------
REDACT = [
 (re.compile(r'[\w.+-]+@[\w-]+\.\w{2,}'), '[EMAIL]'),
 (re.compile(r'\b\w{3,}(?:gmail|yahoo|hotmail|outlook|rediffmail)com\b', re.I), '[EMAIL]'),
 (re.compile(r'(?<![\da-f])(?:\+\d{1,3}[-\s]?)?[6-9]\d{9}(?![\da-f])'), '[PHONE]'),
 (re.compile(r'\bPin\s?\d{6}\b', re.I), '[POSTCODE]'),
 (re.compile(r'https?://\S+|\bhttpwww\w+'), '[URL]'),
]


def redact(text):
    """Remove residual direct identifiers from a resume before analysis."""
    for rx, tag in REDACT:
        text = rx.sub(tag, text or '')
    return text

P = CandidateParser()
VOCAB = [s.lower() for s in P.tech_skills]

items = []
for f in sorted(glob.glob(paths.CORPUS349)):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    items += d
print(f"resumes: {len(items)}  |  parser vocabulary: {len(VOCAB)} terms")

def labelled(item, want):
    out = []
    for a in item.get('annotations', []):
        for r in a.get('result', []):
            v = r.get('value', {})
            if want in (v.get('labels') or []):
                t = (v.get('text') or '').strip()
                if t: out.append(t)
    return out

SPLIT = re.compile(r'[,\n;/|]+|\s{2,}')
NOISE = re.compile(r'^(languages?|tools?|databases?|skills?|technologies|web technologies|'
                   r'operating systems?|middleware|frameworks?|other|others|programming|'
                   r'platforms?|technical skills?|additional information|expertise|knowledge|'
                   r'experience|summary|environment|domain)\s*:?\s*$', re.I)

def mentions(span):
    out = []
    for c in SPLIT.split(span):
        c = c.strip().strip('.:•-').strip()
        c = re.sub(r'\((?:less than\s*)?[\d.]*\s*(?:year|month)s?\)', '', c, flags=re.I).strip()
        if not c or len(c) < 2 or len(c) > 45: continue
        if NOISE.match(c) or c.replace('.', '').isdigit(): continue
        out.append(c.lower())
    return out

freq = collections.Counter(); per = []
exp_hits = exp_n = 0
for it in items:
    ms = []
    for s in labelled(it, 'technical_skills'):
        ms += mentions(redact(s))
    ms = list(dict.fromkeys(ms))
    if ms:
        cov = sum(1 for m in ms if any(v in m for v in VOCAB))
        per.append(cov / len(ms)); freq.update(ms)
    # experience: does the parser recover any years figure at all?
    yrs = labelled(it, 'work_year')
    if yrs:
        exp_n += 1
        if P._extract_experience(redact(it.get('data', {}).get('text', ''))) > 0: exp_hits += 1

covered = {m for m in freq if any(v in m for v in VOCAB)}
n_tok = sum(freq.values()); n_cov = sum(v for m, v in freq.items() if m in covered)
per = np.array(per)

print("\n" + "=" * 74)
print("SKILL-VOCABULARY COVERAGE  (Resume Corpus Dataset, 349 resumes)")
print("=" * 74)
print(f"resumes with annotated technical skills : {len(per)}")
print(f"distinct skill mentions                 : {len(freq)}")
print(f"total skill mentions                    : {n_tok}")
print(f"\nType coverage  : {len(covered)}/{len(freq)} = {len(covered)/len(freq):.3f}")
print(f"Token coverage : {n_cov}/{n_tok} = {n_cov/n_tok:.3f}")
print(f"Per-resume     : mean={per.mean():.3f} median={np.median(per):.3f} "
      f"sd={per.std():.3f} zero-coverage={int((per==0).sum())} ({(per==0).mean()*100:.1f}%)")
print(f"\nExperience: parser returns a non-zero figure for {exp_hits}/{exp_n} "
      f"= {exp_hits/exp_n:.3f} of resumes with an annotated work-year span"
      if exp_n else "")

print("\nMost frequent skills the vocabulary cannot represent:")
for m, c in [(m, c) for m, c in freq.most_common() if m not in covered][:20]:
    print(f"   {c:4d}  {m}")
never = [v for v in VOCAB if not any(v in m for m in freq)]
print(f"\nVocabulary terms never observed ({len(never)}/{len(VOCAB)}): {', '.join(never)}")

json.dump(dict(corpus='Resume Corpus Dataset', resumes=len(items),
               with_skills=len(per), distinct=len(freq), tokens=n_tok,
               type_coverage=len(covered)/len(freq), token_coverage=n_cov/n_tok,
               per_resume_mean=float(per.mean()), per_resume_median=float(np.median(per)),
               zero_pct=float((per==0).mean()*100),
               experience_nonzero=(exp_hits/exp_n if exp_n else None), experience_n=exp_n,
               never_seen=never),
          open(paths.out('corpus349.json'), 'w', encoding='utf-8'), indent=2)
print("\nsaved corpus349.json")
