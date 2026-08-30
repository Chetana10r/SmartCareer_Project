"""
Experiment 3 - (a) learning-to-rank derivation of the composite weights
               (b) empirical calibration of the 85/70/55/40 tier thresholds
Addresses Reviewer 5 points 4 and 8.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import pickle, numpy as np, pandas as pd
from scipy.stats import kendalltau
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

D_ALL = pickle.load(open(paths.out('scored.pkl'),'rb'))
COMPS = ['S_skills','S_experience','S_education','S_keyword','S_semantic']
W1 = dict(S_skills=.35, S_experience=.20, S_education=.15, S_keyword=.15, S_semantic=.15)

def composite(d, w):
    t = sum(w.values()); return sum(d[c]*w.get(c,0) for c in COMPS)/(t if t else 1)

def ndcg(df, col, k=10):
    o=[]
    for _,g in df.groupby('job'):
        g=g.sort_values(col,ascending=False); rel=g['rel'].values[:k]
        dcg=np.sum(rel/np.log2(np.arange(2,len(rel)+2)))
        idl=np.sort(g['rel'].values)[::-1][:k]
        idcg=np.sum(idl/np.log2(np.arange(2,len(idl)+2)))
        o.append(dcg/idcg if idcg>0 else 0.)
    return float(np.mean(o))

def coord_ascent(df, seed_w, iters=30, grid=np.linspace(0,1,41)):
    """Coordinate ascent directly on NDCG@10 (Metzler & Croft style)."""
    w = dict(seed_w); best = ndcg(df.assign(s=composite(df,w)),'s')
    for _ in range(iters):
        improved = False
        for c in COMPS:
            cur = w[c]; bv, bs = cur, best
            for g in grid:
                w[c] = g
                if sum(w.values()) == 0: continue
                s = ndcg(df.assign(s=composite(df,w)),'s')
                if s > bs + 1e-9: bs, bv = s, g
            w[c] = bv
            if bs > best + 1e-9: best, improved = bs, True
        if not improved: break
    tot = sum(w.values())
    return {k: round(v/tot,4) for k,v in w.items()}, best

print("="*78)
print("(a) LEARNING-TO-RANK WEIGHT DERIVATION")
print("="*78)
rows=[]
for dom,(D,bn,bp) in D_ALL.items():
    # grouped CV by job so weights are not tuned and tested on the same job
    jobs = D['job'].unique(); gkf = GroupKFold(n_splits=len(jobs))
    heldout_base, heldout_opt = [], []
    for tr, te in gkf.split(D, groups=D['job']):
        Dtr, Dte = D.iloc[tr], D.iloc[te]
        w_opt,_ = coord_ascent(Dtr, W1, iters=8)
        heldout_base.append(ndcg(Dte.assign(s=composite(Dte,W1)),'s'))
        heldout_opt.append(ndcg(Dte.assign(s=composite(Dte,w_opt)),'s'))
    w_full, ndcg_full = coord_ascent(D, W1, iters=20)

    # LambdaRank-free alternative: logistic regression on relevance, coefficients -> weights
    lr = LogisticRegression(max_iter=2000, class_weight='balanced')
    Xs = D[COMPS].values / 100.0
    lr.fit(Xs, D['rel'].values)
    coef = np.clip(lr.coef_[0], 0, None)
    w_lr = {c: round(float(v/coef.sum()),4) for c,v in zip(COMPS, coef)} if coef.sum()>0 else W1

    print(f"\n--- {dom} ---")
    print(f"  heuristic weights (current) : {W1}")
    print(f"  coordinate-ascent (in-sample NDCG@10 optimum): {w_full}")
    print(f"  logistic-regression derived : {w_lr}")
    print(f"  NDCG@10  heuristic = {bn:.4f} | coord-ascent in-sample = {ndcg_full:.4f} "
          f"| logistic = {ndcg(D.assign(s=composite(D,w_lr)),'s'):.4f}")
    print(f"  leave-one-job-out CV NDCG@10: heuristic = {np.mean(heldout_base):.4f} "
          f"| learned = {np.mean(heldout_opt):.4f}  (delta {np.mean(heldout_opt)-np.mean(heldout_base):+.4f})")
    rows.append(dict(domain=dom, **{f'lr_{k}':v for k,v in w_lr.items()},
                     **{f'ca_{k}':v for k,v in w_full.items()},
                     ndcg_heur=bn, ndcg_ca=ndcg_full,
                     cv_heur=np.mean(heldout_base), cv_learned=np.mean(heldout_opt)))
pd.DataFrame(rows).to_csv(paths.out('weights.csv'), index=False)

print("\n"+"="*78)
print("(b) TIER THRESHOLD CALIBRATION  (Excellent>=85, Strong>=70, Good>=55, Average>=40)")
print("="*78)
W_RANK = dict(S_match=.40, S_skills=.25, S_experience=.20, S_education=.10, S_semantic=.05)
TIERS = [('Excellent',85,101),('Strong',70,85),('Good',55,70),('Average',40,55),('Below Average',-1,40)]
tr_rows=[]
for dom,(D,bn,bp) in D_ALL.items():
    D = D.copy()
    D['S_match'] = composite(D, W1)
    tot = sum(W_RANK.values())
    D['S_rank'] = sum(D[c]*w for c,w in W_RANK.items())/tot
    print(f"\n--- {dom} --- S_rank: mean {D.S_rank.mean():.1f}, sd {D.S_rank.std():.1f}, "
          f"min {D.S_rank.min():.1f}, max {D.S_rank.max():.1f}")
    print(f"{'tier':<15}{'n':>7}{'% of pool':>11}{'precision':>11}{'recall':>9}")
    for name, lo, hi in TIERS:
        m = (D.S_rank>=lo)&(D.S_rank<hi)
        n = int(m.sum())
        prec = D.loc[m,'rel'].mean() if n else float('nan')
        rec  = D.loc[m,'rel'].sum()/D['rel'].sum() if n else 0
        print(f"{name:<15}{n:>7}{100*n/len(D):>10.1f}%{prec:>11.3f}{rec:>9.3f}")
        tr_rows.append(dict(domain=dom, tier=name, n=n, pct=100*n/len(D), precision=prec, recall=rec))
    base = D['rel'].mean()
    print(f"  base rate (random candidate is a true role match) = {base:.3f}")
    # monotonicity check
    precs=[D.loc[(D.S_rank>=lo)&(D.S_rank<hi),'rel'].mean() for _,lo,hi in TIERS]
    precs=[p for p in precs if p==p]
    print(f"  precision monotonically decreasing across tiers: {all(np.diff(precs)<=1e-9)}")
    # sensitivity: shift all thresholds +-5
    for shift in (-5,5):
        cuts=[85+shift,70+shift,55+shift,40+shift]
        t0=np.digitize(D.S_rank,[40,55,70,85]); t1=np.digitize(D.S_rank,sorted(cuts))
        print(f"  thresholds shifted {shift:+d} pts -> {100*np.mean(t0!=t1):.1f}% of candidates change tier")
pd.DataFrame(tr_rows).to_csv(paths.out('thresholds.csv'), index=False)
print("\nsaved weights.csv + thresholds.csv")
