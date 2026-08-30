# SmartCareer — analysis scripts for the paper

Every quantitative claim in *"SmartCareer: An AI-Powered Integrated Career Development
and Recruitment Intelligence Platform"* can be reproduced from this directory.
Each script writes its results to a `.csv` or `.json` file alongside itself.


## Windows

Everything runs on Windows. Three differences from the commands shown below:

- Use `python` (or `py`) instead of `python3`.
- Set environment variables with `set` in Command Prompt, or `$env:` in PowerShell,
  not `export`.
- `ffmpeg` is not bundled. You only need it for `exp1b` / `exp1c` (the audio scripts);
  install with `winget install Gyan.FFmpeg`, then reopen the terminal so it is on PATH.

Console output is forced to UTF-8 by `paths.py`, so the default cp1252 code page will
not break printing of skill names. `spaCy` is optional: if it is not installed the
parser falls back automatically, which is fine because none of these analyses use its
code path.

```bat
cd SmartCareer_Project\analysis
python paths.py
pip install numpy pandas scipy scikit-learn sentence-transformers
python exp2_ablation.py
python rerun_ablation_minilm.py
```

If `paths.py` reports a missing location:

```bat
set SMARTCAREER_REPO=C:\path\to\SmartCareer_Project
set SMARTCAREER_CORPORA=C:\path\to\corpora
```

PowerShell uses `$env:SMARTCAREER_REPO = "C:\path\to\SmartCareer_Project"` instead.

## Where to put this folder

Drop it inside your project repo as `analysis/`. Paths are resolved automatically:

```
SmartCareer_Project/
    candidate_parser.py
    resume_data_IT_5000_updated.csv
    analysis/          <- this folder
```

Check the resolution before running anything:

```bash
cd SmartCareer_Project/analysis
python paths.py          # every line should show [x]
```

If a line shows `[ ]`, point the script at the right place:

```bash
export SMARTCAREER_REPO=/path/to/SmartCareer_Project
export SMARTCAREER_CORPORA=/path/to/where/you/cloned/the/corpora
```

## Setup

```bash
pip install numpy pandas scipy scikit-learn librosa soundfile requests flask mongomock PyPDF2 docx2txt
```

`exp1*` additionally needs `ffmpeg` on the PATH, because the browser-recorded answer
clips in `static/audio/` are WebM containers despite their `.wav` extension:

```bash
mkdir -p wav_native
for f in static/audio/*_a*.wav; do
  [ -s "$f" ] && ffmpeg -y -v error -i "$f" -ac 1 "wav_native/$(basename "$f")"
done
```

## Scripts

| Script | Manuscript section | Produces |
|---|---|---|
| `exp6_qbank.py` | 5.2.1 | Bloom's-taxonomy and behavioural-stem analysis of the question bank (Table 5) |
| `exp5_real220.py` | 7.4.1 | Parser evaluation on the 220-resume replication corpus |
| `exp5b_coverage.py` | 7.4.1 | Skill-vocabulary coverage, replication corpus (Table 10, right column) |
| `exp8_corpus349.py` | 7.4.1 | Skill-vocabulary coverage, primary corpus (Table 10, left column) |
| `exp1b_audio.py` | 7.6 | Correlation of each clarity feature with the background-noise floor |
| `exp1c_noise_injection.py` | 7.6.1 | Pink-noise injection at 0-20 dB SNR; drift and rank stability (Table 12) |
| `rerun_ablation_minilm.py` | 7.9 | **Component ablation (Table 14)** - live MiniLM encoder |
| `rerun_weights_minilm.py` | 7.10, 7.11 | **Learned weights (Table 15) and tier calibration (Table 16)** - live MiniLM |
| `exp4_api_bench.py` | 7.12 | End-to-end HTTP latency and throughput (Tables 17, 18) |
| `exp7_a11y.py` | 7.13 | Static WCAG 2.1 Level A/AA audit of the React frontend (Table 19) |
| `verify_corpus_deidentification.py` | 7.4.1 | Screening of both corpora for residual personal data |
| `exp2_ablation.py` | - | Prerequisite for the two `rerun_*` scripts; also runs a latent-semantic baseline |
| `exp3_weights_thresholds.py` | - | Latent-semantic baseline for weights and tiers |
| `exp3b_recalibrate.py` | 7.11 | Quantile-based threshold recalibration |

