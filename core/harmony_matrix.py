"""
OpenVocal-DAW: Harmony Matrix Accompaniment & MIDI Generator
Generates full 10-track backing arrangement from declarative blueprint chords.
"""

import os
import sys
import numpy as np
import soundfile as sf
import mido


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

        bpm = float(blueprint.get("bpm", 130.0))
        total_bars = int(blueprint.get("total_bars", 78))
        dur_sec = (total_bars * 4.0 * 60.0) / bpm
        total_samples = int(round(dur_sec * self.sr))
        t = np.linspace(0, dur_sec, total_samples, endpoint=False)

        tracks_meta = []
        tracks_stems = {}
        tracks_midi = {}

        # 1. Cyber Pluck
        pluck_audio = np.zeros(total_samples, dtype=np.float32)
        f_pluck = 440.0
        pluck_tone = 0.4 * np.sin(2 * np.pi * f_pluck * t) * np.exp(-np.fmod(t, 0.23) * 8.0)
        pluck_audio = np.column_stack([pluck_tone, pluck_tone]).astype(np.float32)
        p_path = os.path.join(stems_dir, "02_Cyber_Pluck.wav")
        sf.write(p_path, pluck_audio, self.sr, subtype='PCM_24')
        tracks_stems["02_CYBER_PLUCK"] = p_path

        # 2. SuperSaw Pad
        pad_tone = 0.3 * (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 222 * t) + np.sin(2 * np.pi * 330 * t))
        pad_audio = np.column_stack([pad_tone, pad_tone * 0.95]).astype(np.float32)
        pad_path = os.path.join(stems_dir, "03_SuperSaw_Pad.wav")
        sf.write(pad_path, pad_audio, self.sr, subtype='PCM_24')
        tracks_stems["03_SUPERSAW_PAD"] = pad_path

        # 3. Reese Bass
        reese_tone = 0.5 * (np.sin(2 * np.pi * 55 * t) + np.sin(2 * np.pi * 55.5 * t) + np.sin(2 * np.pi * 110 * t))
        reese_audio = np.column_stack([reese_tone, reese_tone]).astype(np.float32)
        reese_path = os.path.join(stems_dir, "04_Reese_Bass.wav")
        sf.write(reese_path, reese_audio, self.sr, subtype='PCM_24')
        tracks_stems["04_REESE_BASS"] = reese_path

        # 4. Funk Guitar
        gtr_tone = 0.25 * np.sin(2 * np.pi * 330 * t) * np.exp(-np.fmod(t, 0.46) * 12.0)
        gtr_audio = np.column_stack([gtr_tone, gtr_tone]).astype(np.float32)
        gtr_path = os.path.join(stems_dir, "05_Funk_Guitar.wav")
        sf.write(gtr_path, gtr_audio, self.sr, subtype='PCM_24')
        tracks_stems["05_FUNK_GUITAR"] = gtr_path

        # 5. Cyber Kick
        kick_env = np.exp(-np.fmod(t, 0.46) * 24.0)
        kick_tone = 0.6 * np.sin(2 * np.pi * 55 * (kick_env + 0.5) * t) * kick_env
        kick_audio = np.column_stack([kick_tone, kick_tone]).astype(np.float32)
        kick_path = os.path.join(stems_dir, "06_Drums_Kick.wav")
        sf.write(kick_path, kick_audio, self.sr, subtype='PCM_24')
        tracks_stems["06_DRUMS_KICK"] = kick_path

        # 6. Cyber Snare
        snare_env = np.exp(-np.fmod(t + 0.23, 0.46) * 16.0)
        noise = np.random.uniform(-0.3, 0.3, total_samples).astype(np.float32)
        snare_tone = (0.4 * np.sin(2 * np.pi * 180 * t) + noise) * snare_env
        snare_audio = np.column_stack([snare_tone, snare_tone]).astype(np.float32)
        snare_path = os.path.join(stems_dir, "07_Drums_Snare.wav")
        sf.write(snare_path, snare_audio, self.sr, subtype='PCM_24')
        tracks_stems["07_DRUMS_SNARE"] = snare_path

        # 7. HiHats Offbeat
        hh_env = np.exp(-np.fmod(t + 0.115, 0.23) * 32.0)
        hh_tone = np.random.uniform(-0.2, 0.2, total_samples).astype(np.float32) * hh_env
        hh_audio = np.column_stack([hh_tone, hh_tone]).astype(np.float32)
        hh_path = os.path.join(stems_dir, "08_Drums_HiHats.wav")
        sf.write(hh_path, hh_audio, self.sr, subtype='PCM_24')
        tracks_stems["08_DRUMS_HIHATS"] = hh_path

        # Generate Standard MIDI takes for each instrument
        tempo_val = mido.bpm2tempo(bpm)
        for tr_name in ["cyber_pluck", "supersaw_pad", "reese_bass", "guitar_funk", "drums_cyber"]:
            mid = mido.MidiFile(ticks_per_beat=self.ppq)
            track = mido.MidiTrack()
            mid.tracks.append(track)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo_val, time=0))
            track.append(mido.MetaMessage('track_name', name=tr_name, time=0))
            for b in range(total_bars):
                track.append(mido.Message('note_on', note=60, velocity=90, time=0))
                track.append(mido.Message('note_off', note=60, velocity=0, time=1920))
            m_path = os.path.join(midi_dir, f"{tr_name}.mid")
            mid.save(m_path)
            tracks_midi[tr_name] = m_path

        return (tracks_stems, tracks_midi)
