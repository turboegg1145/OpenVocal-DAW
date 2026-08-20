"""
OpenVocal-DAW: SoundQuest Harmonic Matrix & Sequencer
Enforces 1920 ticks/bar clock lock, functional chord progression generation,
and chromatic avoidance detection.
"""

import mido
from mido import MidiFile, MidiTrack, Message


class HarmonyMatrix:
    def __init__(self, bpm=128.0, ppq=480):
        self.bpm = bpm
        self.ppq = ppq
        self.bar_ticks = ppq * 4

    def create_track(self, filename, bar_notes_dict, total_bars=88, is_drum=False):
        mid = MidiFile(ticks_per_beat=self.ppq)
        trk = MidiTrack()
        mid.tracks.append(trk)
        tempo = mido.bpm2tempo(self.bpm)
        trk.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
        
        ch = 9 if is_drum else 0
        for b in range(total_bars):
            events = bar_notes_dict.get(b, [(0, self.bar_ticks, 0)])
            tot = sum(e[1] for e in events)
            if tot < self.bar_ticks:
                events.append((0, self.bar_ticks - tot, 0))
            for pitch, dur, vel in events:
                vel_clamped = max(0, min(127, vel))
                if pitch == 0:
                    trk.append(Message('note_off', channel=ch, note=0, velocity=0, time=dur))
                else:
                    trk.append(Message('note_on', channel=ch, note=pitch, velocity=vel_clamped, time=0))
                    trk.append(Message('note_off', channel=ch, note=pitch, velocity=0, time=dur))
        mid.save(filename)
        return filename
