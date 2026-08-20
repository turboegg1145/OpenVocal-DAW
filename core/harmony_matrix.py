"""
OpenVocal-DAW: SoundQuest Harmonic Matrix & Backing Track Engine
Generates multi-track MIDI and rendered acoustic stems for Grand Piano, Bass, Drums, and Synth.
"""

import os
import re
import numpy as np
import soundfile as sf
import mido
from mido import MidiFile, MidiTrack, Message

ROOT_MAP = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

CHORD_INTERVALS = {
    'maj7': [0, 4, 7, 11],
    'maj': [0, 4, 7],
    'm7': [0, 3, 7, 10],
    'm': [0, 3, 7],
    '7': [0, 4, 7, 10],
    'dim7': [0, 3, 6, 9],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'sus4': [0, 5, 7],
    '7sus4': [0, 5, 7, 10],
    'add9': [0, 4, 7, 14],
    'm9': [0, 3, 7, 10, 14],
    '9': [0, 4, 7, 10, 14]
}


def parse_chord_name(chord_str):
    c = str(chord_str).strip()
    if not c or c in ['N.C.', 'NC', 'R', '']:
        return None, []
    m = re.match(r'^([A-G][#b]?)(.*)$', c)
    if not m:
        return 60, [0, 4, 7]
    root_str, qual_str = m.groups()
    root_pc = ROOT_MAP.get(root_str, 0)
    qual = qual_str.strip()
    if qual in CHORD_INTERVALS:
        intervals = CHORD_INTERVALS[qual]
    elif qual.startswith('m') and '7' in qual:
        intervals = CHORD_INTERVALS['m7']
    elif qual.startswith('m'):
        intervals = CHORD_INTERVALS['m']
    elif 'maj7' in qual or 'M7' in qual:
        intervals = CHORD_INTERVALS['maj7']
    elif '7' in qual:
        intervals = CHORD_INTERVALS['7']
    elif 'dim' in qual:
        intervals = CHORD_INTERVALS['dim']
    elif 'sus' in qual:
        intervals = CHORD_INTERVALS['sus4']
    else:
        intervals = CHORD_INTERVALS['maj']
    return root_pc, intervals


