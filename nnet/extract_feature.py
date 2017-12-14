# -*- coding: utf-8 -*-
import librosa
import numpy as np
from scipy import signal

# parameters
sample_rate = 16000
n_fft = int(25 * sample_rate / 1000)
hop_length = int(10 * sample_rate / 1000)

n_imfcc = 40
n_mfcc = 13
n_cqt = 20
f_max = sample_rate / 2
f_min = f_max / 2**9


def extract(wav_path, feature_type):
    if feature_type == "imfcc":
        return extract_imfcc(wav_path)
    if feature_type == "mfcc":
        return extract_mfcc(wav_path)
    if feature_type == "cqt":
        return extract_cqt(wav_path)
    if feature_type == "fft":
        return extract_fft(wav_path)


def extract_imfcc(wav_path):
    y, sr = librosa.load(wav_path, sr=16000)
    S = np.abs(librosa.core.stft(y, n_fft=n_fft, hop_length=hop_length)) ** 2.0
    mel_basis = librosa.filters.mel(sr, n_fft)
    mel_basis = np.linalg.pinv(mel_basis).T
    mel = np.dot(mel_basis, S)
    S = librosa.power_to_db(mel)
    return np.dot(librosa.filters.dct(n_imfcc, S.shape[0]), S)


def extract_mfcc(wav_path):
    y, sr = librosa.load(wav_path, sr=16000)
    mfcc = librosa.feature.mfcc(y, sr, n_mfcc=n_mfcc, n_fft=n_fft, hop_length=hop_length)
    return mfcc


def extract_cqt(wav_path):
    y, sr = librosa.load(wav_path, sr=16000)
    cqt = librosa.feature.chroma_cqt(y, sr, hop_length=hop_length, fmin=f_min, n_chroma=n_cqt, n_octaves=5)
    return cqt


def extract_fft(wav_path):
    p_preemphasis = 0.97
    min_level_db = -100
    num_freq = 1025
    ref_level_db = 20
    frame_length_ms = 50
    frame_shift_ms = 12.5

    def _normalize(S):
        return np.clip((S - min_level_db) / -min_level_db, 0, 1)

    def preemphasis(x):
        return signal.lfilter([1, -p_preemphasis], [1], x)

    def _stft(y):
        n_fft, hop_length, win_length = _stft_parameters()
        return librosa.stft(y=y, n_fft=n_fft, hop_length=hop_length, win_length=win_length)

    def _stft_parameters():
        n_fft = (num_freq - 1) * 2
        hop_length = int(frame_shift_ms / 1000 * sample_rate)
        win_length = int(frame_length_ms / 1000 * sample_rate)
        return n_fft, hop_length, win_length

    def _amp_to_db(x):
        return 20 * np.log10(np.maximum(1e-5, x))
    y = librosa.core.load(wav_path, sr=sample_rate)[0]
    D = _stft(preemphasis(y))
    S = _amp_to_db(np.abs(D)) - ref_level_db
    return _normalize(S)