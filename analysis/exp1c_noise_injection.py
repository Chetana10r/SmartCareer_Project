"""
Experiment 1c - Controlled noise-injection robustness test.
Each of the 37 real clips is degraded with additive noise at known SNRs.
A noise-robust feature should drift little from its clean-condition value.
Reports mean absolute drift (on the feature's own 0-10 scale) and the
rank-stability (Spearman) of the feature across clips at each SNR.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import glob, os
import numpy as np, pandas as pd
import librosa
from scipy.stats import spearmanr

rng = np.random.default_rng(42)
CLIPS = sorted(glob.glob(paths.AUDIO_WAV))
SNRS = [20, 15, 10, 5, 0]

def add_noise(y, snr_db, kind='pink'):
    if kind == 'white':
        n = rng.standard_normal(len(y))
    else:  # pink (1/f) - closer to real room/fan noise
        w = rng.standard_normal(len(y))
        S = np.fft.rfft(w)
        f = np.fft.rfftfreq(len(w)); f[0] = f[1]
        S = S / np.sqrt(f)
        n = np.fft.irfft(S, n=len(w))
    n = n / (np.sqrt(np.mean(n**2)) + 1e-12)
    sp = np.sqrt(np.mean(y**2))
    npow = sp / (10 ** (snr_db / 20.0))
    return y + n * npow

# --- features ---
def f_zcr(y, sr):
    return float(min(10.0, 3.0 + np.mean(librosa.feature.zero_crossing_rate(y)[0]) * 100))

def f_mfcc_naive(y, sr):
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return float(np.clip(np.mean(np.var(m[5:], axis=1)) / 8.0, 0, 10))

def spectral_subtraction(y, sr, n_fft=1024, hop=256, alpha=2.0, floor=0.05):
    S = librosa.stft(y, n_fft=n_fft, hop_length=hop)
    mag, ph = np.abs(S), np.angle(S)
    e = mag.sum(axis=0); k = max(1, int(0.10 * len(e)))
    noise = np.mean(mag[:, np.argsort(e)[:k]], axis=1, keepdims=True)
    clean = np.maximum(mag - alpha * noise, floor * mag)
    return librosa.istft(clean * np.exp(1j * ph), hop_length=hop, length=len(y))

def f_upgraded(y, sr):
    yd = spectral_subtraction(y, sr)
    segs = librosa.effects.split(yd, top_db=25)
    yv = np.concatenate([yd[s:e] for s, e in segs]) if len(segs) else yd
    if len(yv) < 2048: yv = yd
    yv = yv / (np.max(np.abs(yv)) + 1e-9)
    hop = 256
    M = librosa.feature.melspectrogram(y=yv, sr=sr, n_mels=40, n_fft=1024,
                                       hop_length=hop, fmin=80, fmax=8000)
    env = librosa.power_to_db(M)
    env = env - env.mean(axis=1, keepdims=True)
    if env.shape[1] < 8: return 5.0
    spec = np.abs(np.fft.rfft(env, axis=1))
    fr = np.fft.rfftfreq(env.shape[1], d=hop / sr)
    band = (fr >= 2) & (fr <= 8); tot = (fr > 0.5) & (fr <= 20)
    if band.sum() == 0 or tot.sum() == 0: return 5.0
    return float(np.clip(spec[:, band].sum() / (spec[:, tot].sum() + 1e-9) * 20.0, 0, 10))

FEATS = [('ZCR clarity (current)', f_zcr),
         ('MFCC variance (no denoising)', f_mfcc_naive),
         ('Upgraded denoise+VAD+CMVN Mel', f_upgraded)]

clean, sigs = {}, []
for p in CLIPS:
    y, sr = librosa.load(p, sr=None)
    if len(y) < 2048: continue
    sigs.append((os.path.basename(p), y, sr))
print(f"clips: {len(sigs)}")

for name, fn in FEATS:
    clean[name] = np.array([fn(y, sr) for _, y, sr in sigs])

recs = []
for snr in SNRS:
    deg = [(nm, add_noise(y, snr), sr) for nm, y, sr in sigs]
    for name, fn in FEATS:
        v = np.array([fn(y, sr) for _, y, sr in deg])
        drift = np.mean(np.abs(v - clean[name]))
        rho = spearmanr(v, clean[name])[0]
        recs.append(dict(snr=snr, feature=name, mean_abs_drift=drift, rank_stability=rho))

df = pd.DataFrame(recs)
print("\n=== Mean absolute drift from clean value (feature units, 0-10 scale) ===")
piv = df.pivot(index='feature', columns='snr', values='mean_abs_drift')
print(piv.round(3).to_string())
print("\n=== Rank stability vs clean condition (Spearman across the 37 clips) ===")
piv2 = df.pivot(index='feature', columns='snr', values='rank_stability')
print(piv2.round(3).to_string())
df.to_csv(paths.out('noise_injection.csv'), index=False)
