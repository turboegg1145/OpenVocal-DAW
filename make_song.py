"""
OpenVocal-DAW CLI Entrypoint
Autonomous AI Vocal & Music Production Pipeline.
"""

import os
import sys
import json
from core.utau_vocal_engine import UtauVocalEngine
from core.harmony_matrix import HarmonyMatrix
from core.reaper_project_builder import ReaperProjectBuilder
from core.mastering_dsp import MasteringDSP


def main():
    print("=" * 70)
    print("   OpenVocal-DAW: Autonomous AI Vocal & Music Production Toolkit")
    print("=" * 70)
    if len(sys.argv) < 2:
        print("Usage: python make_song.py <path_to_song_blueprint.json>")
        return

    blueprint_path = sys.argv[1]
    with open(blueprint_path, "r", encoding="utf-8") as f:
        blueprint = json.load(f)

    title = blueprint.get("title", "Untitled_Song")
    bpm = float(blueprint.get("bpm", 128.0))
    total_bars = int(blueprint.get("total_bars", 88))
    print(f"Loaded Song: {title} | BPM: {bpm} | Total Bars: {total_bars}")

    print("[1/3] Generating UTAU Vocal Tracks...")
    engine = UtauVocalEngine("", "")
    vocal_wav = engine.render_blueprint(blueprint, "export/vocal_dry.wav")

    print("[2/3] Building REAPER Session...")
    builder = ReaperProjectBuilder(bpm=bpm, total_bars=total_bars)
    rpp_path = builder.build_session([], f"export/{title}.rpp", f"export/{title}_Master.wav")

    print(f"[3/3] Production Complete! DAW Session saved to {rpp_path}")


if __name__ == "__main__":
    main()
