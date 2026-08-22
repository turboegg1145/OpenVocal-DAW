#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenVocal-DAW: End-to-End Autonomous Music Production Engine
Synthesizes 100% authentic Kasane Teto (重音テト) vocals, multi-track studio arrangement,
OpenUtau native .ustx projects, and full 10-track REAPER DAW sessions from a 29KB Blueprint.
"""

import os
import sys
import json

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from core.env_detector import EnvDetector
from core.harmony_matrix import HarmonyMatrix
from core.utau_vocal_engine import UtauVocalEngine
from core.openutau_ustx_builder import OpenUtauUstxBuilder
from core.reaper_project_builder import build_rpp_session, ReaperProjectBuilder
from core.mastering_dsp import MasteringDSP


def produce_song(blueprint_path, export_root=None):
    if not os.path.exists(blueprint_path):
        print(f"[Error] Blueprint file not found at: {blueprint_path}")
        sys.exit(1)

    with open(blueprint_path, "r", encoding="utf-8") as f:
        blueprint = json.load(f)

    title = blueprint.get("title", "OpenVocal_Track")
    bpm = float(blueprint.get("bpm", 130.0))
    total_bars = int(blueprint.get("total_bars", 78))

    if not export_root:
        export_root = os.path.join(SCRIPT_DIR, "export", title)
    os.makedirs(export_root, exist_ok=True)

    print("=" * 75)
    print(f"[OpenVocal-DAW] Producing Song: '{title}' ({bpm} BPM, {total_bars} Bars)")
    print("=" * 75)

    config = EnvDetector.load_config()

    # Step 1: Multi-Track Accompaniment & MIDI
    print("\n[Step 1/5] Synthesizing Multi-Track Accompaniment & MIDI sequences...")
    hm = HarmonyMatrix(bpm=bpm, ppq=480)
    tracks_stems, tracks_midi = hm.generate_full_arrangement(blueprint, export_root)
    audio_files = dict(tracks_stems)
    midi_files = dict(tracks_midi)

    # Step 2: Authentic Kasane Teto Vocal Production
    print("\n[Step 2/5] Synthesizing Kasane Teto Vocal Track...")
    vocal_engine = UtauVocalEngine(
        voicebank_path=config.get("openutau_singers_dir"),
        resampler_exe=os.path.join(SCRIPT_DIR, "..", "antigravity-p", "utau_engines", "moresampler.exe")
    )
    vocal_wav_path = os.path.join(export_root, "stems", "01_VOCAL_LEAD.wav")
    vocal_score = blueprint.get("vocal_score", {})
    vocal_engine.render_vocal_track(vocal_score, total_bars=total_bars, bpm=bpm, output_path=vocal_wav_path)
    audio_files["01_VOCAL_LEAD"] = vocal_wav_path

    # Step 3: OpenUtau Project Generation
    print("\n[Step 3/5] Generating Native OpenUtau .ustx Project...")
    ustx_path = os.path.join(export_root, f"{title}.ustx")
    OpenUtauUstxBuilder.build_ustx(blueprint, ustx_path)

    # Step 4: REAPER 10-Track Session (.rpp)
    print("\n[Step 4/5] Building REAPER 10-Track Studio Session (.rpp)...")
    rpp_path = os.path.join(export_root, f"{title}.rpp")
    master_wav_path = os.path.join(export_root, f"{title}_Master.wav")
    build_rpp_session(blueprint, audio_files, midi_files, rpp_path, output_master_wav_path=master_wav_path)

    # Step 5: Mastering Final Audio Track
    print("\n[Step 5/5] Mastering Final Audio Track...")
    reaper_exe = config.get("reaper_exe")
    rendered, msg = ReaperProjectBuilder.render_with_reaper(reaper_exe, rpp_path, master_wav_path)
    if not rendered:
        MasteringDSP.mix_and_master(audio_files, master_wav_path)

    print("\n" + "=" * 75)
    print("[SUCCESS] SONG PRODUCTION COMPLETE!")
    print(f"  * Output Directory : {export_root}")
    print(f"  * Master WAV       : {master_wav_path}")
    print(f"  * REAPER Project   : {rpp_path}")
    print(f"  * OpenUtau Project : {ustx_path}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        bp_in = sys.argv[1]
    else:
        bp_in = os.path.join(SCRIPT_DIR, "examples", "neon_pulse", "song_blueprint.json")
    produce_song(bp_in)
