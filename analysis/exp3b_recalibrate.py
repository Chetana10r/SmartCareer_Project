"""
Experiment 3b - Constructive recalibration of the tier thresholds.
Compares (i) current fixed cut-offs, (ii) quantile-based cut-offs on the
existing heuristic score, (iii) quantile cut-offs on the learned-weight score.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import pickle, numpy as np, pandas as pd
D_ALL = pickle.load(open(paths.out('scored.pkl'),'rb'))
COMPS = ['S_skills','S_experience','S_education','S_keyword','S_semantic']
W1 = dict(S_skills=.35,S_experience=.20,S_education=.15,S_keyword=.15,S_semantic=.15)
W_LEARNED = {'IT': dict(S_skills=.13,S_experience=.35,S_education=.26,S_keyword=.00,S_semantic=.26),
             'Non-IT': dict(S_skills=.00,S_experience=.01,S_education=.08,S_keyword=.36,S_semantic=.55)}
W_RANK = dict(S_match=.40,S_skills=.25,S_experience=.20,S_education=.10,S_semantic=.05)
NAMES = ['Below Average','Average','Good','Strong','Excellent']
# target share of pool per tier, top-heavy: Excellent 5%, Strong 15%, Good 30%, Average 30%, Below 20%
QS = [0.20, 0.50, 0.80, 0.95]

def comp(d,w):
    t=sum(w.values()); return sum(d[c]*w.get(c,0) for c in COMPS)/(t if t else 1)

def tier_table(scores, rel, cuts, label):
    edges = [-np.inf]+list(cuts)+[np.inf]
    print(f"\n  {label}")
    print(f"  {'tier':<15}{'cut-off':>10}{'n':>7}{'% pool':>9}{'precision':>11}{'lift':>7}")
    base = rel.mean(); precs=[]
    for i,name in enumerate(NAMES):
        m = (scores>=edges[i])&(scores<edges[i+1]); n=int(m.sum())
        p = rel[m].mean() if n else float('nan')
        precs.append(p)
        cut = '-inf' if i==0 else f"{edges[i]:.1f}"
        print(f"  {name:<15}{cut:>10}{n:>7}{100*n/len(scores):>8.1f}%{p:>11.3f}{(p/base if n and base else float('nan')):>7.2f}")
    v=[p for p in precs if p==p]
    print(f"  monotonic (higher tier => higher precision): {all(np.diff(v)>=-1e-9)}   base rate={base:.3f}")
    return precs

for dom,(D,_,_) in D_ALL.items():
    D=D.copy(); rel=D['rel'].values
    D['S_match']=comp(D,W1)
    tot=sum(W_RANK.values())
    s_cur = (sum(D[c]*w for c,w in W_RANK.items())/tot).values
    D['S_match']=comp(D,W_LEARNED[dom])
    s_new = (sum(D[c]*w for c,w in W_RANK.items())/tot).values

    print("\n"+"="*70); print(f"  DOMAIN: {dom}"); print("="*70)
    tier_table(s_cur, rel, [40,55,70,85], "(i) CURRENT: heuristic weights + fixed 40/55/70/85 cut-offs")
    q_cur = np.quantile(s_cur, QS)
    tier_table(s_cur, rel, q_cur, f"(ii) heuristic weights + quantile cut-offs {np.round(q_cur,1).tolist()}")
    q_new = np.quantile(s_new, QS)
    tier_table(s_new, rel, q_new, f"(iii) LEARNED weights + quantile cut-offs {np.round(q_new,1).tolist()}")
