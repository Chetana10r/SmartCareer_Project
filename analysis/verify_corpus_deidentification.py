"""
Data-provenance and de-identification check for the external resume corpora
used in Section 7.4.1.

Run this before submission and keep the output. If an editor or reviewer asks
what personal data the study touched, this is the answer, and it is reproducible.

    python verify_corpus_deidentification.py
"""
import json, glob, re, sys, os, collections

CORPORA = {
 'primary (Resume Corpus Dataset, 349)': dict(
     glob='Resume-Corpus-Dataset/data-files/*.json',
     text=lambda it: it.get('data', {}).get('text', ''),
     nested=True),
 'replication (Entity-Recognition-In-Resumes, 220)': dict(
     glob='Entity-Recognition-In-Resumes-SpaCy/*data.json',
     text=lambda it: it.get('content', ''),
     nested=False),
}

# Direct identifiers. Note the year-string guard: strings such as
# "SQL Server 201220142017" match a naive 10-digit phone pattern.
PATTERNS = {
 'email address':      re.compile(r'[\w.+-]+@[\w-]+\.\w{2,}'),
 'web/profile URL':    re.compile(r'linkedin\.com|github\.com|https?://\S+\.\w'),
 'telephone number':   re.compile(r'(?<!\d)(?:\+\d{1,3}[-\s]?)?[6-9]\d{9}(?!\d)'),
}
YEARISH = re.compile(r'^(?:19|20)\d{2}')   # discard version/year concatenations


def load(spec):
    out = []
    for f in sorted(glob.glob(spec['glob'])):
        if spec['nested']:
            try: out += json.load(open(f, encoding='utf-8'))
            except Exception: pass
        else:
            for line in open(f, encoding='utf-8'):
                line = line.strip()
                if line:
                    try: out.append(json.loads(line))
                    except Exception: pass
    return out


def audit(name, spec):
    items = load(spec)
    if not items:
        print(f"\n{name}: NOT FOUND (clone it first - see README)"); return None
    texts = [spec['text'](it) for it in items]
    print(f"\n{name}")
    print(f"  documents scanned: {len(texts)}")
    findings = {}
    for label, rx in PATTERNS.items():
        hits = []
        for i, t in enumerate(texts):
            for m in rx.finditer(t or ''):
                if label == 'telephone number' and YEARISH.match(m.group(0)):
                    continue
                hits.append((i, m.group(0)))
        findings[label] = hits
        verdict = 'none found' if not hits else f'{len(hits)} in {len({i for i,_ in hits})} docs'
        print(f"  {label:20s}: {verdict}")
        for i, v in hits[:3]:
            print(f"        e.g. doc {i}: {v!r}")
    # annotator metadata (personal data about the labellers, not the candidates)
    ann = set()
    for it in items:
        for a in (it.get('annotations') or []):
            cb = a.get('completed_by')
            if isinstance(cb, dict) and cb.get('email'):
                ann.add(cb['email'])
    print(f"  annotator emails in metadata: {len(ann)}"
          + ("  <-- strip before any redistribution" if ann else ""))
    return findings


if __name__ == '__main__':
    print("=" * 72)
    print("DE-IDENTIFICATION AUDIT OF EXTERNAL RESUME CORPORA")
    print("=" * 72)
    clean = True
    for name, spec in CORPORA.items():
        f = audit(name, spec)
        if f and any(v for v in f.values()):
            clean = False
    print("\n" + "=" * 72)
    print("CONCLUSION: no direct identifiers detected in resume text."
          if clean else
          "CONCLUSION: direct identifiers present - review before use.")
    print("Company names, cities and employment dates remain and are quasi-identifiers;")
    print("only aggregate metrics are reported and neither corpus is redistributed.")
    print("=" * 72)
