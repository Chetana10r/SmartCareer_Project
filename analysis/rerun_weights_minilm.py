"""
Re-derive the composite scoring weights (Table 13) and the tier calibration
(Table 14) from the LIVE MiniLM score matrices produced by
rerun_ablation_minilm.py.

Run AFTER rerun_ablation_minilm.py:

    python rerun_weights_minilm.py

Reads  minilm_scores_IT.csv and minilm_scores_Non-IT.csv
Writes minilm_weights.csv and minilm_thresholds.csv
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

COMPS = ['S_skills', 'S_experience', 'S_education', 'S_keyword', 'S_semantic']
W1 = dict(S_skills=.35, S_experience=.20, S_education=.15, S_keyword=.15, S_semantic=.15)
W_RANK = dict(S_match=.40, S_skills=.25, S_experience=.20, S_education=.10, S_semantic=.05)
TIERS = [('Excellent', 85, 101), ('Strong', 70, 85), ('Good', 55, 70),
         ('Average', 40, 55), ('Below Average', -1, 40)]


def composite(d, w):
    t = sum(w.values())
    return sum(d[c] * w.get(c, 0) for c in COMPS) / (t if t else 1)


def ndcg(df, col, k=10):
    out = []
    for _, g in df.groupby('job'):
        g = g.sort_values(col, ascending=False)
        rel = g['rel'].values[:k]
        dcg = np.sum(rel / np.log2(np.arange(2, len(rel) + 2)))
        idl = np.sort(g['rel'].values)[::-1][:k]
        idcg = np.sum(idl / np.log2(np.arange(2, len(idl) + 2)))
        out.append(dcg / idcg if idcg > 0 else 0.0)
    return float(np.mean(out))


def coord_ascent(df, seed, iters=20, grid=np.linspace(0, 1, 41)):
    w = dict(seed); best = ndcg(df.assign(s=composite(df, w)), 's')
    for _ in range(iters):
        improved = False
        for c in COMPS:
            bv, bs = w[c], best
            for g in grid:
                w[c] = g
                if sum(w.values()) == 0:
                    continue
                sc = ndcg(df.assign(s=composite(df, w)), 's')
                if sc > bs + 1e-9:
                    bs, bv = sc, g
            w[c] = bv
            if bs > best + 1e-9:
                best, improved = bs, True
        if not improved:
            break
    tot = sum(w.values())
    return {k: round(v / tot, 4) for k, v in w.items()}, best


rows, trows = [], []
for dom in ['IT', 'Non-IT']:
    f = paths.out(f'minilm_scores_{dom}.csv')
    if not os.path.exists(f):
        sys.exit(f"Missing {f}\nRun rerun_ablation_minilm.py first.")
    D = pd.read_csv(f)
    base = ndcg(D.assign(s=composite(D, W1)), 's')

    # leave-one-job-out cross-validation
    gkf = GroupKFold(n_splits=D['job'].nunique())
    hb, ho = [], []
    for tr, te in gkf.split(D, groups=D['job']):
        Dtr, Dte = D.iloc[tr], D.iloc[te]
        w_opt, _ = coord_ascent(Dtr, W1, iters=8)
        hb.append(ndcg(Dte.assign(s=composite(Dte, W1)), 's'))
        ho.append(ndcg(Dte.assign(s=composite(Dte, w_opt)), 's'))

    w_ca, ndcg_ca = coord_ascent(D, W1, iters=20)
    lr = LogisticRegression(max_iter=2000, class_weight='balanced')
    lr.fit(D[COMPS].values / 100.0, D['rel'].values)
    coef = np.clip(lr.coef_[0], 0, None)
    w_lr = {c: round(float(v / coef.sum()), 4) for c, v in zip(COMPS, coef)} \
        if coef.sum() > 0 else dict(W1)

    print(f"\n=============== {dom} (live MiniLM) ===============")
    print(f"  heuristic NDCG@10        : {base:.4f}")
    print(f"  coordinate ascent weights: {w_ca}")
    print(f"     in-sample NDCG@10     : {ndcg_ca:.4f}")
    print(f"  logistic regression      : {w_lr}")
    print(f"     in-sample NDCG@10     : {ndcg(D.assign(s=composite(D, w_lr)), 's'):.4f}")
    print(f"  leave-one-job-out CV     : heuristic {np.mean(hb):.4f} | "
          f"learned {np.mean(ho):.4f}  (delta {np.mean(ho)-np.mean(hb):+.4f})")
    rows.append(dict(domain=dom, ndcg_heur=base, ndcg_ca=ndcg_ca,
                     cv_heur=np.mean(hb), cv_learned=np.mean(ho),
                     **{f'ca_{k}': v for k, v in w_ca.items()},
                     **{f'lr_{k}': v for k, v in w_lr.items()}))

    # ---- tier calibration on the live-MiniLM score ----
    D['S_match'] = composite(D, W1)
    tot = sum(W_RANK.values())
    D['S_rank'] = sum(D[c] * w for c, w in W_RANK.items()) / tot
    print(f"\n  S_rank: mean {D.S_rank.mean():.1f}  sd {D.S_rank.std():.1f}  "
          f"min {D.S_rank.min():.1f}  max {D.S_rank.max():.1f}")
    print(f"  {'tier':<15}{'n':>7}{'% pool':>9}{'precision':>11}{'lift':>7}")
    baserate = D['rel'].mean()
    for name, lo, hi in TIERS:
        m = (D.S_rank >= lo) & (D.S_rank < hi)
        n = int(m.sum())
        p = D.loc[m, 'rel'].mean() if n else float('nan')
        print(f"  {name:<15}{n:>7}{100*n/len(D):>8.1f}%{p:>11.3f}"
              f"{(p/baserate if n else float('nan')):>7.2f}")
        trows.append(dict(domain=dom, tier=name, n=n, pct=100*n/len(D),
                          precision=p, lift=(p/baserate if n else None)))
    print(f"  base rate = {baserate:.3f}")

pd.DataFrame(rows).to_csv(paths.out('minilm_weights.csv'), index=False)
pd.DataFrame(trows).to_csv(paths.out('minilm_thresholds.csv'), index=False)
print("\nsaved minilm_weights.csv and minilm_thresholds.csv")
