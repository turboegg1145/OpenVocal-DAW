"""
OpenVocal-DAW: REAPER Project Builder
Generates professional Dual-Layer DAW project files (.rpp) with audio stems
and full MIDI sequence takes.
"""

import os


class ReaperProjectBuilder:
    def __init__(self, bpm=128.0, total_bars=88):
        self.bpm = bpm
        self.total_bars = total_bars
        self.total_seconds = (total_bars * 4 * 60.0 / bpm) + 4.0

    def build_session(self, tracks_config, rpp_output_path, master_wav_path):
        track_blocks = []
        for t in tracks_config:
            name = t["name"]
            wav_file = t.get("wav", "")
            mid_file = t.get("mid", "")
            vol = t.get("vol", "1.0000")
            pan = t.get("pan", "0.0000")
            wav_base = os.path.basename(wav_file)
            mid_base = os.path.basename(mid_file)

            items_str = ""
            if wav_file and os.path.exists(wav_file):
                items_str += f"""    <ITEM
      POSITION 0.00000000000000
      LENGTH {self.total_seconds:.4f}
      MUTE 0
      NAME "{wav_base}"
      VOLPAN 1.0 0.0 1.0 1.0 0
      <SOURCE WAVE
        FILE "{wav_file}"
      >
    >
"""
            if mid_file and os.path.exists(mid_file):
                items_str += f"""    <ITEM
      POSITION 0.00000000000000
      LENGTH {self.total_seconds:.4f}
      MUTE 0
      NAME "{mid_base}"
      <SOURCE MIDI
        FILE "{mid_file}"
      >
    >
"""

            blk = f"""  <TRACK
    NAME "{name}"
    PEAKCOL 16576
    VOLPAN {vol} {pan} -1.0 -1.0 1.0
    MUTESOLO 0 0 0
{items_str}  >"""
            track_blocks.append(blk)

        tracks_joined = "\n".join(track_blocks)
        rpp_content = f"""<REAPER_PROJECT 0.1 "7.0" 1620000000
  RPR_VERSION 7.59
  SAMPLERATE 44100 0 0
  TEMPO {self.bpm:.1f} 4 4
  RENDER_FILE "{master_wav_path}"
  RENDER_PATTERN ""
  RENDER_FMT 0 2 44100
  RENDER_1X 0
  RENDER_RANGE 1 0 {self.total_seconds:.4f}
{tracks_joined}
>
"""
        os.makedirs(os.path.dirname(rpp_output_path), exist_ok=True)
        with open(rpp_output_path, "w", encoding="utf-8") as f:
            f.write(rpp_content)
        return rpp_output_path
