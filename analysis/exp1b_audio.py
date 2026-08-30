"""
Experiment 1b - Upgraded noise-robust audio pipeline, native 48 kHz.
Baseline replication + modulation-domain articulation feature.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import glob, os
import numpy as np, pandas as pd
import librosa
from scipy.stats import pearsonr, spearmanr

CLIPS = sorted(glob.glob(paths.AUDIO_WAV))

def noise_floor(y):
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
    k = max(1, int(0.10 * len(rms)))
    return float(np.mean(np.sort(rms)[:k]))

# ---- current implementation, verbatim from audio_analyzer.py ----
def clarity_zcr(y, sr):
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    return float(min(10.0, 3.0 + np.mean(zcr) * 100))

def clarity_zcr_trim(y, sr):
    yt, _ = librosa.effects.trim(y, top_db=20)
    if len(yt) < 512: yt = y
    return float(min(10.0, 3.0 + np.mean(librosa.feature.zero_crossing_rate(yt)[0]) * 100))

def mfcc_var_naive(y, sr):
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return float(np.mean(np.var(m[5:], axis=1)))

# ---- upgraded pipeline ----
def spectral_subtraction(y, sr, n_fft=1024, hop=256, alpha=2.0, floor=0.05):
    S = librosa.stft(y, n_fft=n_fft, hop_length=hop)
    mag, ph = np.abs(S), np.angle(S)
    e = mag.sum(axis=0); k = max(1, int(0.10 * len(e)))
    noise = np.mean(mag[:, np.argsort(e)[:k]], axis=1, keepdims=True)
    clean = np.maximum(mag - alpha * noise, floor * mag)
    return librosa.istft(clean * np.exp(1j * ph), hop_length=hop, length=len(y))

def modulation_articulation(y, sr):
    """
    Noise-robust articulation proxy.
    Speech carries strong 2-8 Hz (syllabic) amplitude modulation; stationary
    background noise does not. Ratio of syllabic-band modulation energy to
    total modulation energy is therefore insensitive to a constant noise floor.
    Computed on denoised, VAD-selected, Mel-band energy envelopes.
    """
    yd = spectral_subtraction(y, sr)
    segs = librosa.effects.split(yd, top_db=25)
    yv = np.concatenate([yd[s:e] for s, e in segs]) if len(segs) else yd
    if len(yv) < 2048: yv = yd
    yv = yv / (np.max(np.abs(yv)) + 1e-9)

    hop = 256
    M = librosa.feature.melspectrogram(y=yv, sr=sr, n_mels=40, n_fft=1024,
                                       hop_length=hop, fmin=80, fmax=8000)
    env = librosa.power_to_db(M)
    env = env - env.mean(axis=1, keepdims=True)          # CMVN (removes static noise offset)
    fps = sr / hop
    if env.shape[1] < 8:
        return 5.0
    spec = np.abs(np.fft.rfft(env, axis=1))
    freqs = np.fft.rfftfreq(env.shape[1], d=1.0 / fps)
    band = (freqs >= 2) & (freqs <= 8)
    tot = (freqs > 0.5) & (freqs <= 20)
    if band.sum() == 0 or tot.sum() == 0:
        return 5.0
    ratio = spec[:, band].sum() / (spec[:, tot].sum() + 1e-9)
    return float(np.clip(ratio * 20.0, 0, 10))

rows = []
for p in CLIPS:
    y, sr = librosa.load(p, sr=None)
    if len(y) < 1024: continue
    rows.append(dict(f=os.path.basename(p), dur=len(y)/sr, sr=sr, noise=noise_floor(y),
                     zcr=clarity_zcr(y, sr), zcr_trim=clarity_zcr_trim(y, sr),
                     mfcc_naive=mfcc_var_naive(y, sr),
                     upgraded=modulation_articulation(y, sr)))

df = pd.DataFrame(rows)
print(f"N = {len(df)} clips, sr = {int(df.sr.iloc[0])} Hz, "
      f"duration {df.dur.min():.1f}-{df.dur.max():.1f}s (mean {df.dur.mean():.1f}s)")
print("\nCorrelation with objective background-noise floor:")
print(f"{'feature':52s} {'pearson r':>10s} {'p':>8s} {'spearman':>10s} {'p':>8s}")
for c, lab in [('zcr','(A) ZCR clarity - CURRENT implementation'),
               ('zcr_trim','(B) ZCR + silence trimming'),
               ('mfcc_naive','(C) MFCC variance, no denoising'),
               ('upgraded','(D) UPGRADED denoise+VAD+CMVN Mel modulation')]:
    r, p1 = pearsonr(df[c], df.noise); rho, p2 = spearmanr(df[c], df.noise)
    print(f"{lab:52s} {r:+10.3f} {p1:8.4f} {rho:+10.3f} {p2:8.4f}")

df.to_csv(paths.out('audio_results_native.csv'), index=False)
print("\nvariance explained by noise:  current ZCR = %.1f%%   upgraded = %.1f%%" %
      (100*pearsonr(df.zcr, df.noise)[0]**2, 100*pearsonr(df.upgraded, df.noise)[0]**2))
