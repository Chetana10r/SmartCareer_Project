"""
Experiment 9 - Leakage-controlled skill prediction.

Section 7.5 shows that the reported skill-prediction scores are inflated because
each Skills label is recoverable by substring search over the same
Keywords/Technologies text the vectoriser is fit on, so the task is close to
deterministic. Acknowledging that is not the same as measuring what the model
can do when the shortcut is removed.

This experiment quantifies the leak and re-runs the task without it:

  Setting A (as published) : input = Projects + Keywords + Technologies
  Setting B (leak-free)    : input = Projects only, and any example whose label
                             token appears literally in the input is counted so
                             that residual leakage is reported rather than assumed
  Setting C (inference)    : input = Projects only, evaluated ONLY on
                             (example, label) pairs where the skill word does NOT
                             appear anywhere in the input text - i.e. genuine
                             inference from context rather than lexical matching

Reported per setting: micro/macro F1, plus the proportion of positive labels
that are lexically present in the input (the leak rate).
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

RS = 42


def load(csv):
    d = pd.read_csv(csv)
    d = d.dropna(subset=['Skills'])
    labels = [[s.strip().lower() for s in str(r).split(',') if s.strip()] for r in d['Skills']]
    for c in ['Projects','Keywords','Technologies']:
        d[c] = d[c].fillna('').astype(str)
    txt_full = (d['Projects'] + ' ' + d['Keywords'] + ' ' + d['Technologies']).str.lower()
    txt_proj = d['Projects'].str.lower()
    return labels, txt_full.values, txt_proj.values


def leak_rate(texts, labels):
    """Proportion of positive labels whose token appears literally in the input."""
    tot = hit = 0
    for t, ls in zip(texts, labels):
        for l in ls:
            tot += 1
            if l in t:
                hit += 1
    return hit / tot if tot else float('nan')


def run(texts, labels, tag, mask_lexical=False):
    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(labels)
    keep = Y.sum(axis=0) >= 20                      # labels with enough support
    Y = Y[:, keep]; classes = mlb.classes_[keep]

    Xtr, Xte, Ytr, Yte, ttr, tte = train_test_split(
        texts, Y, texts, test_size=0.2, random_state=RS)

    vec = TfidfVectorizer(max_features=3000, stop_words='english', ngram_range=(1, 2))
    A = vec.fit_transform(Xtr); B = vec.transform(Xte)

    clf = MultiOutputClassifier(
        RandomForestClassifier(n_estimators=120, random_state=RS, n_jobs=-1))
    clf.fit(A, Ytr)
    P = clf.predict(B)

    if mask_lexical:
        # evaluate only on (example, label) cells where the label word is ABSENT
        # from the input text: genuine inference, no lexical shortcut available
        M = np.ones_like(Yte, dtype=bool)
        for i, t in enumerate(tte):
            for j, c in enumerate(classes):
                if c in t:
                    M[i, j] = False
        if M.sum() == 0:
            print(f"  {tag}: no inference-only cells"); return None
        yt = Yte[M].ravel(); yp = P[M].ravel()
        mi = f1_score(yt, yp, average='binary', zero_division=0)
        ma = mi
        n = int(M.sum()); pos = int(yt.sum())
        print(f"  {tag:<46} F1={mi:.3f}   cells={n}  positives={pos}")
        return dict(setting=tag, micro_f1=mi, macro_f1=ma, n_cells=n, n_positive=pos)

    mi = f1_score(Yte, P, average='micro', zero_division=0)
    ma = f1_score(Yte, P, average='macro', zero_division=0)
    print(f"  {tag:<46} micro-F1={mi:.3f}   macro-F1={ma:.3f}   labels={len(classes)}")
    return dict(setting=tag, micro_f1=mi, macro_f1=ma, n_labels=len(classes))


rows = []
for name, csv in [('IT', paths.IT_CSV), ('Non-IT', paths.NONIT_CSV)]:
    labels, full, proj = load(csv)
    print(f"\n=== {name} ({len(labels)} resumes) ===")
    print(f"  leak rate, Projects+Keywords+Technologies : {leak_rate(full, labels):.3f}")
    print(f"  leak rate, Projects only                  : {leak_rate(proj, labels):.3f}")
    for r in [run(full, labels, 'A: as published (Projects+Keywords+Tech)'),
              run(proj, labels, 'B: leak-reduced (Projects only)'),
              run(proj, labels, 'C: inference-only cells (label word absent)', mask_lexical=True)]:
        if r: r['domain'] = name; rows.append(r)

df = pd.DataFrame(rows)
df.to_csv(paths.out('skill_inference.csv'), index=False)
print("\nsaved skill_inference.csv")
