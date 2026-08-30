"""
Experiment 5 - Quantitative validation of candidate_parser.py on a real,
independently-annotated resume corpus (220 resumes from an online jobs platform,
manually annotated with Skills, Degree, Years of Experience, Name, Email).

The parser's internal extraction methods are called unmodified on the corpus's
raw resume text. Only PDF text extraction is bypassed, since the corpus supplies
text directly; every parsing rule under test is the released one.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import json, re, sys, collections
import numpy as np, pandas as pd

from candidate_parser import CandidateParser

P = CandidateParser()
VOCAB = [s.lower() for s in P.tech_skills]
print(f"parser skill vocabulary: {len(VOCAB)} terms")

recs = []
for f in [paths.CORPUS220_TRAIN,
          paths.CORPUS220_TEST]:
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if line: recs.append(json.loads(line))
print(f"resumes: {len(recs)}")

def spans(rec, label):
    out = []
    for a in (rec.get('annotation') or []):
        if a.get('label') and a['label'][0] == label:
            for p in a['points']:
                out.append(p['text'])
    return out

def parse_years(s):
    """'5 Years 6 Months' / '3 years' / 'Less than 1 year' -> float years"""
    s = s.lower()
    if 'less than' in s: return 0.5
    y = re.search(r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*year', s)
    m = re.search(r'(\d+)\s*month', s)
    tot = (float(y.group(1)) if y else 0.0) + (int(m.group(1))/12.0 if m else 0.0)
    return tot if (y or m) else None

# =============================================================
rows = []
skill_tp = skill_fp = skill_fn = 0
oracle_tp = oracle_fn = 0
exp_n = exp_exact = exp_within1 = exp_zero = 0
edu_n = edu_hit = 0
email_n = email_hit = 0
name_n = name_hit = 0

for r in recs:
    text = r['content']
    pred_sk = {s.lower() for s in P._extract_skills(text)}

    # ---- ground truth skills: vocabulary terms inside annotated Skills spans
    sk_text = ' '.join(spans(r, 'Skills')).lower()
    gt_sk = {v for v in VOCAB if v in sk_text}
    # oracle: vocabulary terms anywhere in the document (coverage ceiling)
    full_low = text.lower()
    oracle_sk = {v for v in VOCAB if v in full_low}

    if gt_sk or pred_sk:
        skill_tp += len(pred_sk & gt_sk)
        skill_fp += len(pred_sk - gt_sk)
        skill_fn += len(gt_sk - pred_sk)
    oracle_tp += len(oracle_sk & gt_sk); oracle_fn += len(gt_sk - oracle_sk)

    # ---- years of experience
    ys = [parse_years(s) for s in spans(r, 'Years of Experience')]
    ys = [y for y in ys if y is not None]
    if ys:
        gt_y = max(ys); pred_y = P._extract_experience(text)
        exp_n += 1
        if abs(pred_y - gt_y) < 0.5: exp_exact += 1
        if abs(pred_y - gt_y) <= 1.0: exp_within1 += 1
        if pred_y == 0: exp_zero += 1
        rows.append(dict(kind='experience', gt=gt_y, pred=pred_y))

    # ---- degree present in extracted education field
    degs = spans(r, 'Degree')
    if degs:
        edu_n += 1
        edu_field = (P._extract_education(text) or '').lower()
        if any(d.lower()[:25] in edu_field for d in degs): edu_hit += 1

    # ---- email
    ems = spans(r, 'Email Address')
    if ems:
        email_n += 1
        pe = (P._extract_email(text) or '').lower()
        if pe and any(pe in e.lower() or e.lower() in pe for e in ems): email_hit += 1

    # ---- name
    nms = spans(r, 'Name')
    if nms:
        name_n += 1
        pn = (P._extract_name(text) or '').lower().strip()
        if pn and any(n.lower().strip() in pn or pn in n.lower().strip() for n in nms):
            name_hit += 1

def prf(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    return p, r, (2*p*r/(p+r) if p+r else 0.0)

print("\n" + "="*72)
print("QUANTITATIVE PARSER VALIDATION ON 220 REAL, ANNOTATED RESUMES")
print("="*72)
p, r, f = prf(skill_tp, skill_fp, skill_fn)
print(f"\nSkill extraction (vs annotated Skills spans)")
print(f"  TP={skill_tp}  FP={skill_fp}  FN={skill_fn}")
print(f"  precision={p:.3f}  recall={r:.3f}  F1={f:.3f}")
op, orr, of = prf(oracle_tp, 0, oracle_fn)
print(f"  vocabulary coverage ceiling (any vocab term anywhere in doc): recall={orr:.3f}")

print(f"\nYears of experience (n={exp_n} resumes with annotation)")
if exp_n:
    print(f"  within 0.5 yr : {exp_exact}/{exp_n} = {exp_exact/exp_n:.3f}")
    print(f"  within 1.0 yr : {exp_within1}/{exp_n} = {exp_within1/exp_n:.3f}")
    print(f"  returned 0    : {exp_zero}/{exp_n} = {exp_zero/exp_n:.3f}")

print(f"\nEducation field contains annotated Degree (n={edu_n})")
print(f"  {edu_hit}/{edu_n} = {edu_hit/edu_n:.3f}" if edu_n else "  n/a")
print(f"\nEmail extraction (n={email_n}): {email_hit}/{email_n} = {email_hit/email_n:.3f}")
print(f"Name extraction, spaCy unavailable so first-line fallback (n={name_n}): "
      f"{name_hit}/{name_n} = {name_hit/name_n:.3f}")

pd.DataFrame(rows).to_csv(paths.out('real220_experience.csv'), index=False)
json.dump(dict(skill=dict(tp=skill_tp, fp=skill_fp, fn=skill_fn, precision=p, recall=r, f1=f,
                          oracle_recall=orr),
               experience=dict(n=exp_n, within05=exp_exact, within1=exp_within1, zero=exp_zero),
               education=dict(n=edu_n, hit=edu_hit),
               email=dict(n=email_n, hit=email_hit),
               name=dict(n=name_n, hit=name_hit)),
          open(paths.out('real220_results.json'), 'w', encoding='utf-8'), indent=2)
print("\nsaved real220_results.json")
