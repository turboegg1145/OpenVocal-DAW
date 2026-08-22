"""
OpenVocal-DAW: REAPER Project (.rpp) Generator
Generates full 10-track declarative REAPER sessions with embedded VSTs, MIDI, Stems,
and auto-render configuration for headless CLI rendering.
"""

import os
import sys

def build_rpp_session(blueprint, audio_files, midi_files, output_rpp_path, output_master_wav_path=None):
    bpm = blueprint.get("bpm", 128.0)
    total_bars = blueprint.get("total_bars", 78)
    title = blueprint.get("title", "OpenVocal Track")

    if not output_master_wav_path:
        output_master_wav_path = os.path.splitext(output_rpp_path)[0] + "_Master.wav"

    rpp_dir = os.path.dirname(os.path.abspath(output_rpp_path))
    rel_render_file = os.path.relpath(output_master_wav_path, rpp_dir).replace("/", "\\")

    rpp = []
    rpp.append('<REAPER_PROJECT 0.1 "6.80/x64" 1680000000')
    rpp.append('  RIPPLE 0')
    rpp.append('  GROUPOVERRIDE 0 0 0')
    rpp.append('  AUTOXFADE 1')
    rpp.append('  ENVATTACH 1')
    rpp.append('  POOLEDENVATTACH 0')
    rpp.append('  MIXERFLAG 1')
    rpp.append('  PEAKGAIN 1')
    rpp.append('  FEEDBACK 0')
    rpp.append(f'  TEMPO {bpm} 4 4')
    rpp.append('  SAMPLERATE 44100 0 0')
    
    # Configure Render target inside RPP so `reaper.exe -renderproject` knows where to export
    rpp.append(f'  RENDER_FILE "{rel_render_file}"')
    rpp.append('  RENDER_FMT 0 2 44100')
    rpp.append('  RENDER_RANGE 1 0 0')
    rpp.append('  RENDER_RESAMPLE 3 0 0')
    rpp.append('  RENDER_SPEED 0')

    daw_tracks = blueprint.get("daw_tracks", [])
    if not daw_tracks:
        # Default tracks
        daw_tracks = [
            {"id": "01_Lead_Vocal", "name": "Lead Vocal", "color": 16744448, "volume_db": 0.0, "pan": 0.0},
            {"id": "02_SuperSaw_Pad", "name": "SuperSaw Pad", "color": 33023, "volume_db": -2.0, "pan": 0.0},
            {"id": "03_Cyber_Pluck", "name": "Cyber Pluck", "color": 65535, "volume_db": -3.0, "pan": 0.2},
            {"id": "04_Reese_Bass", "name": "Reese Bass", "color": 16711680, "volume_db": -1.0, "pan": 0.0},
            {"id": "05_Cyber_Drums", "name": "Cyber Drums", "color": 255, "volume_db": 0.0, "pan": 0.0},
            {"id": "06_Funk_Guitar", "name": "Funk Guitar", "color": 65280, "volume_db": -4.0, "pan": -0.2}
        ]

    for idx, tr in enumerate(daw_tracks, start=1):
        tr_id = tr.get("id", f"Track_{idx}")
        tr_name = tr.get("name", tr_id)
        tr_color = tr.get("color", 16777215)
        vol_db = tr.get("volume_db", 0.0)
        pan = tr.get("pan", 0.0)
        vol_linear = 10.0 ** (vol_db / 20.0)

        rpp.append('  <TRACK')
        rpp.append(f'    NAME "{tr_name}"')
        rpp.append(f'    PEAKCOL {tr_color}')
        rpp.append(f'    VOLPAN {vol_linear:.6f} {pan:.6f} -1 -1 1')
        rpp.append('    MUTESOLO 0 0 0')
        rpp.append('    IPHASE 0')
        rpp.append('    ISBUS 0 0')
        rpp.append('    BUSCOMP 0 0 0 0 0')
        rpp.append('    SHOWINMIX 1 0.6 1 0.5 0 0 0')
        rpp.append('    REC 0 0 0 0 0 0 0')

        # Link Stem WAV
        stem_path = audio_files.get(tr_id)
        if stem_path and os.path.exists(stem_path):
            rel_wav = os.path.relpath(stem_path, rpp_dir).replace("/", "\\")
            dur_sec = (total_bars * 4 * (60.0 / bpm))
            rpp.append('    <ITEM')
            rpp.append('      POSITION 0.0')
            rpp.append('      SNAPOFFS 0.0')
            rpp.append(f'      LENGTH {dur_sec:.6f}')
            rpp.append('      LOOP 0')
            rpp.append('      ALLTAKES 0')
            rpp.append('      FADEIN 1 0.005 0 1 0 0')
            rpp.append('      FADEOUT 1 0.05 0 1 0 0')
            rpp.append(f'      NAME "{os.path.basename(stem_path)}"')
            rpp.append('      VOLPAN 1.0 0.0 1.0 -1.0')
            rpp.append('      <SOURCE WAVE')
            rpp.append(f'        FILE "{rel_wav}"')
            rpp.append('      >')
            rpp.append('    >')

        # Link MIDI Take
        mid_path = midi_files.get(tr_id)
        if mid_path and os.path.exists(mid_path):
            rel_mid = os.path.relpath(mid_path, rpp_dir).replace("/", "\\")
            dur_sec = (total_bars * 4 * (60.0 / bpm))
            rpp.append('    <ITEM')
            rpp.append('      POSITION 0.0')
            rpp.append('      SNAPOFFS 0.0')
            rpp.append(f'      LENGTH {dur_sec:.6f}')
            rpp.append('      LOOP 0')
            rpp.append('      ALLTAKES 0')
            rpp.append(f'      NAME "{os.path.basename(mid_path)}"')
            rpp.append('      <SOURCE MIDI')
            rpp.append(f'        FILE "{rel_mid}"')
            rpp.append('      >')
            rpp.append('    >')

        # VST FX Chain
        vst_name = tr.get("vst_plugin")
        if vst_name:
            rpp.append('    <FXCHAIN')
            rpp.append('      WNDRECT 0 0 0 0')
            rpp.append('      SHOW 0')
            rpp.append('      LASTSEL 0')
            rpp.append('      DOCKED 0')
            rpp.append(f'      <VST "{vst_name}"')
            rpp.append('      >')
            rpp.append('    >')

        rpp.append('  >')

    rpp.append('>')
    
    os.makedirs(os.path.dirname(os.path.abspath(output_rpp_path)), exist_ok=True)
    with open(output_rpp_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rpp))
    return output_rpp_path


class ReaperProjectBuilder:
    @staticmethod
    def render_with_reaper(reaper_exe, rpp_path, expected_output_wav):
        if not reaper_exe or not os.path.exists(reaper_exe):
            return False, "REAPER executable not found or not configured."
        if not os.path.exists(rpp_path):
            return False, f"RPP project file not found: {rpp_path}"

        print(f"  🎛️ [REAPER Engine] Launching headless render via '{reaper_exe}'...")
        cmd = [reaper_exe, "-renderproject", rpp_path]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if os.path.exists(expected_output_wav) and os.path.getsize(expected_output_wav) > 1024:
                return True, expected_output_wav
            else:
                return False, f"Render finished but output file not generated: {expected_output_wav}"
        except Exception as e:
            return False, str(e)
