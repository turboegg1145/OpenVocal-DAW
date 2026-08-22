#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenVocal-DAW: Autonomous Song Production Engine
Orchestrates:
1. Blueprint loading & Harmonic Matrix multi-track synthesis
2. Authentic Voicebank vocal slice rendering
3. OpenUtau .ustx YAML project generation
4. REAPER .rpp session generation with VST plugin chains
5. Headless REAPER CLI rendering for genuine VST master audio!
"""

import os
import sys
import json
import time
import argparse
import soundfile as sf

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.env_detector import EnvDetector
from core.harmony_matrix import HarmonyMatrix
from core.openutau_ustx_builder import OpenUtauUstxBuilder
from core.reaper_project_builder import build_rpp_session, ReaperProjectBuilder
from core.utau_vocal_engine import UtauVocalEngine
from core.mastering_dsp import MasteringDSP


def produce_song(blueprint_path):
    if not os.path.exists(blueprint_path):
        print(f"❌ Error: Blueprint file not found: {blueprint_path}")
        sys.exit(1)

    with open(blueprint_path, "r", encoding="utf-8") as f:
        blueprint = json.load(f)

    title = blueprint.get("title", "Untitled Track")
    bpm = float(blueprint.get("bpm", 128.0))
    total_bars = int(blueprint.get("total_bars", 78))

    print("=" * 75)
    print(f"🎵 OpenVocal-DAW Producing Song: '{title}' ({bpm} BPM, {total_bars} Bars)")
    print("=" * 75)

    # Prepare export folders
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-', '(', ')')).strip()
    export_root = os.path.join(PROJECT_ROOT, "export", safe_title)
    stems_dir = os.path.join(export_root, "stems")
    midi_dir = os.path.join(export_root, "midi")
    os.makedirs(stems_dir, exist_ok=True)
    os.makedirs(midi_dir, exist_ok=True)

    cfg = EnvDetector.load_config(PROJECT_ROOT)
    reaper_exe = cfg.get("reaper_exe")

    # 1. Synthesize multi-track accompaniment stems and MIDI
    print("
[Step 1/5] Synthesizing Multi-Track Accompaniment & MIDI sequences...")
    matrix = HarmonyMatrix(bpm=bpm, sample_rate=44100)
    audio_files, midi_files = matrix.generate_full_arrangement(blueprint, stems_dir, midi_dir)

    # 2. Render Vocal with authentic Voicebank
    print("
[Step 2/5] Synthesizing Vocal Track using OpenUtau Voicebank...")
    vocal_engine = UtauVocalEngine()
    vocal_wav_path = os.path.join(stems_dir, "01_Lead_Vocal.wav")
    vocal_engine.render_blueprint(blueprint, vocal_wav_path)
    audio_files["01_Lead_Vocal"] = vocal_wav_path

    # 3. Generate OpenUtau .ustx Project
    print("
[Step 3/5] Generating Native OpenUtau .ustx Project...")
    ustx_path = os.path.join(export_root, f"{safe_title}.ustx")
    OpenUtauUstxBuilder.build_ustx(blueprint, ustx_path)

    # 4. Generate REAPER 10-Track Session (.rpp)
    print("
[Step 4/5] Building REAPER 10-Track Session (.rpp)...")
    rpp_path = os.path.join(export_root, f"{safe_title}.rpp")
    master_wav_path = os.path.join(export_root, f"{safe_title}_Master.wav")
    build_rpp_session(blueprint, audio_files, midi_files, rpp_path, master_wav_path)

    # 5. Render Final Master (REAPER Headless Render -> DSP Limiter)
    print("
[Step 5/5] Mastering Final Audio Track...")
    rendered_via_reaper = False
    if reaper_exe and os.path.exists(reaper_exe):
        success, res = ReaperProjectBuilder.render_with_reaper(reaper_exe, rpp_path, master_wav_path)
        if success:
            print(f"  ✓ [SUCCESS] Rendered authentic VST Master via REAPER: {master_wav_path}")
            rendered_via_reaper = True
        else:
            print(f"  ⚠️ REAPER Headless Render note: {res}")

    if not rendered_via_reaper:
        print("  🎚️ Mixing Stems into 24-bit PCM Master Audio...")
        MasteringDSP.mix_and_master(audio_files, master_wav_path)

    print("
" + "=" * 75)
    print("🎉 SONG PRODUCTION COMPLETE!")
    print(f"📁 Output Directory : {export_root}")
    print(f"🎵 Master WAV       : {master_wav_path}")
    print(f"🎛️ REAPER Project   : {rpp_path}")
    print(f"🎤 OpenUtau Project : {ustx_path}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="OpenVocal-DAW Autonomous Song Production")
    parser.add_argument("blueprint", nargs="?", default="examples/neon_pulse/song_blueprint.json", help="Path to song blueprint JSON")
    args = parser.parse_args()
    produce_song(args.blueprint)


if __name__ == "__main__":
    main()
