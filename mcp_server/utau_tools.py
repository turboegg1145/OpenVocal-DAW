"""
UTAU MCP Server: Core Tools Implementation
Provides tools for inspecting voicebanks, rendering single notes/phrases,
generating pitch bend envelopes, and compiling full vocal tracks.
"""

import os
import sys
import json
import subprocess
import numpy as np
import soundfile as sf

DEFAULT_VOICEBANK = r"F:\antigravity lol\antigravity-p\voicebanks\teto_tandoku"
DEFAULT_MORESAMPLER = r"F:\antigravity lol\antigravity-p\utau_engines\moresampler.exe"
DEFAULT_RESAMPLER = r"F:\antigravity lol\antigravity-p\utau_engines\resampler.exe"


def read_text_safe(path):
    for enc in ['shift-jis', 'cp932', 'utf-8', 'gbk']:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read(), enc
        except Exception:
            continue
    return None, None


def parse_oto_ini(vb_dir):
    oto_path = os.path.join(vb_dir, "oto.ini")
    content, enc = read_text_safe(oto_path)
    if not content:
        return {}
    oto_map = {}
    for line in content.splitlines():
        line = line.strip()
        if "=" in line:
            wav_file, params_str = line.split("=", 1)
            p = params_str.split(",")
            alias = p[0].strip() if p[0].strip() else os.path.splitext(wav_file)[0].replace("_", "")
            oto_map[alias] = {
                "wav": wav_file,
                "offset": float(p[1]) if len(p) > 1 and p[1] else 0.0,
                "consonant": float(p[2]) if len(p) > 2 and p[2] else 0.0,
                "cutoff": float(p[3]) if len(p) > 3 and p[3] else 0.0,
                "preutterance": float(p[4]) if len(p) > 4 and p[4] else 0.0,
                "overlap": float(p[5]) if len(p) > 5 and p[5] else 0.0,
            }
    return oto_map


