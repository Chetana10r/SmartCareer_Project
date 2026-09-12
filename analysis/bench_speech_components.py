"""
Benchmark the three inference components excluded from the Section 7.12 API
benchmark: speech-to-text (faster-whisper), text-to-speech (Coqui TTS), and
the sentence-transformer encoder (all-MiniLM-L6-v2).

Run from SmartCareer_Project/analysis on a machine with internet access:

    pip install faster-whisper sentence-transformers
    pip install TTS                 # optional; skipped automatically if absent
    python bench_speech_components.py

Writes speech_bench.csv and prints a summary table.

Notes
-----
* STT is measured on the real answer recordings in static/audio. Those files are
  WebM containers despite the .wav extension; faster-whisper decodes them through
  PyAV, so no external ffmpeg installation is needed.
* Model download happens on first run (~150 MB for Whisper base, ~120 MB TTS).
* Cold-start (first call, model load) is reported separately from steady-state,
  because they have very different deployment implications.
"""
import os, sys, glob, time, json, subprocess, statistics, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

import numpy as np
import pandas as pd

OUT = []


def record(component, phase, n, times_ms, extra=None):
    a = np.array(times_ms, dtype=float)
    row = dict(component=component, phase=phase, n=n,
               mean_ms=a.mean(), p50_ms=np.percentile(a, 50),
               p95_ms=np.percentile(a, 95), min_ms=a.min(), max_ms=a.max())
    if extra:
        row.update(extra)
    OUT.append(row)
    print(f"  {component:<22} {phase:<12} n={n:<4} mean={a.mean():9.1f} ms   "
          f"p50={np.percentile(a,50):9.1f}   p95={np.percentile(a,95):9.1f}")


# ---------------------------------------------------------------- audio prep
def prepare_audio(limit=20):
    """
    Return the real answer recordings as-is.

    These files carry a .wav extension but are WebM/Opus containers written by
    the browser MediaRecorder. faster-whisper decodes through PyAV, which sniffs
    the container and handles this natively, so no external ffmpeg is required.
    """
    raw = sorted(glob.glob(paths.AUDIO_RAW))
    return [f for f in raw if os.path.getsize(f) > 0][:limit]


# ---------------------------------------------------------------- 1. STT
def bench_stt(clips):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  faster-whisper not installed - SKIPPED"); return
    if not clips:
        print("  no audio clips found - SKIPPED"); return

    t0 = time.perf_counter()
    model = WhisperModel("base", device="cpu", compute_type="int8")
    load_ms = (time.perf_counter() - t0) * 1000
    record("Whisper base (STT)", "model load", 1, [load_ms])

    # first transcription separately: includes lazy graph warm-up
    try:
        t0 = time.perf_counter()
        segs, info = model.transcribe(clips[0])
        list(segs)
        record("Whisper base (STT)", "cold call", 1, [(time.perf_counter() - t0) * 1000])
    except Exception as e:
        print(f"  could not decode audio: {e}")
        print("  SKIPPED - try: pip install av")
        return

    times, rtf, durs = [], [], []
    for c in clips:
        t0 = time.perf_counter()
        segs, info = model.transcribe(c)
        list(segs)
        el = (time.perf_counter() - t0) * 1000
        dur = float(getattr(info, "duration", 0) or 0)
        times.append(el); durs.append(dur)
        rtf.append(el / 1000.0 / dur if dur else np.nan)
    record("Whisper base (STT)", "steady state", len(times), times,
           extra=dict(mean_realtime_factor=float(np.nanmean(rtf)),
                      mean_clip_seconds=float(np.mean(durs)) if durs else None))


# ---------------------------------------------------------------- 2. TTS
def bench_tts(n=10):
    try:
        from TTS.api import TTS
    except Exception:
        print("  Coqui TTS not installed - SKIPPED (report as unmeasured)"); return
    qs = ["Tell me about a time you handled a difficult stakeholder.",
          "Explain the difference between supervised and unsupervised learning.",
          "What are the trade-offs between SQL and NoSQL databases?",
          "Describe a project where you improved system performance.",
          "How would you design a scalable REST API?"]
    t0 = time.perf_counter()
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
    record("Tacotron2-DDC (TTS)", "model load", 1, [(time.perf_counter() - t0) * 1000])

    tmp = tempfile.mkdtemp()
    t0 = time.perf_counter()
    tts.tts_to_file(text=qs[0], file_path=os.path.join(tmp, "w.wav"))
    record("Tacotron2-DDC (TTS)", "cold call", 1, [(time.perf_counter() - t0) * 1000])

    times, chars = [], []
    for i in range(n):
        q = qs[i % len(qs)]
        t0 = time.perf_counter()
        tts.tts_to_file(text=q, file_path=os.path.join(tmp, f"{i}.wav"))
        times.append((time.perf_counter() - t0) * 1000); chars.append(len(q))
    record("Tacotron2-DDC (TTS)", "steady state", len(times), times,
           extra=dict(mean_chars=float(np.mean(chars))))


# ---------------------------------------------------------------- 3. encoder
def bench_encoder():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("  sentence-transformers not installed - SKIPPED"); return
    t0 = time.perf_counter()
    m = SentenceTransformer('all-MiniLM-L6-v2')
    record("MiniLM-L6-v2 (encode)", "model load", 1, [(time.perf_counter() - t0) * 1000])

    it = pd.read_csv(paths.IT_CSV)
    texts = [(str(r['Projects']) + ' ' + str(r['Skills']) + ' ' + str(r['Keywords']))
             for _, r in it.head(600).iterrows()]
    m.encode(texts[:16], show_progress_bar=False)          # warm-up

    # single-document latency: the per-request cost in an interactive path
    t = []
    for s in texts[:50]:
        t0 = time.perf_counter()
        m.encode([s], show_progress_bar=False)
        t.append((time.perf_counter() - t0) * 1000)
    record("MiniLM-L6-v2 (encode)", "1 document", len(t), t)

    # batched throughput: the cost when scoring a candidate pool
    for bs in (50, 200, 600):
        t0 = time.perf_counter()
        m.encode(texts[:bs], batch_size=32, show_progress_bar=False)
        el = (time.perf_counter() - t0) * 1000
        record("MiniLM-L6-v2 (encode)", f"batch of {bs}", 1, [el],
               extra=dict(per_doc_ms=el / bs))


if __name__ == '__main__':
    print("=" * 78)
    print("INFERENCE BENCHMARK: STT, TTS, SENTENCE-TRANSFORMER")
    print("=" * 78)
    print(f"{'component':<24}{'phase':<13}{'':6}{'mean':>12}{'p50':>12}{'p95':>12}")
    clips = prepare_audio()
    print(f"\n[1/3] speech-to-text   ({len(clips)} real answer recordings)")
    bench_stt(clips)
    print("\n[2/3] text-to-speech")
    bench_tts()
    print("\n[3/3] sentence-transformer encoder")
    bench_encoder()

    if OUT:
        df = pd.DataFrame(OUT)
        df.to_csv(paths.out('speech_bench.csv'), index=False)
        print("\nsaved speech_bench.csv")
        print("\nPaste the whole output above back into the chat.")
    else:
        print("\nNothing measured - check the SKIPPED messages above.")
