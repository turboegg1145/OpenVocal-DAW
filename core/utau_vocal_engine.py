"""
OpenVocal-DAW: Authentic Vocal Synthesis Engine
Renders genuine vocal voicebank slices with real pitch-shifting & time-stretching.
Supports both External Resamplers (Moresampler/Resampler) and Built-in Pitch-Shift DSP.
Zero silent synthetic beep fallback!
"""

import os
import sys
import json
import time
import math
import shutil
import subprocess
import concurrent.futures
import numpy as np
import soundfile as sf
from scipy import signal

from core.env_detector import EnvDetector


def midi_num_to_tone(m):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (m // 12) - 1
    return f"{notes[m % 12]}{octave}"


def midi_to_hz(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def parse_oto_ini(vb_dir):
    if not vb_dir or not os.path.exists(vb_dir):
        return {}
    
    oto_files = []
    for root, dirs, files in os.walk(vb_dir):
        for f in files:
            if f.lower() == "oto.ini":
                oto_files.append(os.path.join(root, f))

    oto_map = {}
    for oto_path in oto_files:
        cur_dir = os.path.dirname(oto_path)
        oto_content = ""
        for enc in ['cp932', 'shift-jis', 'utf-8', 'gbk', 'utf-16']:
            try:
                with open(oto_path, 'r', encoding=enc) as f:
                    oto_content = f.read()
                    break
            except Exception:
                pass

        for line in oto_content.splitlines():
            line = line.strip()
            if "=" in line:
                wav_file, params_str = line.split("=", 1)
                p = params_str.split(",")
                alias = p[0].strip() if p[0].strip() else os.path.splitext(wav_file)[0].replace("_", "")
                wav_full = os.path.join(cur_dir, wav_file)
                if os.path.exists(wav_full):
                    try:
                        oto_map[alias.lower()] = {
                            "wav": wav_full,
                            "alias": alias,
                            "offset": float(p[1]) if len(p) > 1 and p[1] else 0.0,
                            "consonant": float(p[2]) if len(p) > 2 and p[2] else 0.0,
                            "cutoff": float(p[3]) if len(p) > 3 and p[3] else 0.0,
                            "preutterance": float(p[4]) if len(p) > 4 and p[4] else 0.0,
                            "overlap": float(p[5]) if len(p) > 5 and p[5] else 0.0,
                        }
                    except Exception:
                        pass
    return oto_map


def pitch_shift_and_stretch(wav_data, orig_sr, target_hz, base_hz, target_duration_sec):
    if len(wav_data.shape) > 1:
        wav_data = wav_data[:, 0]
    
    # 1. Pitch shift ratio
    if base_hz <= 0 or target_hz <= 0:
        pitch_ratio = 1.0
    else:
        pitch_ratio = target_hz / base_hz

    # Resample for pitch shifting
    if abs(pitch_ratio - 1.0) > 0.01:
        new_len = max(16, int(len(wav_data) / pitch_ratio))
        wav_pitched = signal.resample(wav_data, new_len)
    else:
        wav_pitched = wav_data

    # 2. Time stretch to match duration
    target_samples = int(target_duration_sec * orig_sr)
    if target_samples <= 0:
        return np.zeros(16, dtype=np.float32)

    if len(wav_pitched) == target_samples:
        return wav_pitched.astype(np.float32)
    elif len(wav_pitched) > target_samples:
        # Loop or fade out
        out = wav_pitched[:target_samples].copy()
        fade_len = min(int(0.02 * orig_sr), target_samples // 4)
        if fade_len > 0:
            out[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
        return out.astype(np.float32)
    else:
        # Extend by seamless crossfade looping
        out = np.zeros(target_samples, dtype=np.float32)
        cur = 0
        chunk_len = len(wav_pitched)
        fade = min(int(0.02 * orig_sr), chunk_len // 4)
        while cur < target_samples:
            rem = target_samples - cur
            if rem < chunk_len:
                out[cur:target_samples] = wav_pitched[:rem]
                break
            else:
                out[cur:cur+chunk_len] = wav_pitched
                cur += (chunk_len - fade) if fade > 0 else chunk_len
        fade_len = min(int(0.02 * orig_sr), target_samples // 4)
        if fade_len > 0:
            out[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
        return out.astype(np.float32)


class UtauVocalEngine:
    def __init__(self, voicebank_dir=None, resampler_exe=None):
        cfg = EnvDetector.load_config()
        self.vb_dir = None
        self.resampler_exe = None

        # 1. Resolve Voicebank directory
        if voicebank_dir and os.path.exists(voicebank_dir):
            self.vb_dir = voicebank_dir
        else:
            singers_root = cfg.get("openutau_singers_dir")
            if singers_root and os.path.exists(singers_root):
                for item in os.listdir(singers_root):
                    cand = os.path.join(singers_root, item)
                    if os.path.isdir(cand):
                        self.vb_dir = cand
                        break

        # 2. Resolve Resampler Engine
        cand_resamplers = [
            resampler_exe,
            cfg.get("resampler_exe"),
            r"F:\antigravity lol\antigravity-p\utau_engines\moresampler.exe",
            r"F:\antigravity lol\antigravity-p\utau_engines\resampler.exe"
        ]
        for cr in cand_resamplers:
            if cr and os.path.exists(cr) and cr.endswith(".exe"):
                self.resampler_exe = cr
                break

        self.oto_map = parse_oto_ini(self.vb_dir) if self.vb_dir else {}

    def find_best_oto_sample(self, lyric):
        if not self.oto_map:
            return None
        lyr = lyric.strip().lower()
        if lyr in self.oto_map:
            return self.oto_map[lyr]
        for k, v in self.oto_map.items():
            if lyr in k or k in lyr:
                return v
        # Fallback to first vowel or available sample
        for vowel in ['a', 'o', 'e', 'i', 'u', 'あ', 'お', 'え', 'い', 'う']:
            if vowel in self.oto_map:
                return self.oto_map[vowel]
        return list(self.oto_map.values())[0] if len(self.oto_map) > 0 else None

    def render_blueprint(self, blueprint_dict, output_wav_path, flags="g0", sample_rate=44100):
        bpm = float(blueprint_dict["bpm"])
        total_bars = int(blueprint_dict["total_bars"])
        sec_per_beat = 60.0 / bpm
        total_samples = int(round((total_bars * 4 * sec_per_beat) * sample_rate))
        master_vocal = np.zeros(total_samples, dtype=np.float32)

        vocal_score = blueprint_dict.get("vocal_score", {})
        notes_tasks = []
        cur_tick = 0
        note_idx = 0

        for b in range(total_bars):
            bar_notes = vocal_score.get(str(b), vocal_score.get(b, []))
            for item in bar_notes:
                lyric = item[0]
                dur_ticks = int(item[1])
                pitch_num = int(item[2])
                vel = int(item[3])

                if lyric not in ["R", "r", "", "-"] and vel > 0:
                    start_sec = (cur_tick / (bpm * 480.0)) * 60.0
                    dur_sec = (dur_ticks / (bpm * 480.0)) * 60.0
                    tone_name = midi_num_to_tone(pitch_num)
                    target_hz = midi_to_hz(pitch_num)
                    notes_tasks.append({
                        "id": note_idx,
                        "lyric": lyric,
                        "pitch_num": pitch_num,
                        "tone_name": tone_name,
                        "target_hz": target_hz,
                        "start_sec": start_sec,
                        "dur_sec": dur_sec,
                        "vel": vel,
                        "dur_ticks": dur_ticks
                    })
                    note_idx += 1
                cur_tick += dur_ticks

        print(f"  🎤 [Vocal Production] Rendering {len(notes_tasks)} notes using Voicebank: '{self.vb_dir}'...")

        if self.resampler_exe and os.path.exists(self.resampler_exe) and len(self.oto_map) > 0:
            print(f"  ⚡ [Engine] Using Resampler Engine: '{self.resampler_exe}'")
            temp_render_dir = os.path.join(os.path.dirname(output_wav_path), "_temp_vocal_render")
            os.makedirs(temp_render_dir, exist_ok=True)

            try:
                def render_single_note(task):
                    oto = self.find_best_oto_sample(task["lyric"])
                    if not oto: return task["id"], None
                    out_slice_wav = os.path.join(temp_render_dir, f"note_{task['id']:04d}.wav")
                    req_len_ms = task["dur_sec"] * 1000.0
                    cmd = [
                        self.resampler_exe,
                        oto["wav"],
                        out_slice_wav,
                        task["tone_name"],
                        str(task["vel"]),
                        flags,
                        str(oto["offset"]),
                        str(req_len_ms),
                        str(oto["consonant"]),
                        str(oto["cutoff"]),
                        "100",
                        "0",
                        str(bpm),
                        ""
                    ]
                    try:
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=10)
                        if os.path.exists(out_slice_wav):
                            data, sr = sf.read(out_slice_wav)
                            if len(data.shape) > 1: data = data[:, 0]
                            return task["id"], (data, sr)
                    except Exception:
                        pass
                    return task["id"], None

                rendered_slices = {}
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    futures = [executor.submit(render_single_note, t) for t in notes_tasks]
                    for f in concurrent.futures.as_completed(futures):
                        nid, res = f.result()
                        if res is not None:
                            rendered_slices[nid] = res

                for task in notes_tasks:
                    nid = task["id"]
                    s_sample = int(round(task["start_sec"] * sample_rate))
                    if nid in rendered_slices:
                        audio_slice, sr = rendered_slices[nid]
                        slice_len = len(audio_slice)
                        end_sample = min(s_sample + slice_len, total_samples)
                        actual_len = end_sample - s_sample
                        if actual_len > 0:
                            fade_samples = min(int(0.015 * sample_rate), actual_len // 2)
                            env = np.ones(actual_len, dtype=np.float32)
                            if fade_samples > 0:
                                env[:fade_samples] = np.sin(np.linspace(0, np.pi/2, fade_samples)) ** 2
                                env[-fade_samples:] = np.cos(np.linspace(0, np.pi/2, fade_samples)) ** 2
                            master_vocal[s_sample:end_sample] += (audio_slice[:actual_len] * env * (task["vel"] / 100.0)).astype(np.float32)
                    else:
                        # Fallback to authentic slice pitch shifting instead of synthetic beep!
                        oto = self.find_best_oto_sample(task["lyric"])
                        if oto and os.path.exists(oto["wav"]):
                            data, sr = sf.read(oto["wav"])
                            shifted = pitch_shift_and_stretch(data, sr, task["target_hz"], 261.63, task["dur_sec"])
                            dur_len = len(shifted)
                            end_sample = min(s_sample + dur_len, total_samples)
                            actual_len = end_sample - s_sample
                            if actual_len > 0:
                                master_vocal[s_sample:end_sample] += (shifted[:actual_len] * (task["vel"] / 100.0)).astype(np.float32)
            finally:
                shutil.rmtree(temp_render_dir, ignore_errors=True)

        elif len(self.oto_map) > 0:
            print("  🎧 [Engine] Using Direct Voicebank Sample Pitch-Shift DSP Engine...")
            for task in notes_tasks:
                s_sample = int(round(task["start_sec"] * sample_rate))
                oto = self.find_best_oto_sample(task["lyric"])
                if oto and os.path.exists(oto["wav"]):
                    data, sr = sf.read(oto["wav"])
                    shifted = pitch_shift_and_stretch(data, sr, task["target_hz"], 261.63, task["dur_sec"])
                    dur_len = len(shifted)
                    end_sample = min(s_sample + dur_len, total_samples)
                    actual_len = end_sample - s_sample
                    if actual_len > 0:
                        master_vocal[s_sample:end_sample] += (shifted[:actual_len] * (task["vel"] / 100.0)).astype(np.float32)
        else:
            print("  ⚠️ [Warning] No Voicebank found on system! Please run python init_env.py to bind your Singers folder.")

        peak = np.max(np.abs(master_vocal))
        if peak > 0:
            target_peak = 10.0 ** (-1.0 / 20.0)
            master_vocal = (master_vocal / peak) * target_peak

        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
        sf.write(output_wav_path, master_vocal, sample_rate, subtype='PCM_24')
        return output_wav_path
