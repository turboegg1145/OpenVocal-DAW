"""
OpenVocal-DAW: UTAU Vocal Synthesis Engine
High-fidelity vocal rendering pipeline supporting:
1. Direct multithreaded acoustic concatenative resampling via Moresampler / Resampler + real Voicebanks (e.g. Kasane Teto)
2. Zero-dependency additive physical harmonic acoustic engine fallback.
"""

import os
import sys
import json
import time
import subprocess
import concurrent.futures
import numpy as np
import soundfile as sf

DEFAULT_VB_CANDIDATES = [
    r"F:\antigravity lol\antigravity-p\voicebanks\teto_tandoku",
    r"voicebanks\teto_tandoku",
    r"..\voicebanks\teto_tandoku",
    r"F:\antigravity lol\voicebanks\teto_tandoku"
]

DEFAULT_RESAMPLER_CANDIDATES = [
    r"F:\antigravity lol\antigravity-p\utau_engines\moresampler.exe",
    r"utau_engines\moresampler.exe",
    r"..\utau_engines\moresampler.exe",
    r"F:\antigravity lol\utau_engines\moresampler.exe",
    r"F:\antigravity lol\antigravity-p\utau_engines\resampler.exe"
]


def midi_num_to_tone(m):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (m // 12) - 1
    return f"{notes[m % 12]}{octave}"


def parse_oto_ini(vb_dir):
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
        self.vb_dir = None
        if voicebank_dir and os.path.exists(voicebank_dir):
            self.vb_dir = voicebank_dir
        else:
            for c in DEFAULT_VB_CANDIDATES:
                if os.path.exists(c):
                    self.vb_dir = c
                    break

        self.resampler_exe = None
        if resampler_exe and os.path.exists(resampler_exe):
            self.resampler_exe = resampler_exe
        else:
            for c in DEFAULT_RESAMPLER_CANDIDATES:
                if os.path.exists(c):
                    self.resampler_exe = c
                    break

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

        temp_cache_dir = os.path.join(os.path.dirname(os.path.abspath(output_wav_path)), ".vocal_cache")
        if use_real_voicebank:
            os.makedirs(temp_cache_dir, exist_ok=True)
            print(f"  [Real Voicebank Engine] Detected Voicebank at '{self.vb_dir}'")
            print(f"  [Real Voicebank Engine] Using Resampler '{self.resampler_exe}' with {len(self.oto_map)} aliases.")

        for b in range(total_bars):
            bar_notes = vocal_score.get(str(b), vocal_score.get(b, []))
            for item in bar_notes:
                lyric, ticks, pitch, vel = item[0], int(item[1]), int(item[2]), int(item[3])
                start_tick = cur_tick
                end_tick = cur_tick + ticks
                dur_ms = int(round((ticks / 480.0) * sec_per_beat * 1000.0))
                s_sample = int(round(start_tick * (sec_per_beat / 480.0) * sample_rate))
                e_sample = int(round(end_tick * (sec_per_beat / 480.0) * sample_rate))

                if lyric not in ["R", "r", "", "-"]:
                    if use_real_voicebank:
                        oto_info = self.oto_map.get(lyric)
                        if not oto_info:
                            for k in self.oto_map:
                                if lyric in k:
                                    oto_info = self.oto_map[k]
                                    break
                        if not oto_info:
                            oto_info = self.oto_map.get("あ", list(self.oto_map.values())[0])

                        out_chunk_path = os.path.join(temp_cache_dir, f"note_{note_idx:04d}.wav")
                        tone_name = midi_num_to_tone(pitch)
                        cmd = [
                            self.resampler_exe,
                            oto_info["wav"],
                            out_chunk_path,
                            tone_name,
                            str(vel),
                            flags,
                            str(int(oto_info["offset"])),
                            str(max(50, dur_ms)),
                            str(int(oto_info["consonant"])),
                            str(int(oto_info["cutoff"])),
                            "100",
                            "0",
                            f"!{bpm:.1f}",
                            "AA"
                        ]
                        notes_tasks.append({
                            "idx": note_idx,
                            "cmd": cmd,
                            "out_wav": out_chunk_path,
                            "s_sample": s_sample,
                            "e_sample": e_sample,
                            "dur_samples": e_sample - s_sample
                        })
                    else:
                        # Fallback math synthesizer
                        notes_tasks.append({
                            "idx": note_idx,
                            "lyric": lyric,
                            "pitch": pitch,
                            "vel": vel,
                            "s_sample": s_sample,
                            "e_sample": e_sample,
                            "dur_samples": e_sample - s_sample
                        })
                cur_tick += ticks
                note_idx += 1

        if use_real_voicebank:
            print(f"  [Real Voicebank Engine] Resampling {len(notes_tasks)} real notes concurrently...")
            def worker(task):
                subprocess.run(task["cmd"], capture_output=True, text=True)
                return task["idx"]

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(worker, notes_tasks))

            # Splice and crossfade real voicebank chunks
            fade_samples = int(0.025 * sample_rate)
            for task in notes_tasks:
                out_wav = task["out_wav"]
                s = task["s_sample"]
                if os.path.exists(out_wav) and os.path.getsize(out_wav) > 100:
                    audio, chunk_sr = sf.read(out_wav)
                    if len(audio.shape) > 1: audio = audio[:, 0]
                    dur = task["dur_samples"]
                    chunk = audio[:dur] if len(audio) >= dur else np.pad(audio, (0, dur - len(audio)))
                    f_len = min(fade_samples, len(chunk) // 4)
                    if f_len > 0:
                        t_in = np.linspace(0, 1, f_len, endpoint=False)
                        chunk[:f_len] *= (np.sin(0.5 * np.pi * t_in) ** 2)
                        t_out = np.linspace(0, 1, f_len, endpoint=True)
                        chunk[-f_len:] *= (np.cos(0.5 * np.pi * t_out) ** 2)

                    actual_e = min(total_samples, s + len(chunk))
                    valid_len = actual_e - s
                    master_vocal[s:actual_e] += chunk[:valid_len]

            # Clean cache
            import shutil
            try: shutil.rmtree(temp_cache_dir, ignore_errors=True)
            except Exception: pass
        else:
            print(f"  [Acoustic Fallback] Synthesizing {len(notes_tasks)} notes via harmonic modeling...")
            fade_samples = int(0.025 * sample_rate)
            for task in notes_tasks:
                s = task["s_sample"]
                dur_samples = task["dur_samples"]
                if dur_samples <= 0 or s >= total_samples: continue
                dur_t = dur_samples / sample_rate
                t = np.linspace(0, dur_t, dur_samples, endpoint=False)
                freq = 440.0 * (2.0 ** ((task["pitch"] - 69) / 12.0))
                harmonics = (
                    0.52 * np.sin(2 * np.pi * freq * t) +
                    0.26 * np.sin(2 * np.pi * 2 * freq * t) +
                    0.14 * np.sin(2 * np.pi * 3 * freq * t) +
                    0.08 * np.sin(2 * np.pi * 4 * freq * t)
                ).astype(np.float32) * (task["vel"] / 100.0)

                f_len = min(fade_samples, dur_samples // 3)
                if f_len > 0:
                    t_in = np.linspace(0, 1, f_len, endpoint=False)
                    harmonics[:f_len] *= (np.sin(0.5 * np.pi * t_in) ** 2)
                    t_out = np.linspace(0, 1, f_len, endpoint=True)
                    harmonics[-f_len:] *= (np.cos(0.5 * np.pi * t_out) ** 2)

                actual_e = min(total_samples, s + dur_samples)
                valid_len = actual_e - s
                master_vocal[s:actual_e] += harmonics[:valid_len]

        pk = np.max(np.abs(master_vocal))
        if pk > 0: master_vocal = (master_vocal / pk) * 0.90

        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
        sf.write(output_wav_path, master_vocal, sample_rate, subtype='PCM_24')
        return output_wav_path