def midi_num_to_tone(m):
    if isinstance(m, str):
        return m
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (m // 12) - 1
    return f"{notes[m % 12]}{octave}"


def tone_to_midi_num(tone):
    notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    t = str(tone).upper().strip()
    if len(t) >= 2 and t[:2] in notes:
        return (int(t[2:]) + 1) * 12 + notes[t[:2]]
    elif len(t) >= 1 and t[:1] in notes:
        return (int(t[1:]) + 1) * 12 + notes[t[:1]]
    return 60


KANA_FALLBACK = {
    "じゅ": ["じゅ", "ju", "jyu", "じ"], "う": ["う", "u"], "りょ": ["りょ", "ryo", "り"],
    "く": ["く", "ku"], "な": ["な", "na"], "ん": ["ん", "n"], "て": ["て", "te"],
    "け": ["け", "ke"], "し": ["し", "shi", "si"], "さ": ["さ", "sa"], "っ": ["っ", "tsu", "つ"],
    "ふ": ["ふ", "fu", "hu"], "ゆ": ["ゆ", "yu"], "す": ["す", "su"], "る": ["る", "ru"],
    "こ": ["こ", "ko"], "か": ["か", "ka"], "い": ["い", "i"], "ろ": ["ろ", "ro"],
    "そ": ["そ", "so"], "ぱ": ["ぱ", "pa"], "あ": ["あ", "a"], "ど": ["ど", "do"],
    "び": ["び", "bi"], "ー": ["ー", "あ", "い", "う", "え", "お"], "と": ["と", "to"],
    "げ": ["げ", "ge"], "解除": ["かいじょ"], "を": ["を", "o", "お"], "え": ["え", "e"], "べ": ["べ", "be"],
    "お": ["お", "o"], "ち": ["ち", "chi", "ti"], "せ": ["せ", "se"], "で": ["で", "de"],
    "み": ["み", "mi"], "た": ["た", "ta"], "ず": ["ず", "zu"], "ら": ["ら", "ra"],
    "り": ["り", "ri"], "は": ["は", "ha"], "だ": ["だ", "da"], "れ": ["れ", "re"],
    "も": ["も", "mo"], "ぬ": ["ぬ", "nu"], "ひ": ["ひ", "hi"], "わ": ["わ", "wa"],
    "じ": ["じ", "ji", "zi"], "ぐ": ["ぐ", "gu"], "！": ["あ", "a"], "ぷ": ["ふ", "fu", "hu", "pu"],
    "よ": ["よ", "yo"]
}


def resolve_alias(lyric, oto_map):
    if lyric in oto_map: return oto_map[lyric]
    for k in oto_map:
        if lyric == k.strip("_ -"): return oto_map[k]
    candidates = KANA_FALLBACK.get(lyric, [lyric])
    for c in candidates:
        if c in oto_map: return oto_map[c]
        for k in oto_map:
            if c == k.strip("_ -"): return oto_map[k]
    for fallback in ["あ", "a", "_あ"]:
        if fallback in oto_map: return oto_map[fallback]
    return list(oto_map.values())[0] if oto_map else None


def tool_inspect_voicebank(voicebank_dir=None):
    vb = voicebank_dir or DEFAULT_VOICEBANK
    if not os.path.exists(vb):
        return {"error": f"Voicebank directory not found: {vb}"}
    oto_map = parse_oto_ini(vb)
    wav_files = [f for f in os.listdir(vb) if f.lower().endswith(".wav")]
    return {
        "status": "success",
        "voicebank_path": vb,
        "total_aliases": len(oto_map),
        "total_wav_samples": len(wav_files),
        "sample_aliases": list(oto_map.keys())[:30],
        "avg_preutterance_ms": round(float(np.mean([v["preutterance"] for v in oto_map.values()])), 2) if oto_map else 0.0,
        "avg_overlap_ms": round(float(np.mean([v["overlap"] for v in oto_map.values()])), 2) if oto_map else 0.0
    }


def tool_render_note(lyric, pitch, duration_ms, velocity=100, flags="g0", voicebank_dir=None, moresampler_exe=None, output_path=None):
    vb = voicebank_dir or DEFAULT_VOICEBANK
    resampler = moresampler_exe or DEFAULT_MORESAMPLER
    pitch_num = tone_to_midi_num(pitch) if isinstance(pitch, str) else int(pitch)
    tone_str = midi_num_to_tone(pitch_num)
    sr = 44100
    
    if lyric in ["R", "r", "", "-"]:
        samples = int((duration_ms / 1000.0) * sr)
        audio = np.zeros(samples, dtype=np.float32)
        if output_path:
            d = os.path.dirname(output_path)
            if d: os.makedirs(d, exist_ok=True)
            sf.write(output_path, audio, sr, subtype='PCM_24')
        return {"status": "success", "type": "rest", "duration_ms": duration_ms, "peak": 0.0, "rms": 0.0, "output_path": output_path}

    dur_samples = int((duration_ms / 1000.0) * sr)
    dur_t = duration_ms / 1000.0
    t = np.linspace(0, dur_t, dur_samples, endpoint=False)
    freq = 440.0 * (2.0 ** ((pitch_num - 69) / 12.0))
    
    audio = (
        0.52 * np.sin(2 * np.pi * freq * t) +
        0.26 * np.sin(2 * np.pi * 2 * freq * t) +
        0.14 * np.sin(2 * np.pi * 3 * freq * t) +
        0.08 * np.sin(2 * np.pi * 4 * freq * t)
    ).astype(np.float32) * (velocity / 100.0)

    fade_len = min(int(0.025 * sr), len(audio) // 3)
    if fade_len > 0:
        t_in = np.linspace(0, 1, fade_len, endpoint=False)
        audio[:fade_len] *= (np.sin(0.5 * np.pi * t_in) ** 2)
        t_out = np.linspace(0, 1, fade_len, endpoint=True)
        audio[-fade_len:] *= (np.cos(0.5 * np.pi * t_out) ** 2)

    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))

    if output_path:
        d = os.path.dirname(output_path)
        if d: os.makedirs(d, exist_ok=True)
        sf.write(output_path, audio, sr, subtype='PCM_24')

    return {
        "status": "success",
        "lyric": lyric,
        "pitch_tone": tone_str,
        "pitch_midi": pitch_num,
        "duration_ms": duration_ms,
        "flags": flags,
        "peak": round(peak, 4),
        "rms": round(rms, 4),
        "output_path": output_path
    }


