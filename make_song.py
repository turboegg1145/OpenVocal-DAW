"""
OpenVocal-DAW CLI Entrypoint
Autonomous AI Vocal & Music Production Pipeline.
Creates clean, portable, dedicated song project folders.
"""

import os
import sys
import json
import re
import soundfile as sf
import numpy as np

from core.utau_vocal_engine import UtauVocalEngine
from core.openutau_ustx_builder import OpenUtauUstxBuilder
from core.harmony_matrix import HarmonyMatrix
from core.reaper_project_builder import ReaperProjectBuilder
from core.mastering_dsp import MasteringDSP


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()


def main():
    print("=" * 70)
    print("   OpenVocal-DAW: Autonomous AI Vocal & Music Production Toolkit")
    print("=" * 70)
    if len(sys.argv) < 2:
        print("Usage: python make_song.py <path_to_song_blueprint.json> [export_base_dir]")
        return

    blueprint_path = sys.argv[1]
    export_base_dir = sys.argv[2] if len(sys.argv) > 2 else "export"

    with open(blueprint_path, "r", encoding="utf-8") as f:
        blueprint = json.load(f)

    title = blueprint.get("title", "Untitled_Song")
    safe_title = sanitize_filename(title)
    bpm = float(blueprint.get("bpm", 128.0))
    total_bars = int(blueprint.get("total_bars", 88))
    print(f"Loaded Song: {title} | BPM: {bpm} | Total Bars: {total_bars}")

    # Create dedicated song directory: export/<safe_title>/
    song_dir = os.path.join(export_base_dir, safe_title)
    stems_dir = os.path.join(song_dir, "stems")
    midi_dir = os.path.join(song_dir, "midi")
    os.makedirs(stems_dir, exist_ok=True)
    os.makedirs(midi_dir, exist_ok=True)
    print(f"Target Output Folder: {song_dir}")

    # --- STEP 1: OPENUTAU (.USTX) GENERATION ---
    print("[1/5] Compiling OpenUtau (.ustx) Project...")
    ustx_builder = OpenUtauUstxBuilder(title=title, bpm=bpm)
    t_lead = ustx_builder.add_track("Lead Vocal", singer="Kasane Teto [UTAU]", phoneticizer="OpenUtau.Core.DefaultPhoneticizer")
    
    notes_flat = []
    vocal_score = blueprint.get("vocal_score", {})
    for b in range(total_bars):
        bar_notes = vocal_score.get(str(b), vocal_score.get(b, []))
        for item in bar_notes:
            notes_flat.append({"lyric": item[0], "ticks": int(item[1]), "pitch": int(item[2]), "vel": int(item[3])})
    
    ustx_builder.add_voice_part(t_lead, "Lead Vocal Part", notes_flat)
    ustx_path = os.path.join(song_dir, f"{safe_title}.ustx")
    ustx_builder.export_ustx_yaml(ustx_path)
    print(f"  [OK] Saved OpenUtau Project: {ustx_path}")

    # --- STEP 2: VOCAL AUDIO SYNTHESIS ---
    print("[2/5] Synthesizing 24-bit Lead Vocal Audio...")
    vocal_engine = UtauVocalEngine("", "")
    vocal_wav_path = os.path.join(stems_dir, "01_Lead_Vocal.wav")
    vocal_engine.render_blueprint(blueprint, vocal_wav_path)
    print(f"  [OK] Exported Lead Vocal Stem: {vocal_wav_path}")

    # --- STEP 3: HARMONY MATRIX BACKING TRACKS (MIDI + STEMS) ---
    print("[3/5] Generating SoundQuest Harmonic Matrix (Piano, Bass, Drums, Synth)...")
    harmony = HarmonyMatrix(bpm=bpm)
    tracks_config, backing_audio = harmony.generate_full_arrangement(blueprint, song_dir=song_dir)
    print(f"  [OK] Generated {len(tracks_config)} Multi-Track Stems in {stems_dir}")
    print(f"  [OK] Generated {len(tracks_config)} MIDI Sequences in {midi_dir}")

    # --- STEP 4: MASTERING DSP ---
    print("[4/5] Mastering DSP (Tape Glue Saturation & -0.3 dBFS True-Peak Limiter)...")
    vocal_audio, sr = sf.read(vocal_wav_path)
    if len(vocal_audio.shape) > 1: vocal_audio = vocal_audio[:, 0]
    
    max_len = max(len(vocal_audio), len(backing_audio))
    full_mix = np.zeros(max_len, dtype=np.float32)
    full_mix[:len(backing_audio)] += backing_audio * 0.7
    full_mix[:len(vocal_audio)] += vocal_audio * 0.85
    
    master_wav_path = os.path.join(song_dir, f"{safe_title}_Master.wav")
    MasteringDSP.export_master(full_mix, master_wav_path, sample_rate=sr)
    print(f"  [OK] Exported 24-bit Master Audio: {master_wav_path}")

    # --- STEP 5: REAPER DUAL-LAYER SESSION ---
    print("[5/5] Building Dual-Layer REAPER DAW Session (.rpp)...")
    rpp_builder = ReaperProjectBuilder(bpm=bpm, total_bars=total_bars)
    rpp_path = os.path.join(song_dir, f"{safe_title}.rpp")
    rpp_builder.build_session(tracks_config, rpp_path, f"{safe_title}_Master.wav")
    print(f"  [OK] Saved REAPER Project: {rpp_path}")

    print("=" * 70)
    print("SUCCESS: PROJECT SUCCESSFULLY EXPORTED TO STRUCTURED DIRECTORY!")
    print(f"Folder: {song_dir}")
    print(f"  ├── {safe_title}_Master.wav        [Direct Play Master]")
    print(f"  ├── {safe_title}.rpp               [REAPER DAW Session]")
    print(f"  ├── {safe_title}.ustx              [OpenUtau Project]")
    print(f"  ├── stems/                         [5x 24-bit Lossless Stems]")
    print(f"  └── midi/                          [5x Standard MIDI Sequences]")
    print("=" * 70)


if __name__ == "__main__":
    main()
