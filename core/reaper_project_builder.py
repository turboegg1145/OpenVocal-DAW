"""
OpenVocal-DAW: REAPER Project Builder
Generates professional Dual-Layer DAW project files (.rpp) with audio stems,
full MIDI sequence takes, and perfectly balanced VST FX Chains.
"""

import os
import re


class ReaperProjectBuilder:
    def __init__(self, bpm=128.0, total_bars=88):
        self.bpm = bpm
        self.total_bars = total_bars
        self.total_seconds = (total_bars * 4 * 60.0 / bpm) + 4.0

    def build_from_blueprint(self, blueprint, rpp_output_path, master_wav_rel_path, fallback_tracks=None):
        daw_tracks = blueprint.get("daw_tracks")
        if daw_tracks:
            return self.build_rich_session(daw_tracks, rpp_output_path, master_wav_rel_path)
        else:
            return self.build_session(fallback_tracks or [], rpp_output_path, master_wav_rel_path)

    def build_rich_session(self, daw_tracks, rpp_output_path, master_wav_rel_path):
        track_blocks = []
        for t in daw_tracks:
            name = t.get("name", "Track")
            volpan = t.get("volpan", "1.0 0.0 -1 -1 1")
            peakcol = t.get("peakcol", 16576)
            wav_file = t.get("wav")
            mid_file = t.get("midi")
            fxchain_raw = t.get("fxchain_raw")

            items_list = []
            if wav_file:
                wav_path_str = wav_file.replace("\\", "/")
                wav_base = os.path.basename(wav_file)
                items_list.append(f"""    <ITEM
      POSITION 0.00000000000000
      LENGTH {self.total_seconds:.4f}
      MUTE 0
      NAME "{wav_base}"
      VOLPAN 1.0 0.0 1.0 1.0 0
      <SOURCE WAVE
        FILE "{wav_path_str}"
      >
    >""")
            if mid_file:
                mid_path_str = mid_file.replace("\\", "/")
                mid_base = os.path.basename(mid_file)
                items_list.append(f"""    <ITEM
      POSITION 0.00000000000000
      LENGTH {self.total_seconds:.4f}
      MUTE 0
      NAME "{mid_base}"
      <SOURCE MIDI
        FILE "{mid_path_str}"
      >
    >""")

            items_str = "\n" + "\n".join(items_list) if items_list else ""
            fx_str = f"\n    {fxchain_raw}" if fxchain_raw else ""
            
            blk = f"""  <TRACK
    NAME "{name}"
    PEAKCOL {peakcol}
    VOLPAN {volpan}
    MUTESOLO 0 0 0{items_str}{fx_str}
  >"""
            track_blocks.append(blk)

        tracks_joined = "\n".join(track_blocks)
        master_str = master_wav_rel_path.replace("\\", "/")
        rpp_content = f"""<REAPER_PROJECT 0.1 "7.0" 1620000000
  RPR_VERSION 7.59
  SAMPLERATE 44100 0 0
  TEMPO {self.bpm:.1f} 4 4
  RENDER_FILE "{master_str}"
  RENDER_PATTERN ""
  RENDER_FMT 0 2 44100
  RENDER_1X 0
  RENDER_RANGE 1 0 {self.total_seconds:.4f}
{tracks_joined}
>
"""
        os.makedirs(os.path.dirname(os.path.abspath(rpp_output_path)), exist_ok=True)
        with open(rpp_output_path, "w", encoding="utf-8") as f:
            f.write(rpp_content)
        return rpp_output_path

    def build_session(self, tracks_config, rpp_output_path, master_wav_rel_path):
        track_blocks = []
        for t in tracks_config:
            name = t["name"]
            wav_file = t.get("wav", "")
            mid_file = t.get("mid", "")
            vol = t.get("vol", "1.0000")
            pan = t.get("pan", "0.0000")
            wav_base = os.path.basename(wav_file) if wav_file else ""
            mid_base = os.path.basename(mid_file) if mid_file else ""

            items_list = []
            if wav_file:
                wav_path_str = wav_file.replace("\\", "/")
                items_list.append(f"""    <ITEM
      POSITION 0.00000000000000
      LENGTH {self.total_seconds:.4f}
      MUTE 0
      NAME "{wav_base}"
      VOLPAN 1.0 0.0 1.0 1.0 0
      <SOURCE WAVE
        FILE "{wav_path_str}"
      >
    >""")
            if mid_file:
                mid_path_str = mid_file.replace("\\", "/")
                items_list.append(f"""    <ITEM
      POSITION 0.00000000000000
      LENGTH {self.total_seconds:.4f}
      MUTE 0
      NAME "{mid_base}"
      <SOURCE MIDI
        FILE "{mid_path_str}"
      >
    >""")

            items_str = "\n" + "\n".join(items_list) if items_list else ""
            blk = f"""  <TRACK
    NAME "{name}"
    PEAKCOL 16576
    VOLPAN {vol} {pan} -1.0 -1.0 1.0
    MUTESOLO 0 0 0{items_str}
  >"""
            track_blocks.append(blk)

        tracks_joined = "\n".join(track_blocks)
        master_str = master_wav_rel_path.replace("\\", "/")
        rpp_content = f"""<REAPER_PROJECT 0.1 "7.0" 1620000000
  RPR_VERSION 7.59
  SAMPLERATE 44100 0 0
  TEMPO {self.bpm:.1f} 4 4
  RENDER_FILE "{master_str}"
  RENDER_PATTERN ""
  RENDER_FMT 0 2 44100
  RENDER_1X 0
  RENDER_RANGE 1 0 {self.total_seconds:.4f}
{tracks_joined}
>
"""
        os.makedirs(os.path.dirname(os.path.abspath(rpp_output_path)), exist_ok=True)
        with open(rpp_output_path, "w", encoding="utf-8") as f:
            f.write(rpp_content)
        return rpp_output_path