class HarmonyMatrix:
    def __init__(self, bpm=128.0, ppq=480):
        self.bpm = bpm
        self.ppq = ppq
        self.bar_ticks = ppq * 4
        self.sr = 44100

    def flatten_chords(self, chords_spec, total_bars):
        chord_list = ["C"] * total_bars
        if isinstance(chords_spec, list):
            for i, c in enumerate(chords_spec):
                if i < total_bars: chord_list[i] = c
        elif isinstance(chords_spec, dict):
            for k, v in chords_spec.items():
                if "-" in str(k):
                    parts = str(k).split("-")
                    try:
                        s_bar, e_bar = int(parts[0]), int(parts[1])
                        if isinstance(v, list):
                            for idx, c in enumerate(v):
                                b = s_bar + idx
                                if b <= e_bar and b < total_bars:
                                    chord_list[b] = c
                        elif isinstance(v, str):
                            for b in range(s_bar, min(e_bar + 1, total_bars)):
                                chord_list[b] = v
                    except Exception:
                        pass
                else:
                    try:
                        b = int(k)
                        if b < total_bars: chord_list[b] = str(v)
                    except Exception:
                        pass
        return chord_list

    def generate_full_arrangement(self, blueprint, song_dir):
        stems_dir = os.path.join(song_dir, "stems")
        midi_dir = os.path.join(song_dir, "midi")
        os.makedirs(stems_dir, exist_ok=True)
        os.makedirs(midi_dir, exist_ok=True)

        bpm = float(blueprint.get("bpm", 128.0))
        total_bars = int(blueprint.get("total_bars", 88))
        self.bpm = bpm
        chords_per_bar = self.flatten_chords(blueprint.get("chords", {}), total_bars)
        sec_per_bar = (4.0 * 60.0) / bpm
        total_samples = int(round(total_bars * sec_per_bar * self.sr))

        # 1. PIANO
        piano_mid_path = os.path.join(midi_dir, "02_Grand_Piano.mid")
        piano_wav_path = os.path.join(stems_dir, "02_Grand_Piano.wav")
        piano_mid = MidiFile(ticks_per_beat=self.ppq)
        p_trk = MidiTrack()
        piano_mid.tracks.append(p_trk)
        p_trk.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        p_audio = np.zeros(total_samples, dtype=np.float32)

        # 2. BASS
        bass_mid_path = os.path.join(midi_dir, "03_Bass.mid")
        bass_wav_path = os.path.join(stems_dir, "03_Bass.wav")
        bass_mid = MidiFile(ticks_per_beat=self.ppq)
        b_trk = MidiTrack()
        bass_mid.tracks.append(b_trk)
        b_trk.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        b_audio = np.zeros(total_samples, dtype=np.float32)

        # 3. DRUMS
        drums_mid_path = os.path.join(midi_dir, "04_Drums.mid")
        drums_wav_path = os.path.join(stems_dir, "04_Drums.wav")
        drums_mid = MidiFile(ticks_per_beat=self.ppq)
        d_trk = MidiTrack()
        drums_mid.tracks.append(d_trk)
        d_trk.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        d_audio = np.zeros(total_samples, dtype=np.float32)

        # 4. SYNTH LEAD
        synth_mid_path = os.path.join(midi_dir, "05_Synth_Lead.mid")
        synth_wav_path = os.path.join(stems_dir, "05_Synth_Lead.wav")
        synth_mid = MidiFile(ticks_per_beat=self.ppq)
        s_trk = MidiTrack()
        synth_mid.tracks.append(s_trk)
        s_trk.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        s_audio = np.zeros(total_samples, dtype=np.float32)

        quarter_samples = int(round((60.0 / bpm) * self.sr))
        eighth_samples = quarter_samples // 2
        sixteenth_samples = quarter_samples // 4

        for bar_idx in range(total_bars):
            chord_name = chords_per_bar[bar_idx]
            root_pc, intervals = parse_chord_name(chord_name)
            bar_start_sample = int(round(bar_idx * sec_per_bar * self.sr))

            # --- PIANO ---
            if root_pc is not None:
                chord_pitches = [60 + root_pc + iv for iv in intervals]
                for beat in range(4):
                    dur_ticks = self.ppq - 20
                    for idx, p in enumerate(chord_pitches):
                        p_trk.append(Message('note_on', note=p, velocity=88, time=0))
                    for idx, p in enumerate(chord_pitches):
                        delta = dur_ticks if idx == 0 else 0
                        p_trk.append(Message('note_off', note=p, velocity=0, time=delta))
                    p_trk.append(Message('note_off', note=0, velocity=0, time=20))

                    b_sample = bar_start_sample + beat * quarter_samples
                    env_len = min(quarter_samples * 2, total_samples - b_sample)
                    if env_len > 0:
                        t = np.linspace(0, env_len / self.sr, env_len, endpoint=False)
                        decay = np.exp(-4.5 * t)
                        wave = np.zeros(env_len, dtype=np.float32)
                        for p in chord_pitches:
                            freq = 440.0 * (2.0 ** ((p - 69) / 12.0))
                            wave += 0.4 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * 2 * freq * t)
                        p_audio[b_sample:b_sample+env_len] += (wave * decay * 0.25).astype(np.float32)

            # --- BASS ---
            if root_pc is not None:
                bass_pitch = 36 + root_pc
                for e_idx in range(8):
                    dur_ticks = (self.ppq // 2) - 15
                    b_trk.append(Message('note_on', note=bass_pitch, velocity=95, time=0))
                    b_trk.append(Message('note_off', note=bass_pitch, velocity=0, time=dur_ticks))
                    b_trk.append(Message('note_off', note=0, velocity=0, time=15))

                    b_sample = bar_start_sample + e_idx * eighth_samples
                    env_len = min(eighth_samples * 2, total_samples - b_sample)
                    if env_len > 0:
                        t = np.linspace(0, env_len / self.sr, env_len, endpoint=False)
                        freq = 440.0 * (2.0 ** ((bass_pitch - 69) / 12.0))
                        decay = np.exp(-3.0 * t)
                        wave = np.sin(2 * np.pi * freq * t) + 0.45 * np.sin(2 * np.pi * 2 * freq * t)
                        b_audio[b_sample:b_sample+env_len] += (wave * decay * 0.35).astype(np.float32)

            # --- DRUMS ---
            for beat in range(4):
                d_trk.append(Message('note_on', channel=9, note=36, velocity=105, time=0))
                d_trk.append(Message('note_off', channel=9, note=36, velocity=0, time=120))
                if beat in [1, 3]:
                    d_trk.append(Message('note_on', channel=9, note=38, velocity=100, time=0))
                    d_trk.append(Message('note_off', channel=9, note=38, velocity=0, time=120))
                d_trk.append(Message('note_off', channel=9, note=0, velocity=0, time=self.ppq - 120))

                k_sample = bar_start_sample + beat * quarter_samples
                k_len = min(int(0.25 * self.sr), total_samples - k_sample)
                if k_len > 0:
                    t_k = np.linspace(0, k_len / self.sr, k_len, endpoint=False)
                    f_env = 140.0 * np.exp(-25.0 * t_k) + 45.0
                    phase = 2 * np.pi * np.cumsum(f_env) / self.sr
                    d_audio[k_sample:k_sample+k_len] += (np.sin(phase) * np.exp(-12.0 * t_k) * 0.55).astype(np.float32)
                if beat in [1, 3]:
                    s_len = min(int(0.22 * self.sr), total_samples - k_sample)
                    if s_len > 0:
                        t_s = np.linspace(0, s_len / self.sr, s_len, endpoint=False)
                        noise = np.random.uniform(-1, 1, s_len) * np.exp(-18.0 * t_s)
                        tone = np.sin(2 * np.pi * 180.0 * t_s) * np.exp(-22.0 * t_s)
                        d_audio[k_sample:k_sample+s_len] += ((noise * 0.4 + tone * 0.3) * 0.5).astype(np.float32)

            # --- SYNTH LEAD ---
            if root_pc is not None:
                arp_tones = [72 + root_pc + iv for iv in intervals]
                for s_idx in range(16):
                    cur_p = arp_tones[s_idx % len(arp_tones)]
                    dur_ticks = (self.ppq // 4) - 10
                    s_trk.append(Message('note_on', note=cur_p, velocity=80, time=0))
                    s_trk.append(Message('note_off', note=cur_p, velocity=0, time=dur_ticks))
                    s_trk.append(Message('note_off', note=0, velocity=0, time=10))

                    s_sample = bar_start_sample + s_idx * sixteenth_samples
                    env_len = min(sixteenth_samples * 2, total_samples - s_sample)
                    if env_len > 0:
                        t = np.linspace(0, env_len / self.sr, env_len, endpoint=False)
                        freq = 440.0 * (2.0 ** ((cur_p - 69) / 12.0))
                        decay = np.exp(-10.0 * t)
                        saw = 2.0 * (t * freq - np.floor(0.5 + t * freq))
                        s_audio[s_sample:s_sample+env_len] += (saw * decay * 0.15).astype(np.float32)

        for audio, path in [(p_audio, piano_wav_path), (b_audio, bass_wav_path), (d_audio, drums_wav_path), (s_audio, synth_wav_path)]:
            pk = np.max(np.abs(audio))
            if pk > 0: audio = (audio / pk) * 0.85
            sf.write(path, audio, self.sr, subtype='PCM_24')

        piano_mid.save(piano_mid_path)
        bass_mid.save(bass_mid_path)
        drums_mid.save(drums_mid_path)
        synth_mid.save(synth_mid_path)

        # 5. VOCAL LEAD MIDI
        vocal_mid_path = os.path.join(midi_dir, "01_Lead_Vocal.mid")
        v_mid = MidiFile(ticks_per_beat=self.ppq)
        v_trk = MidiTrack()
        v_mid.tracks.append(v_trk)
        v_trk.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))

        vocal_score = blueprint.get("vocal_score", {})
        for b in range(total_bars):
            bar_notes = vocal_score.get(str(b), vocal_score.get(b, []))
            for item in bar_notes:
                lyric, ticks, pitch, vel = item[0], int(item[1]), int(item[2]), int(item[3])
                if lyric not in ["R", "r", "", "-"]:
                    v_trk.append(Message('note_on', note=pitch, velocity=vel, time=0))
                    v_trk.append(Message('note_off', note=pitch, velocity=0, time=ticks))
                else:
                    v_trk.append(Message('note_off', note=0, velocity=0, time=ticks))
        v_mid.save(vocal_mid_path)

        # Tracks metadata with portable relative paths
        tracks_meta = [
            {"name": "01_Lead_Vocal", "wav": "stems/01_Lead_Vocal.wav", "mid": "midi/01_Lead_Vocal.mid", "vol": "1.0000", "pan": "0.0000"},
            {"name": "02_Grand_Piano", "wav": "stems/02_Grand_Piano.wav", "mid": "midi/02_Grand_Piano.mid", "vol": "0.8500", "pan": "-0.2000"},
            {"name": "03_Bass", "wav": "stems/03_Bass.wav", "mid": "midi/03_Bass.mid", "vol": "0.9000", "pan": "0.0000"},
            {"name": "04_Drums", "wav": "stems/04_Drums.wav", "mid": "midi/04_Drums.mid", "vol": "0.9500", "pan": "0.0000"},
            {"name": "05_Synth_Lead", "wav": "stems/05_Synth_Lead.wav", "mid": "midi/05_Synth_Lead.mid", "vol": "0.7500", "pan": "0.2500"}
        ]
        backing_audio = p_audio + b_audio + d_audio + s_audio
        return tracks_meta, backing_audio
