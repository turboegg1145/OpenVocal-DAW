"""
OpenVocal-DAW: OpenUtau .ustx Project Generator
Generates native YAML-based OpenUtau v0.6+ project files (.ustx) with multi-track,
phoneticizer selection, DiffSinger/classic engine binding, and micro-tuning curves.
"""

import os
import json
import yaml


def midi_num_to_tone(m):
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


class OpenUtauUstxBuilder:
    def __init__(self, title="OpenUtau_Song", bpm=128.0, beat_per_bar=4, beat_unit=4):
        self.title = title
        self.bpm = bpm
        self.beat_per_bar = beat_per_bar
        self.beat_unit = beat_unit
        self.resolution = 480
        self.tracks = []
        self.voice_parts = []

    def add_track(self, track_name, singer="Kasane Teto [UTAU]", phoneticizer="OpenUtau.Core.DefaultPhoneticizer", renderer="CLASSIC"):
        track_idx = len(self.tracks)
        self.tracks.append({
            "singer": singer,
            "phoneticizer": phoneticizer,
            "renderer_settings": {
                "renderer": renderer,
                "resampler": "moresampler.exe"
            },
            "track_name": track_name,
            "track_color": "Blue" if track_idx == 0 else "Purple",
            "mute": False,
            "solo": False,
            "volume": 0.0,
            "pan": 0.0
        })
        return track_idx

    def add_voice_part(self, track_no, part_name, notes_list, start_pos=0):
        notes_entries = []
        cur_pos = 0
        for n in notes_list:
            lyric = n.get("lyric", "あ")
            ticks = n.get("ticks", 480)
            pitch = n.get("pitch", 60)
            pitch_num = tone_to_midi_num(pitch) if isinstance(pitch, str) else int(pitch)
            vel = n.get("vel", 100)

            if lyric not in ["R", "r", "", "-"]:
                note_dict = {
                    "position": cur_pos,
                    "duration": ticks,
                    "tone": pitch_num,
                    "lyric": lyric,
                    "pitch": {
                        "data": [
                            {"x": -40, "y": 0, "shape": "io"},
                            {"x": 40, "y": 0, "shape": "io"}
                        ],
                        "snap_first": True
                    },
                    "vibrato": {
                        "length": 65,
                        "period": 175,
                        "depth": 25,
                        "in": 15,
                        "out": 15,
                        "shift": 0,
                        "drift": 0,
                        "vol_link": 0
                    }
                }
                notes_entries.append(note_dict)
            cur_pos += ticks

        self.voice_parts.append({
            "name": part_name,
            "track_no": track_no,
            "position": start_pos,
            "notes": notes_entries
        })

    def export_ustx_yaml(self, output_path):
        ustx_data = {
            "name": self.title,
            "comment": "Generated automatically by OpenVocal-DAW OpenUtau Engine",
            "output_dir": "Vocal",
            "cache_dir": "Cache",
            "ustx_version": "0.6",
            "bpm": self.bpm,
            "beat_per_bar": self.beat_per_bar,
            "beat_unit": self.beat_unit,
            "resolution": self.resolution,
            "tracks": self.tracks,
            "voice_parts": self.voice_parts,
            "curves": []
        }
        d = os.path.dirname(os.path.abspath(output_path))
        if d: os.makedirs(d, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(ustx_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        return output_path
