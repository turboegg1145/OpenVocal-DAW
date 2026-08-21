"""
OpenVocal-DAW: UTAU Vocal Synthesis Engine
High-fidelity vocal rendering pipeline supporting:
1. Direct multithreaded concatenative resampling via Moresampler / Resampler + real Voicebanks.
2. Zero-dependency additive physical harmonic acoustic engine fallback.
100% dynamically configured via EnvDetector (Zero hardcoded paths).
"""

import os
import sys
import json
import time
import subprocess
import concurrent.futures
import numpy as np
import soundfile as sf

from core.env_detector import EnvDetector


def midi_num_to_tone(m):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (m // 12) - 1
    return f"{notes[m % 12]}{octave}"


def parse_oto_ini(vb_dir):
    if not vb_dir or not os.path.exists(vb_dir):
        return {}
    oto_path = os.path.join(vb_dir, "oto.ini")
    if not os.path.exists(oto_path):
        return {}
    
    oto_content = ""
    for enc in ['cp932', 'shift-jis', 'utf-8', 'gbk']:
        try:
            with open(oto_path, 'r', encoding=enc) as f:
                oto_content = f.read()
                break
        except Exception:
            pass

    oto_map = {}
    for line in oto_content.splitlines():
        line = line.strip()
        if "=" in line:
            wav_file, params_str = line.split("=", 1)
            p = params_str.split(",")
            alias = p[0].strip() if p[0].strip() else os.path.splitext(wav_file)[0].replace("_", "")
            wav_full = os.path.join(vb_dir, wav_file)
            if os.path.exists(wav_full):
                oto_map[alias] = {
                    "wav": wav_full,
                    "alias": alias,
                    "offset": float(p[1]) if len(p) > 1 and p[1] else 0.0,
                    "consonant": float(p[2]) if len(p) > 2 and p[2] else 0.0,
                    "cutoff": float(p[3]) if len(p) > 3 and p[3] else 0.0,
                    "preutterance": float(p[4]) if len(p) > 4 and p[4] else 0.0,
                    "overlap": float(p[5]) if len(p) > 5 and p[5] else 0.0,
                }
    return oto_map


class UtauVocalEngine:
    def __init__(self, voicebank_dir=None, resampler_exe=None):
        cfg = EnvDetector.load_config()
        
        # 1. Voicebank Path Resolution
        if voicebank_dir and os.path.exists(voicebank_dir):
            self.vb_dir = voicebank_dir
        else:
            self.vb_dir = cfg.get("voicebank_dir")

        # 2. Resampler Path Resolution
        if resampler_exe and os.path.exists(resampler_exe):
            self.resampler_exe = resampler_exe
        else:
            self.resampler_exe = cfg.get("resampler_exe")

        self.oto_map = parse_oto_ini(self.vb_dir) if self.vb_dir else {}

    def render_blueprint(self, blueprint_dict, output_wav_path, flags="g0", sample_rate=44100):
        bpm = float(blueprint_dict["bpm"])
        total_bars = int(blueprint_dict["total_bars"])
        sec_per_beat = 60.0 / bpm
        total_samples = int(round((total_bars * 4 * sec_per_beat) * sample_rate))
        master_vocal = np.zeros(total_samples, dtype=np.float32)

        # Check if real voicebank + resampler can be used
        use_real_voicebank = bool(self.vb_dir and self.resampler_exe and len(self.oto_map) > 0)

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
                    notes_tasks.append({
                        "id": note_idx,
                        "lyric": lyric,
                        "pitch_num": pitch_num,
                        "tone_name": tone_name,
                        "start_sec": start_sec,
                        "dur_sec": dur_sec,
                        "vel": vel,
                        "dur_ticks": dur_ticks
                    })
                    note_idx += 1
                cur_tick += dur_ticks

        if use_real_voicebank:
            print(f"  [Real Voicebank Engine] Detected Voicebank at '{self.vb_dir}'")
            print(f"  [Real Voicebank Engine] Using Resampler '{self.resampler_exe}' with {len(self.oto_map)} aliases.")
            print(f"  [Real Voicebank Engine] Resampling {len(notes_tasks)} real notes concurrently...")
            
            temp_render_dir = os.path.join(os.path.dirname(output_wav_path), "_temp_utau_render")
            os.makedirs(temp_render_dir, exist_ok=True)

            def render_single_note(task):
                lyric = task["lyric"]
                oto = self.oto_map.get(lyric)
                if not oto:
                    return task["id"], None

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
                        # Cosine crossfade
                        fade_samples = min(int(0.015 * sample_rate), actual_len // 2)
                        env = np.ones(actual_len, dtype=np.float32)
                        if fade_samples > 0:
                            env[:fade_samples] = np.sin(np.linspace(0, np.pi/2, fade_samples)) ** 2
                            env[-fade_samples:] = np.cos(np.linspace(0, np.pi/2, fade_samples)) ** 2
                        master_vocal[s_sample:end_sample] += (audio_slice[:actual_len] * env * (task["vel"] / 100.0)).astype(np.float32)
                else:
                    # Single note mathematical harmonic fallback
                    dur_samples = int(round(task["dur_sec"] * sample_rate))
                    end_sample = min(s_sample + dur_samples, total_samples)
                    actual_len = end_sample - s_sample
                    if actual_len > 0:
                        t = np.linspace(0, actual_len / sample_rate, actual_len, endpoint=False)
                        f0 = 440.0 * (2.0 ** ((task["pitch_num"] - 69) / 12.0))
                        sig = (0.6 * np.sin(2 * np.pi * f0 * t) +
                               0.3 * np.sin(2 * np.pi * 2 * f0 * t) +
                               0.15 * np.sin(2 * np.pi * 3 * f0 * t))
                        fade_len = min(int(0.01 * sample_rate), actual_len // 4)
                        env = np.ones(actual_len, dtype=np.float32)
                        if fade_len > 0:
                            env[:fade_len] = np.linspace(0, 1, fade_len)
                            env[-fade_len:] = np.linspace(1, 0, fade_len)
                        master_vocal[s_sample:end_sample] += (sig * env * 0.5 * (task["vel"] / 100.0)).astype(np.float32)

            # Cleanup temp slices
            try:
                shutil.rmtree(temp_render_dir, ignore_errors=True)
            except Exception:
                pass

        else:
            # Full mathematical acoustic harmonic oscillator fallback
            print("  [Vocal Acoustic Engine] Using zero-dependency additive harmonic oscillator fallback...")
            for task in notes_tasks:
                s_sample = int(round(task["start_sec"] * sample_rate))
                dur_samples = int(round(task["dur_sec"] * sample_rate))
                end_sample = min(s_sample + dur_samples, total_samples)
                actual_len = end_sample - s_sample
                if actual_len > 0:
                    t = np.linspace(0, actual_len / sample_rate, actual_len, endpoint=False)
                    f0 = 440.0 * (2.0 ** ((task["pitch_num"] - 69) / 12.0))
                    sig = (0.55 * np.sin(2 * np.pi * f0 * t) +
                           0.30 * np.sin(2 * np.pi * 2 * f0 * t) +
                           0.18 * np.sin(2 * np.pi * 3 * f0 * t) +
                           0.08 * np.sin(2 * np.pi * 4 * f0 * t))
                    fade_len = min(int(0.015 * sample_rate), actual_len // 4)
                    env = np.ones(actual_len, dtype=np.float32)
                    if fade_len > 0:
                        env[:fade_len] = np.linspace(0, 1, fade_len)
                        env[-fade_len:] = np.linspace(1, 0, fade_len)
                    master_vocal[s_sample:end_sample] += (sig * env * 0.65 * (task["vel"] / 100.0)).astype(np.float32)

        # Normalize to -1.0 dBFS
        peak = np.max(np.abs(master_vocal))
        if peak > 0:
            target_peak = 10.0 ** (-1.0 / 20.0)
            master_vocal = (master_vocal / peak) * target_peak

        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
        sf.write(output_wav_path, master_vocal, sample_rate, subtype='PCM_24')
        return output_wav_path
