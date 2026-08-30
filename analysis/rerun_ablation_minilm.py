"""
Re-run the component ablation and learning-to-rank weight derivation using the
LIVE all-MiniLM-L6-v2 sentence-transformer, replacing the TF-IDF+LSA stand-in
used when the model could not be downloaded.

WHY THIS EXISTS
---------------
Sections 7.9 and 7.10 of the manuscript report the ablation and weight
derivation. S_semantic in those runs was computed with a locally fitted latent
semantic model because the sandbox that produced them had no access to the
model weights host. This script reproduces the identical analysis with the real
encoder so that caveat can be removed from the paper.

REQUIREMENTS
------------
    pip install sentence-transformers scikit-learn pandas scipy
Needs internet access on first run (downloads ~90 MB of model weights).

USAGE
-----
    python rerun_ablation_minilm.py

Then compare the printed numbers against Tables 14 and 15 in the manuscript.
If they differ materially, update those tables and delete the stand-in caveat
in Sections 7.9, 7.10 and 8.4. If they agree, keep the tables and simply state
that the analysis was confirmed with the deployed encoder.
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    sys.exit("Install first:  pip install sentence-transformers")

import numpy as np
import exp2_ablation as A          # reuses the job descriptions and scorers
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

print("loading all-MiniLM-L6-v2 (downloads on first run)...")
MODEL = SentenceTransformer('all-MiniLM-L6-v2')
print("loaded.\n")


def score_matrix_minilm(cands, roles):
    """Identical to exp2_ablation.score_matrix but S_semantic uses real MiniLM."""
    texts = [c['text'] for c in cands]
    jd_texts = [A.JD[r]['text'] for r in roles]

    tf = TfidfVectorizer(max_features=500, stop_words='english', ngram_range=(1, 2))
    X = tf.fit_transform(texts + jd_texts)
    nC = len(cands)
    Kw = cosine_similarity(X[:nC], X[nC:]) * 100                      # S_keyword

    Ec = MODEL.encode(texts, batch_size=64, show_progress_bar=True,
                      normalize_embeddings=True)
    Ej = MODEL.encode(jd_texts, normalize_embeddings=True)
    Sem = np.clip(cosine_similarity(Ec, Ej), 0, 1) * 100              # S_semantic (live)

    rows = []
    for i, c in enumerate(cands):
        for j, r in enumerate(roles):
            jd = A.JD[r]
            rows.append(dict(cand=i, job=r, rel=int(c['role'] == r),
                             S_skills=A.s_skills(c['skills'], jd['skills']),
                             S_experience=A.s_experience(c['exp'], jd['years']),
                             S_education=A.s_education(c['edu'], jd['degree']),
                             S_keyword=float(Kw[i, j]),
                             S_semantic=float(Sem[i, j])))
    return pd.DataFrame(rows)


if __name__ == '__main__':
    out = {}
    for dom, roles in [('IT', A.IT_ROLES), ('Non-IT', A.NON_ROLES)]:
        D = score_matrix_minilm(A.CAND[dom], roles)
        D['full'] = A.composite(D, A.W1)
        base_n, base_p = A.ndcg_at_k(D, 'full'), A.prec_at_k(D, 'full')
        print(f"\n================ {dom} (live MiniLM) ================")
        print(f"FULL model  NDCG@10 = {base_n:.4f}   P@10 = {base_p:.4f}")
        print(f"{'ablated':<16}{'NDCG@10':>9}{'delta':>9}{'P@10':>8}{'delta':>9}")
        for comp in A.COMPS:
            w = {k: v for k, v in A.W1.items() if k != comp}
            col = f'abl_{comp}'
            D[col] = A.composite(D, w)
            n2, p2 = A.ndcg_at_k(D, col), A.prec_at_k(D, col)
            print(f"{comp:<16}{n2:9.4f}{n2-base_n:+9.4f}{p2:8.4f}{p2-base_p:+9.4f}")
        out[dom] = D
        D.to_csv(os.path.join(HERE, f'minilm_scores_{dom}.csv'), index=False)

    print("\nCompare against Table 14 (ablation) and Table 15 (weights) in the manuscript.")
    print("Per-domain score matrices written to minilm_scores_*.csv")