**Important.** Tables 14, 15 and 16 in the paper are produced by `rerun_ablation_minilm.py`
and `rerun_weights_minilm.py`, which use the deployed `all-MiniLM-L6-v2` encoder.
`exp2_ablation.py` and `exp3_weights_thresholds.py` use a locally fitted latent-semantic
model instead, and give different numbers. They are retained because `exp2` must run first
to build the candidate-job pairs, and because the difference between the two is itself
discussed in Section 7.9. Do not compare their output against Tables 14-16.

Run order for the matching results:

```
python exp2_ablation.py            # builds the pairs, writes scored.pkl
python rerun_ablation_minilm.py    # Table 14
python rerun_weights_minilm.py     # Tables 15 and 16
```

`exp2_ablation.py` must be run before `exp3_weights_thresholds.py`, `exp3b_recalibrate.py`
and the two `rerun_*` scripts, all of which depend on what it writes.

The `.csv` and `.json` files shipped alongside these scripts are the outputs from our own
runs, for comparison. This includes the live-encoder results behind Tables 14, 15 and 16:

| File | Contains |
|---|---|
| `minilm_scores_IT.csv`, `minilm_scores_Non-IT.csv` | Per-pair component scores and every ablation column, 3,000 rows per domain. Tables 14 is derived from these. |
| `minilm_weights.csv` | Coordinate-ascent and logistic-regression weights, in-sample and leave-one-job-out NDCG@10 (Table 15) |
| `minilm_thresholds.csv` | Tier populations, precision and lift (Table 16) |

Every figure in Tables 14, 15 and 16 can be recomputed directly from the two score
matrices without re-running the encoder.


## Re-running the ablation with the live MiniLM encoder

The ablation and weight derivation in the manuscript computed `S_semantic` with a
locally fitted latent-semantic model, because the environment that produced them
could not download the `all-MiniLM-L6-v2` weights. Re-run it with the real encoder
on a machine with internet access:

```bash
cd SmartCareer_Project/analysis
python paths.py                          # confirm every line shows [x]
pip install sentence-transformers
python exp2_ablation.py                  # baseline, writes scored.pkl
python rerun_ablation_minilm.py          # downloads ~90 MB on first run
python rerun_weights_minilm.py           # re-derives weights + tiers from those scores
```

Expect 5-10 minutes: most of it is the one-time model download, then about a minute
of encoding for 1,200 documents.

**Reading the result.** Compare the `delta` column against **Table 14** of the
manuscript. The claim that matters is the *sign* on `S_skills`: the paper argues that
removing it **improves** ranking quality, so its delta should stay positive in both
domains.

- Sign holds -> the conclusion stands. Delete the stand-in caveat in Sections 7.9 and
  8.4, and add one sentence saying the analysis was confirmed with the deployed encoder.
- Sign flips, or `S_semantic` changes materially -> update Tables 14 and 15 with the new
  numbers and revise the surrounding text in Sections 7.9 and 7.10.

Either way keep `minilm_scores_IT.csv` and `minilm_scores_Non-IT.csv`; they are the
evidence for whichever statement you make.

## External corpora (not redistributed here)

Section 7.4.1 uses two third-party annotated resume corpora. Neither is included in
this repository. Clone them next to it before running `exp5*` or `exp8*`:

```bash
git clone https://github.com/vrundag91/Resume-Corpus-Dataset.git          # primary, 349 resumes
git clone https://github.com/DataTurks-Engg/Entity-Recognition-In-Resumes-SpaCy.git  # replication, 220
```

The primary corpus is published for academic and research use. The replication corpus
carries no declared licence and is used here for non-commercial evaluation only, with
aggregate metrics reported and no documents redistributed.

## Known substitution

The ablation and weight-derivation runs reported in the manuscript computed
`S_semantic` with a locally fitted latent-semantic model rather than the deployed
`all-MiniLM-L6-v2` encoder, because the environment that produced them could not reach
the model-weights host. `rerun_ablation_minilm.py` repeats the identical analysis with
the real encoder on a machine with internet access. This substitution is disclosed in
Sections 7.9 and 8.4 of the manuscript and should be removed once the re-run confirms
the numbers.

## Fixed defect

`repo_patch/` contains the corrected `candidate_ranker.py` and its regression tests,
addressing the scoring defect documented in Section 6.10: the ranking criteria named a
key (`overallScore`) that `ResumeMatcher` never emits (`matchScore`), so 0.40 of the
weight mass was silently discarded, capping the attainable score at 60 and making the
`Excellent` and `Strong` tiers unreachable. Run `python test_candidate_ranker.py` — it
fails 4 of 6 tests against the original file and passes all 6 against the patched one.