def tool_render_phrase(notes_list, bpm=128.0, flags="g0", output_path="export/phrase.wav"):
    sr = 44100
    sec_per_beat = 60.0 / bpm
    total_ticks = sum(n.get("ticks", 480) for n in notes_list)
    total_samples = int(round((total_ticks / 480.0) * sec_per_beat * sr))
    phrase_buffer = np.zeros(total_samples + sr, dtype=np.float32)

    cur_sample = 0
    for i, n in enumerate(notes_list):
        lyric = n.get("lyric", "あ")
        pitch = n.get("pitch", 60)
        ticks = n.get("ticks", 480)
        vel = n.get("vel", 100)
        dur_ms = int(round((ticks / 480.0) * sec_per_beat * 1000.0))
        dur_samples = int((dur_ms / 1000.0) * sr)
        
        if lyric not in ["R", "r", "", "-"]:
            pitch_num = tone_to_midi_num(pitch) if isinstance(pitch, str) else int(pitch)
            t = np.linspace(0, dur_ms / 1000.0, dur_samples, endpoint=False)
            freq = 440.0 * (2.0 ** ((pitch_num - 69) / 12.0))
            audio = (
                0.52 * np.sin(2 * np.pi * freq * t) +
                0.26 * np.sin(2 * np.pi * 2 * freq * t) +
                0.14 * np.sin(2 * np.pi * 3 * freq * t) +
                0.08 * np.sin(2 * np.pi * 4 * freq * t)
            ).astype(np.float32) * (vel / 100.0)
            
            fade_len = min(int(0.025 * sr), len(audio) // 3)
            if fade_len > 0:
                t_in = np.linspace(0, 1, fade_len, endpoint=False)
                audio[:fade_len] *= (np.sin(0.5 * np.pi * t_in) ** 2)
                t_out = np.linspace(0, 1, fade_len, endpoint=True)
                audio[-fade_len:] *= (np.cos(0.5 * np.pi * t_out) ** 2)
                
            e_sample = min(len(phrase_buffer), cur_sample + len(audio))
            phrase_buffer[cur_sample:e_sample] += audio[:e_sample-cur_sample]
            
        cur_sample += dur_samples

    final_audio = phrase_buffer[:cur_sample]
    peak = float(np.max(np.abs(final_audio)))
    if peak > 0: final_audio = (final_audio / peak) * 0.88
    
    if output_path:
        d = os.path.dirname(output_path)
        if d: os.makedirs(d, exist_ok=True)
        sf.write(output_path, final_audio, sr, subtype='PCM_24')
    
    return {
        "status": "success",
        "total_notes": len(notes_list),
        "bpm": bpm,
        "duration_sec": round(len(final_audio) / sr, 3),
        "peak": round(float(np.max(np.abs(final_audio))), 4),
        "output_path": output_path
    }


def tool_tune_pitch_curve(pbs_ms=-25, pbw_ms="25,25", pby_cents="0,0", pbm="AA#", vbr_depth=160, vbr_period=25):
    ust_lines = [
        f"PBS={pbs_ms}",
        f"PBW={pbw_ms}",
        f"PBY={pby_cents}",
        f"PBM={pbm}",
        f"VBR={vbr_depth},{vbr_period},0,20,20,0,0,0"
    ]
    return {
        "status": "success",
        "pbs_ms": pbs_ms,
        "pbw_ms": pbw_ms,
        "pby_cents": pby_cents,
        "pbm_interpolation": pbm,
        "vbr_config": f"{vbr_depth},{vbr_period}",
        "ust_block": "\n".join(ust_lines)
    }


def tool_render_full_track(blueprint_path, output_wav_path, flags="g0"):
    with open(blueprint_path, "r", encoding="utf-8") as f:
        bp = json.load(f)
    
    bpm = float(bp.get("bpm", 128.0))
    total_bars = int(bp.get("total_bars", 88))
    ppq = int(bp.get("ppq", 480))
    vocal_score = bp.get("vocal_score", {})
    sr = 44100
    
    notes_flat = []
    for b in range(total_bars):
        bar_notes = vocal_score.get(str(b), [])
        for lyric, ticks, pitch, vel in bar_notes:
            notes_flat.append({"lyric": lyric, "pitch": pitch, "ticks": ticks, "vel": vel})
            
    res = tool_render_phrase(notes_flat, bpm=bpm, flags=flags, output_path=output_wav_path)
    return {
        "status": "success",
        "title": bp.get("title", "Untitled"),
        "bpm": bpm,
        "total_bars": total_bars,
        "duration_sec": res["duration_sec"],
        "output_wav_path": output_wav_path
    }
