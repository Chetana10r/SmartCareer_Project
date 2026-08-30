"""
Experiment 4 - End-to-end API latency and throughput benchmark (Reviewer 5, point 7).

Measures FULL HTTP request latency: client socket -> werkzeug WSGI server ->
Flask routing/blueprint dispatch -> JSON deserialisation -> database query ->
scoring computation -> JSON serialisation -> client.

The database is mongomock, configured with the same collections and indexes
declared in the manuscript (jobs, shortlist, users). Scoring uses the verbatim
component functions from resume_matcher.py / candidate_ranker.py. spaCy and the
SBERT encoder are replaced by a pre-fitted TF-IDF+LSA vectoriser, so the
semantic component's cost is representative of a cached vectoriser rather than
of transformer inference; this is stated explicitly in the manuscript.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import json, time, threading, statistics, sys
import numpy as np, pandas as pd, requests
from flask import Flask, Blueprint, request, jsonify, current_app
import mongomock
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.serving import make_server

# ---------------- data ----------------
it = pd.read_csv(paths.IT_CSV)
EXP = {'0-1 years':0.5,'1-3 years':2.0,'3-5 years':4.0,'5+ years':6.0}
EDU = {'Bachelor':'bachelors','Master':'masters','PhD':'phd','Diploma':'diploma'}
def cand_docs(n):
    out=[]
    for i,(_,r) in enumerate(it.head(n).iterrows()):
        out.append(dict(_id=f"c{i}", name=f"Candidate {i}", email=f"c{i}@example.com",
            role='candidate',
            skills=[s.strip().lower() for s in str(r['Skills']).split(',') if s.strip()],
            experience=EXP.get(str(r['Experience']),0), education=EDU.get(str(r['Education_Level']),'bachelors'),
            summary=str(r['Keywords']), projects=str(r['Projects']),
            achievements=str(r['Certifications'])))
    return out

JOB = dict(_id="j1", title="AI Engineer", company="Acme", status="active", recruiterId="r1",
  description="AI Engineer with 3+ years experience to build machine learning and deep learning models.",
  requirements="bachelors degree; python; tensorflow; pytorch; machine learning; data science; aws; sql; docker",
  skills=['python','machine learning','tensorflow','pytorch','aws','sql','docker','data science'])

# ---------------- verbatim scorers ----------------
EDU_LEVELS={'phd':4,'doctorate':4,'masters':3,'msc':3,'mba':3,'bachelors':2,'bsc':2,'btech':2,'be':2,'diploma':1}
TECH=['python','java','javascript','react','node','sql','mongodb','aws','azure','docker','kubernetes','git',
 'machine learning','data science','flask','django','spring','angular','vue','tensorflow','pytorch','html','css',
 'typescript','c++','c#','php','ruby','go','rust','scala','kotlin','swift']
def job_skills(job):
    s=set(job.get('skills',[]))
    t=job.get('requirements','').lower()
    s|={k for k in TECH if k in t}
    return s
def sc_skills(cs,js): return 100.0 if not js else len(set(cs)&js)/len(js)*100
def sc_exp(ce,je):
    if je==0: return 100.0
    if ce>=je: return 100.0
    if ce>=je*.7: return 80.0
    if ce>=je*.5: return 60.0
    return ce/je*50
def sc_edu(ce,jt):
    cl=max([v for k,v in EDU_LEVELS.items() if k in ce] or [0])
    rl=max([v for k,v in EDU_LEVELS.items() if k in jt] or [0])
    if rl==0: return 100.0
    if cl>=rl: return 100.0
    if cl==rl-1: return 70.0
    return 40.0
W=dict(skills=.35,experience=.20,education=.15,keyword=.15,semantic=.15)
RANKW=dict(matchScore=.40,skillsMatch=.25,experienceMatch=.20,educationMatch=.10,semanticMatch=.05)
def tier(s):
    return 'Excellent' if s>=85 else 'Strong' if s>=70 else 'Good' if s>=55 else 'Average' if s>=40 else 'Below Average'

# ---------------- app ----------------
def build_app(n_cand):
    app=Flask(__name__)
    client=mongomock.MongoClient(); db=client['smartcareer']
    docs=cand_docs(n_cand); db.users.insert_many([dict(d) for d in docs]); db.jobs.insert_one(dict(JOB))
    db.jobs.create_index('recruiterId'); db.jobs.create_index('status'); db.jobs.create_index([('createdAt',-1)])
    db.shortlist.create_index('jobId'); db.shortlist.create_index('candidateId')
    db.shortlist.create_index([('matchScore',-1)]); db.shortlist.create_index([('candidateId',1),('jobId',1)],unique=True)
    corpus=[d['summary']+' '+d['projects'] for d in docs]+[JOB['description']+' '+JOB['requirements']]
    tf=TfidfVectorizer(max_features=500,stop_words='english',ngram_range=(1,2)); X=tf.fit_transform(corpus)
    svd=TruncatedSVD(n_components=min(128,X.shape[1]-1),random_state=42); Z=svd.fit_transform(X)
    app.config['db']=db; app.config['tf']=tf; app.config['svd']=svd
    app.config['jobvec']=(X[-1],Z[-1:])

    bp=Blueprint('recruiter',__name__)

    @bp.route('/jobs',methods=['GET'])
    def get_jobs():
        db=current_app.config['db']
        jobs=list(db.jobs.find({'recruiterId':request.args.get('recruiterId','r1')}))
        for j in jobs: j['_id']=str(j['_id'])
        return jsonify(dict(success=True,jobs=jobs))

    @bp.route('/shortlist',methods=['POST'])
    def add_shortlist():
        db=current_app.config['db']; d=request.get_json()
        db.shortlist.update_one({'candidateId':d['candidateId'],'jobId':d['jobId']},
                                {'$set':{**d,'status':'shortlisted'}},upsert=True)
        n=db.shortlist.count_documents({'jobId':d['jobId']})
        db.jobs.update_one({'_id':d['jobId']},{'$set':{'shortlistCount':n}})
        return jsonify(dict(success=True,shortlistCount=n))

    @bp.route('/match-resumes',methods=['POST'])
    def match():
        db=current_app.config['db']; body=request.get_json()
        limit=int(body.get('limit',50))
        job=db.jobs.find_one({'_id':body.get('jobId','j1')})
        cands=list(db.users.find({'role':'candidate'}).limit(limit))
        tf=current_app.config['tf']; svd=current_app.config['svd']
        jx,jz=current_app.config['jobvec']
        js=job_skills(job); jt=(job.get('requirements','')+' '+job.get('description','')).lower()
        je=3
        texts=[c.get('summary','')+' '+c.get('projects','') for c in cands]
        Xc=tf.transform(texts); Zc=svd.transform(Xc)
        kw=cosine_similarity(Xc,jx)[:,0]*100
        sem=np.clip(cosine_similarity(Zc,jz)[:,0],0,1)*100
        out=[]
        for i,c in enumerate(cands):
            ss=sc_skills(set(c.get('skills',[])),js); se=sc_exp(c.get('experience',0),je)
            sd=sc_edu(c.get('education','').lower(),jt)
            overall=ss*W['skills']+se*W['experience']+sd*W['education']+kw[i]*W['keyword']+sem[i]*W['semantic']
            rec=dict(candidateId=str(c['_id']),candidateName=c.get('name'),matchScore=round(overall,2),
                     skillsMatch=round(ss,2),experienceMatch=round(se,2),educationMatch=round(sd,2),
                     keywordMatch=round(float(kw[i]),2),semanticMatch=round(float(sem[i]),2))
            comp=sum(rec[k]*v for k,v in RANKW.items())
            rec['compositeScore']=round(comp,2); rec['tier']=tier(comp)
            out.append(rec)
        out.sort(key=lambda x:-x['compositeScore'])
        for i,r in enumerate(out): r['rank']=i+1
        return jsonify(dict(success=True,count=len(out),matches=out))

    app.register_blueprint(bp,url_prefix='/api/recruiter')
    return app

class Server(threading.Thread):
    def __init__(self,app,port):
        super().__init__(daemon=True)
        self.srv=make_server('127.0.0.1',port,app,threaded=True); self.ctx=app.app_context(); self.ctx.push()
    def run(self): self.srv.serve_forever()
    def stop(self): self.srv.shutdown()

def bench(url,method='GET',payload=None,n=200,warm=20):
    s=requests.Session()
    for _ in range(warm):
        s.get(url) if method=='GET' else s.post(url,json=payload)
    lat=[]
    for _ in range(n):
        t=time.perf_counter()
        r=s.get(url) if method=='GET' else s.post(url,json=payload)
        lat.append((time.perf_counter()-t)*1000); assert r.status_code==200,r.text[:200]
    a=np.array(lat)
    return dict(mean=a.mean(),p50=np.percentile(a,50),p95=np.percentile(a,95),p99=np.percentile(a,99),
                mn=a.min(),mx=a.max())

def throughput(url,method,payload,conc,duration=6.0):
    stop=time.time()+duration; counts=[0]*conc; errs=[0]*conc; lats=[[] for _ in range(conc)]
    def worker(i):
        s=requests.Session()
        while time.time()<stop:
            t=time.perf_counter()
            try:
                r=s.get(url) if method=='GET' else s.post(url,json=payload)
                if r.status_code==200: counts[i]+=1; lats[i].append((time.perf_counter()-t)*1000)
                else: errs[i]+=1
            except Exception: errs[i]+=1
    th=[threading.Thread(target=worker,args=(i,)) for i in range(conc)]
    t0=time.time(); [t.start() for t in th]; [t.join() for t in th]
    el=time.time()-t0; tot=sum(counts); all_l=np.array([x for l in lats for x in l])
    return dict(conc=conc,rps=tot/el,n=tot,err=sum(errs),
                p50=np.percentile(all_l,50) if len(all_l) else 0,
                p95=np.percentile(all_l,95) if len(all_l) else 0)

if __name__=='__main__':
    PORT=8731
    app=build_app(500); srv=Server(app,PORT); srv.start(); time.sleep(1.2)
    B=f'http://127.0.0.1:{PORT}/api/recruiter'
    print("="*92); print("A. SINGLE-REQUEST END-TO-END HTTP LATENCY (n=200 after 20 warm-up)"); print("="*92)
    print(f"{'endpoint':<44}{'mean':>8}{'p50':>8}{'p95':>8}{'p99':>8}{'min':>8}{'max':>9}")
    cases=[('GET  /jobs  (indexed Mongo query)','GET',f'{B}/jobs',None),
           ('POST /shortlist (upsert + count + update)','POST',f'{B}/shortlist',dict(candidateId='c1',jobId='j1',matchScore=71.2)),
           ('POST /match-resumes  limit=10','POST',f'{B}/match-resumes',dict(jobId='j1',limit=10)),
           ('POST /match-resumes  limit=50','POST',f'{B}/match-resumes',dict(jobId='j1',limit=50)),
           ('POST /match-resumes  limit=100','POST',f'{B}/match-resumes',dict(jobId='j1',limit=100)),
           ('POST /match-resumes  limit=500','POST',f'{B}/match-resumes',dict(jobId='j1',limit=500))]
    rows=[]
    for label,m,u,p in cases:
        r=bench(u,m,p,n=200)
        print(f"{label:<44}{r['mean']:>8.2f}{r['p50']:>8.2f}{r['p95']:>8.2f}{r['p99']:>8.2f}{r['mn']:>8.2f}{r['mx']:>9.2f}")
        rows.append(dict(endpoint=label,**r))
    pd.DataFrame(rows).to_csv(paths.out('api_latency.csv'),index=False)

    print("\n"+"="*92); print("B. THROUGHPUT UNDER CONCURRENCY (6 s sustained load per level)"); print("="*92)
    print(f"{'endpoint':<34}{'clients':>9}{'req/s':>10}{'p50 ms':>10}{'p95 ms':>10}{'errors':>9}")
    trows=[]
    for label,m,u,p in [('GET /jobs','GET',f'{B}/jobs',None),
                        ('POST /match-resumes limit=50','POST',f'{B}/match-resumes',dict(jobId='j1',limit=50))]:
        for c in (1,4,8,16):
            r=throughput(u,m,p,c)
            print(f"{label:<34}{c:>9}{r['rps']:>10.1f}{r['p50']:>10.2f}{r['p95']:>10.2f}{r['err']:>9}")
            trows.append(dict(endpoint=label,**r))
    pd.DataFrame(trows).to_csv(paths.out('api_throughput.csv'),index=False)
    srv.stop(); print("\ndone")
