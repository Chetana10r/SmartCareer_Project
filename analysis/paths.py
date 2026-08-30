"""
Path resolution for the SmartCareer analysis scripts.

Every script imports this instead of hardcoding paths, so the package runs
unchanged wherever you put it.

Layout assumed by default -- the analysis folder sits inside the project repo:

    SmartCareer_Project/
        candidate_parser.py
        resume_data_IT_5000_updated.csv
        config/question_templates.json
        skills_recommender/src/...
        static/audio/
        analysis/            <- this folder
            paths.py
            exp2_ablation.py
            ...

Override any location with an environment variable if your layout differs:

    export SMARTCAREER_REPO=/path/to/SmartCareer_Project
    export SMARTCAREER_CORPORA=/path/to/where/you/cloned/the/corpora
    export SMARTCAREER_OUT=/path/for/results
"""
import os, sys

# Windows consoles default to cp1252 and crash when a script prints a skill name
# or box character outside that range. Force UTF-8 for stdout/stderr.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo():
    env = os.environ.get('SMARTCAREER_REPO')
    if env:
        return os.path.abspath(env)
    # walk upwards looking for a marker file from the project
    d = HERE
    for _ in range(4):
        if os.path.exists(os.path.join(d, 'candidate_parser.py')):
            return d
        d = os.path.dirname(d)
    return os.path.dirname(HERE)          # best guess: parent of analysis/


REPO = _find_repo()
OUT = os.path.abspath(os.environ.get('SMARTCAREER_OUT', HERE))
CORPORA = os.path.abspath(os.environ.get('SMARTCAREER_CORPORA',
                                         os.path.dirname(REPO)))

# make the project importable (candidate_parser, candidate_ranker, ...)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# --- project files -------------------------------------------------------
IT_CSV       = os.path.join(REPO, 'resume_data_IT_5000_updated.csv')
NONIT_CSV    = os.path.join(REPO, 'resume_data_Non_IT_5000_updated.csv')
QTEMPLATES   = os.path.join(REPO, 'config', 'question_templates.json')
FRONTEND_SRC = os.path.join(REPO, 'skills_recommender', 'src', '**', '*.js')
AUDIO_RAW    = os.path.join(REPO, 'static', 'audio', '*_a*.wav')
AUDIO_WAV    = os.path.join(OUT, 'wav_native', '*.wav')

# --- external corpora (cloned separately; see README) --------------------
CORPUS349 = os.path.join(CORPORA, 'Resume-Corpus-Dataset', 'data-files', '*.json')
CORPUS220_TRAIN = os.path.join(CORPORA, 'Entity-Recognition-In-Resumes-SpaCy', 'traindata.json')
CORPUS220_TEST  = os.path.join(CORPORA, 'Entity-Recognition-In-Resumes-SpaCy', 'testdata.json')


def out(name):
    """Absolute path for a result file."""
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def require(path, hint=''):
    """Fail with a useful message rather than a confusing traceback."""
    if '*' in path:
        import glob
        if glob.glob(path, recursive=True):
            return path
    elif os.path.exists(path):
        return path
    raise SystemExit(
        f"\nNot found: {path}\n"
        + (f"  {hint}\n" if hint else '')
        + f"  REPO    = {REPO}\n  CORPORA = {CORPORA}\n"
        "  Set SMARTCAREER_REPO / SMARTCAREER_CORPORA if these are wrong.\n")



# candidate_parser imports spaCy at module level, but none of these analyses use
# the spaCy code path (it serves name extraction only). If spaCy or its model is
# not installed, register a stub so the parser still imports and falls back, as
# it is already written to do.
def _ensure_spacy():
    try:
        import spacy  # noqa: F401
        return 'present'
    except ImportError:
        import types
        stub = types.ModuleType('spacy')
        def _load(*a, **k):
            raise OSError('spaCy model unavailable; parser uses its fallback path')
        stub.load = _load
        sys.modules['spacy'] = stub
        return 'stubbed'


SPACY = _ensure_spacy()

if __name__ == '__main__':
    print(f"HERE    = {HERE}\nREPO    = {REPO}\nCORPORA = {CORPORA}\nOUT     = {OUT}\n")
    for label, p in [('IT csv', IT_CSV), ('non-IT csv', NONIT_CSV),
                     ('question templates', QTEMPLATES), ('frontend src', FRONTEND_SRC),
                     ('raw audio', AUDIO_RAW), ('corpus 349', CORPUS349),
                     ('corpus 220', CORPUS220_TRAIN)]:
        import glob
        ok = bool(glob.glob(p, recursive=True)) if '*' in p else os.path.exists(p)
        print(f"  [{'x' if ok else ' '}] {label:20s} {p}")
