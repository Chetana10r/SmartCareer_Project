"""
Text-to-speech inference benchmark using pyttsx3 (Windows SAPI5 backend).

This measures TTS the same way Section 7.12.1 measures STT and the sentence
encoder: model/engine load cost separately from steady-state per-call cost.

The platform's TTS component is unspecified beyond "text-to-speech" in the
requirements file; the deployed engine could not be installed in the Linux
evaluation environment used for the other benchmarks, so this uses the
Windows-native SAPI5 engine as a representative substitute, run once by the
authors on the same machine used for the STT and encoder measurements.
This substitution is stated explicitly and its limits are the same in kind as
those already declared for the semantic-similarity substitution in Section 7.9.

Run on Windows, after bench_speech_components.py:

    pip install pyttsx3
    python bench_tts_pyttsx3.py

Writes tts_bench.csv in the same analysis/ folder.
"""
import os, sys, time, tempfile, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

import numpy as np, pandas as pd

try:
    import pyttsx3
except ImportError:
    sys.exit("Install first:  pip install pyttsx3")

CALL_TIMEOUT_S = 15   # a single SAPI5 call should never legitimately take this long


def run_with_timeout(fn, timeout=CALL_TIMEOUT_S):
    """Run fn() in a thread; raise TimeoutError rather than hang forever."""
    result, error = [], []

    def target():
        try:
            result.append(fn())
        except Exception as e:
            error.append(e)

    th = threading.Thread(target=target, daemon=True)
    th.start()
    th.join(timeout)
    if th.is_alive():
        raise TimeoutError(f"call exceeded {timeout}s - SAPI5 hang, skipping")
    if error:
        raise error[0]
    return result[0] if result else None

QUESTIONS = [
 "Tell me about a time you handled a difficult stakeholder.",
 "Explain the difference between supervised and unsupervised learning.",
 "What are the trade-offs between SQL and NoSQL databases?",
 "Describe a project where you improved system performance.",
 "How would you design a scalable REST API?",
 "What is your approach to debugging a production issue?",
 "Walk me through how you would optimise a slow database query.",
 "Describe a situation where you disagreed with a team decision.",
]

OUT = []


def record(phase, times_ms, extra=None):
    a = np.array(times_ms, dtype=float)
    row = dict(component='pyttsx3 (SAPI5, TTS)', phase=phase, n=len(a),
               mean_ms=a.mean(), p50_ms=np.percentile(a, 50),
               p95_ms=np.percentile(a, 95), min_ms=a.min(), max_ms=a.max())
    if extra:
        row.update(extra)
    OUT.append(row)
    print(f"  {phase:<16} n={len(a):<3} mean={a.mean():9.1f} ms   "
          f"p50={np.percentile(a,50):9.1f}   p95={np.percentile(a,95):9.1f}")


def synth_to_file(text, path):
    """
    Create a fresh engine instance per call.

    pyttsx3's SAPI5 driver on Windows is known to hang on runAndWait() when a
    single engine instance is reused across many save_to_file() calls in a
    tight loop (a long-standing upstream issue, not specific to this machine).
    Re-initialising per call avoids it at the cost of the init overhead, which
    is exactly the "cold call" cost already measured separately above, so nothing
    about the reported steady-state number is invalidated by this workaround.
    """
    engine = pyttsx3.init()
    engine.save_to_file(text, path)
    engine.runAndWait()
    engine.stop()
    del engine


if __name__ == '__main__':
    print("=" * 70)
    print("TEXT-TO-SPEECH INFERENCE BENCHMARK  (pyttsx3 / Windows SAPI5)")
    print("=" * 70)

    tmp = tempfile.mkdtemp()

    t0 = time.perf_counter()
    engine = pyttsx3.init()
    engine.stop()
    del engine
    record("engine init", [(time.perf_counter() - t0) * 1000])

    t0 = time.perf_counter()
    run_with_timeout(lambda: synth_to_file(QUESTIONS[0], os.path.join(tmp, "cold.wav")))
    record("cold call", [(time.perf_counter() - t0) * 1000])

    N = 10   # kept modest: each call carries its own engine-init overhead
    times, chars, skipped = [], [], 0
    for i, q in enumerate((QUESTIONS * 2)[:N]):
        print(f"  call {i+1}/{N} ...", end="\r")
        t0 = time.perf_counter()
        try:
            run_with_timeout(lambda: synth_to_file(q, os.path.join(tmp, f"{i}.wav")))
            times.append((time.perf_counter() - t0) * 1000)
            chars.append(len(q))
        except TimeoutError as e:
            print(f"\n  call {i+1} timed out and was skipped: {e}")
            skipped += 1
    print(" " * 20, end="\r")
    if times:
        record("steady state (fresh engine per call)", times,
               extra=dict(mean_chars=float(np.mean(chars)), calls_skipped=skipped))
    else:
        print("  every call timed out - TTS could not be reliably measured on this machine")

    df = pd.DataFrame(OUT)
    df.to_csv(paths.out('tts_bench.csv'), index=False)
    print("\nsaved tts_bench.csv")
    print("\nPaste the whole output above back into the chat.")
