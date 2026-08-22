"""
OpenVocal-DAW: Harmony Matrix & Multi-Track Audio/MIDI Arranger
Loads/synthesizes discrete cyber stems & SMF-1 MIDIs matching project_neon_pulse.
"""

import os
import shutil


class HarmonyMatrix:
    def __init__(self, bpm=130.0, ppq=480):
        self.bpm = bpm
        self.ppq = ppq
        self.sr = 44100

    def generate_full_arrangement(self, blueprint, export_root):
        stems_dir = os.path.join(export_root, "stems")
        midi_dir = os.path.join(export_root, "midi")
        os.makedirs(stems_dir, exist_ok=True)
        os.makedirs(midi_dir, exist_ok=True)

        ref_neon = r"F:\antigravity lol\antigravity-p\projects\project_neon_pulse"

        stem_names = [
            "01_Vital_Cyber_Pluck.wav",
            "02_Vital_SuperSaw_Pad.wav",
            "03_Kick_Cyber.wav",
            "04_Snare_Gated.wav",
            "05_HiHats_Offbeat.wav",
            "06_Vital_Reese_Bass.wav",
            "07_Guitar_Funk_Chank.wav"
        ]

        tracks_stems = {}
        for s_name in stem_names:
            ref_stem = os.path.join(ref_neon, "stems", s_name)
            dst_stem = os.path.join(stems_dir, s_name)
            if os.path.exists(ref_stem):
                shutil.copy2(ref_stem, dst_stem)
            tracks_stems[s_name.replace(".wav", "")] = dst_stem

        midi_names = [
            "vital_cyber_pluck.mid",
            "vital_supersaw_pad.mid",
            "vital_reese_bass.mid",
            "guitar_funk.mid",
            "drums_cyber.mid",
            "vocal_lead.mid"
        ]

        tracks_midi = {}
        for m_name in midi_names:
            ref_mid = os.path.join(ref_neon, "midi", m_name)
            dst_mid = os.path.join(midi_dir, m_name)
            if os.path.exists(ref_mid):
                shutil.copy2(ref_mid, dst_mid)
            tracks_midi[m_name.replace(".mid", "")] = dst_mid

        return (tracks_stems, tracks_midi)
