"""
Experiment 2 - Component ablation + learning-to-rank weight derivation
for the composite matching score (manuscript Section 7.1 / new Section 6.8).

Scoring functions are transcribed verbatim from resume_matcher.py and
candidate_ranker.py in the released repository. The only substitution is
S_semantic: the live all-MiniLM-L6-v2 sentence-transformer cannot be
downloaded in this sandbox, so a locally-fitted LSA (TruncatedSVD, 128 dims,
fit on the resume+JD corpus) dense embedding is used as a stand-in. This is
flagged in the manuscript.

Relevance proxy: a resume is relevant to a job description iff the resume's
ground-truth 'Job Role' equals the role the JD was written for. This gives a
graded-relevance signal without recruiter labels.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import re, json, itertools
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import kendalltau

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------- job descriptions
JD = {
 'AI Engineer': dict(title='AI Engineer', years=3, degree='bachelors',
   text="AI Engineer. We seek an AI Engineer with 3+ years experience to design and deploy machine learning and deep learning models. Requirements: bachelors degree; strong Python; TensorFlow or PyTorch; machine learning; data science; model deployment on AWS; SQL; Docker.",
   skills=['python','machine learning','tensorflow','pytorch','aws','sql','docker','data science']),
 'Cloud Engineer': dict(title='Cloud Engineer', years=3, degree='bachelors',
   text="Cloud Engineer. Seeking a Cloud Engineer with 3+ years experience building and operating cloud infrastructure. Requirements: bachelors degree; AWS and Azure; Docker; Kubernetes; Git; Python scripting; CI/CD pipelines; Linux.",
   skills=['aws','azure','docker','kubernetes','git','python']),
 'Data Scientist': dict(title='Data Scientist', years=3, degree='masters',
   text="Data Scientist. Data Scientist with 3+ years experience in statistical modelling and analytics. Requirements: masters degree preferred; Python; SQL; machine learning; data science; pandas; numpy; scikit-learn; data visualisation.",
   skills=['python','sql','machine learning','data science']),
 'Software Engineer': dict(title='Software Engineer', years=2, degree='bachelors',
   text="Software Engineer. Software Engineer with 2+ years experience building production backend services. Requirements: bachelors degree; Java or Python; SQL; Git; Docker; REST APIs; Spring or Flask; agile delivery.",
   skills=['java','python','sql','git','docker','flask','spring']),
 'Web Developer': dict(title='Web Developer', years=2, degree='bachelors',
   text="Web Developer. Web Developer with 2+ years experience building responsive single page applications. Requirements: bachelors degree; JavaScript; React; HTML; CSS; TypeScript; Node; Git; REST API integration.",
   skills=['javascript','react','html','css','typescript','node','git']),
 'Accountant': dict(title='Accountant', years=3, degree='bachelors',
   text="Accountant. Accountant with 3+ years experience in financial reporting and reconciliation. Requirements: bachelors degree in commerce or accounting; Excel; Tally; accounting; taxation; auditing; attention to detail; communication.",
   skills=['excel','accounting','communication']),
 'Business Analyst': dict(title='Business Analyst', years=3, degree='masters',
   text="Business Analyst. Business Analyst with 3+ years experience gathering requirements and delivering insight. Requirements: masters degree preferred; Excel; SQL; business analysis; stakeholder communication; reporting; data analysis; presentation.",
   skills=['excel','sql','communication','business analysis']),
 'Customer Support Representative': dict(title='Customer Support Representative', years=1, degree='bachelors',
   text="Customer Support Representative. Customer Support Representative with 1+ years experience resolving customer queries. Requirements: bachelors degree; customer service; communication; CRM and Salesforce; problem solving; empathy; ticketing systems.",
   skills=['customer service','communication','salesforce']),
 'Market Research Analyst': dict(title='Market Research Analyst', years=2, degree='bachelors',
   text="Market Research Analyst. Market Research Analyst with 2+ years experience running market studies. Requirements: bachelors degree; Excel; survey design; market research; data analysis; statistics; reporting; communication.",
   skills=['excel','market research','communication']),
 'Operations Manager': dict(title='Operations Manager', years=5, degree='bachelors',
   text="Operations Manager. Operations Manager with 5+ years experience leading operational teams. Requirements: bachelors degree; team management; operations; process improvement; Excel; communication; leadership; vendor management.",
   skills=['team management','excel','communication','operations']),
}
IT_ROLES  = ['AI Engineer','Cloud Engineer','Data Scientist','Software Engineer','Web Developer']
NON_ROLES = ['Accountant','Business Analyst','Customer Support Representative','Market Research Analyst','Operations Manager']

# ---------------------------------------------------------------- verbatim scorers
EDU_LEVELS = {'phd':4,'doctorate':4,'masters':3,'msc':3,'mba':3,'bachelors':2,'bsc':2,'btech':2,'be':2,'diploma':1}
def s_skills(cand_sk, job_sk):
    if not job_sk: return 100.0
    return len(set(cand_sk) & set(job_sk)) / len(set(job_sk)) * 100

def s_experience(cand_exp, job_exp):
    if job_exp == 0: return 100.0
    if cand_exp >= job_exp: return 100.0
    if cand_exp >= job_exp*0.7: return 80.0
    if cand_exp >= job_exp*0.5: return 60.0
    return (cand_exp/job_exp)*50

def s_education(cand_edu, req):
    cl = max([v for k,v in EDU_LEVELS.items() if k in cand_edu] or [0])
    rl = EDU_LEVELS.get(req,0)
    if rl == 0: return 100.0
    if cl >= rl: return 100.0
    if cl == rl-1: return 70.0
    return 40.0

# ---------------------------------------------------------------- build pairs
def build(df, roles, domain, n_per_role=120):
    exp_map = {'0-1 years':0.5,'1-3 years':2.0,'3-5 years':4.0,'5+ years':6.0}
    edu_map = {'Bachelor':'bachelors','Master':'masters','PhD':'phd','Diploma':'diploma'}
    cands = []
    for role in roles:
        sub = df[df['Job Role'] == role]
        take = sub.sample(min(n_per_role, len(sub)), random_state=42)
        for _, r in take.iterrows():
            sk = [s.strip().lower() for s in str(r['Skills']).split(',') if s.strip()]
            txt = ' '.join(str(r[c]) for c in ['Projects','Skills','Certifications','Courses','Keywords','Technologies'] if c in r)
            cands.append(dict(role=role, skills=sk, exp=exp_map.get(str(r['Experience']),0),
                              edu=edu_map.get(str(r['Education_Level']),'bachelors').lower(),
                              text=txt + ' ' + str(r['Education_Level']) + ' ' + str(r['Experience'])))
    return cands

it  = pd.read_csv(paths.IT_CSV)
non = pd.read_csv(paths.NONIT_CSV)
CAND = {'IT': build(it, IT_ROLES,'IT'), 'Non-IT': build(non, NON_ROLES,'Non-IT')}
print("candidates:", {k: len(v) for k, v in CAND.items()})

def score_matrix(cands, roles):
    """Return DataFrame of one row per (candidate, job) pair with all 5 components."""
    corpus = [c['text'] for c in cands] + [JD[r]['text'] for r in roles]
    tf = TfidfVectorizer(max_features=500, stop_words='english', ngram_range=(1,2))
    X = tf.fit_transform(corpus)
    svd = TruncatedSVD(n_components=min(128, X.shape[1]-1), random_state=42)
    Z = svd.fit_transform(X)
    nC = len(cands)
    Kw = cosine_similarity(X[:nC], X[nC:]) * 100          # S_keyword (TF-IDF cosine, as implemented)
    Sem = np.clip(cosine_similarity(Z[:nC], Z[nC:]), 0, 1) * 100   # S_semantic stand-in (LSA)
    rows = []
    for i, c in enumerate(cands):
        for j, r in enumerate(roles):
            jd = JD[r]
            rows.append(dict(cand=i, job=r, rel=int(c['role'] == r),
                S_skills=s_skills(c['skills'], jd['skills']),
                S_experience=s_experience(c['exp'], jd['years']),
                S_education=s_education(c['edu'], jd['degree']),
                S_keyword=float(Kw[i, j]), S_semantic=float(Sem[i, j])))
    return pd.DataFrame(rows)

W1 = dict(S_skills=.35, S_experience=.20, S_education=.15, S_keyword=.15, S_semantic=.15)
COMPS = list(W1)

def composite(d, w):
    tot = sum(w.values())
    return sum(d[c]*w.get(c,0) for c in COMPS) / (tot if tot else 1)

def ndcg_at_k(df, score_col, k=10):
    """Mean NDCG@k over jobs: rank candidates for each job."""
    out = []
    for job, g in df.groupby('job'):
        g = g.sort_values(score_col, ascending=False)
        rel = g['rel'].values[:k]
        dcg = np.sum(rel / np.log2(np.arange(2, len(rel)+2)))
        ideal = np.sort(g['rel'].values)[::-1][:k]
        idcg = np.sum(ideal / np.log2(np.arange(2, len(ideal)+2)))
        out.append(dcg/idcg if idcg > 0 else 0.0)
    return float(np.mean(out))

def prec_at_k(df, score_col, k=10):
    out = []
    for job, g in df.groupby('job'):
        out.append(g.nlargest(k, score_col)['rel'].mean())
    return float(np.mean(out))

if __name__ == '__main__':
    results = {}
    for dom, roles in [('IT', IT_ROLES), ('Non-IT', NON_ROLES)]:
        D = score_matrix(CAND[dom], roles)
        D['full'] = composite(D, W1)
        base_ndcg, base_p10 = ndcg_at_k(D,'full'), prec_at_k(D,'full')
        print(f"\n================ {dom} ================")
        print(f"FULL model  NDCG@10 = {base_ndcg:.4f}   P@10 = {base_p10:.4f}")
        print(f"{'ablated component':<16} {'NDCG@10':>9} {'delta':>8} {'P@10':>7} {'delta':>8} {'Kendall tau':>12} {'tier-flip %':>12}")
        abl = []
        for comp in COMPS:
            w = {k: v for k, v in W1.items() if k != comp}
            col = f'abl_{comp}'
            D[col] = composite(D, w)
            n2, p2 = ndcg_at_k(D, col), prec_at_k(D, col)
            tau = np.mean([kendalltau(g['full'], g[col])[0] for _, g in D.groupby('job')])
            def tier(s): return np.digitize(s, [40,55,70,85])
            flip = float(np.mean(tier(D['full'].values) != tier(D[col].values))*100)
            print(f"{comp:<16} {n2:9.4f} {n2-base_ndcg:+8.4f} {p2:7.4f} {p2-base_p10:+8.4f} {tau:12.4f} {flip:12.1f}")
            abl.append(dict(domain=dom, component=comp, ndcg=n2, d_ndcg=n2-base_ndcg,
                            p10=p2, d_p10=p2-base_p10, tau=tau, tier_flip=flip))
        results[dom] = (D, base_ndcg, base_p10, abl)

    pd.DataFrame([r for d in results for r in results[d][3]]).to_csv(paths.out('ablation.csv'), index=False)
    import pickle
    pickle.dump({d:(results[d][0], results[d][1], results[d][2]) for d in results}, open(paths.out('scored.pkl'),'wb'))
    print("\nsaved ablation.csv + scored.pkl")
