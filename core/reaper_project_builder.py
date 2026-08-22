"""
OpenVocal-DAW: Rich REAPER Session (.rpp) Generator
Constructs complete multi-track REAPER DAW sessions with embedded Audio Items,
MIDI Takes, VST Instrument/FX Chains, and Render Configurations.
"""

import os
import sys
import subprocess

DEFAULT_TRACK_SPECS = {
    "01_Lead_Vocal": {
        "name": "01_LEAD_VOCAL",
        "color": 16744448,
        "vol": 1.15,
        "pan": 0.0,
        "vst": [
            'VST "VST: ReaEQ (Cockos)" reaeq.dll 0 "" 1919247729',
            'VST "VST: ReaComp (Cockos)" reacomp.dll 0 "" 1919246960'
        ]
    },
    "02_SuperSaw_Pad": {
        "name": "02_SUPERSAW_PAD",
        "color": 33023,
        "vol": 0.85,
        "pan": -0.15,
        "vst": [
            'VST "VSTi: NeoPiano (SoundMagic (Wang YiChi))" Neo_Piano_x64.dll 0 "" 1313884466'
        ]
    },
    "03_Cyber_Pluck": {
        "name": "03_CYBER_PLUCK",
        "color": 65535,
        "vol": 0.80,
        "pan": 0.20,
        "vst": [
            'VST "VST: ReaDelay (Cockos)" readelay.dll 0 "" 1919247212'
        ]
    },
    "04_Reese_Bass": {
        "name": "04_REESE_BASS",
        "color": 16711680,
        "vol": 0.95,
        "pan": 0.0,
        "vst": [
            'VST "VSTi: Ample Bass P Lite II (Ample Sound)" ABPL_64.dll 0 "" 1094930514'
        ]
    },
    "05_Cyber_Drums": {
        "name": "05_CYBER_DRUMS",
        "color": 255,
        "vol": 1.00,
        "pan": 0.0,
        "vst": [
            'VST "VSTi: MT-PowerDrumKit (MANDA AUDIO)" MT-PowerDrumKit.dll 0 "" 1297371211'
        ]
    },
    "06_Funk_Guitar": {
        "name": "06_FUNK_GUITAR",
        "color": 65280,
        "vol": 0.75,
        "pan": -0.20,
        "vst": [
            'VST "VSTi: Ample Guitar M Lite II (Ample Sound)" AGML_64.dll 0 "" 1095322962'
        ]
    }
}


def build_rpp_session(blueprint, audio_files, midi_files, output_rpp_path, output_master_wav_path=None):
    bpm = float(blueprint.get("bpm", 128.0))
    total_bars = int(blueprint.get("total_bars", 78))
    dur_sec = (total_bars * 4 * (60.0 / bpm))

    if not output_master_wav_path:
        output_master_wav_path = os.path.splitext(output_rpp_path)[0] + "_Master.wav"

    rpp_dir = os.path.dirname(os.path.abspath(output_rpp_path))
    rel_render_file = os.path.relpath(output_master_wav_path, rpp_dir).replace("/", "\\")

    rpp = []
    rpp.append('<REAPER_PROJECT 0.1 "7.0" 1620000000')
    rpp.append('  RPR_VERSION 7.59')
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
    
    # Configure Render target inside RPP
    rpp.append(f'  RENDER_FILE "{rel_render_file}"')
    rpp.append('  RENDER_PATTERN ""')
    rpp.append('  RENDER_FMT 0 2 44100')
    rpp.append('  RENDER_1X 0')
    rpp.append(f'  RENDER_RANGE 1 0 {dur_sec:.4f}')
    rpp.append('  RENDER_RESAMPLE 3 0 1')
    rpp.append('  RENDER_DITHER 0')
    rpp.append('  <RENDER_CFG')
    rpp.append('    ZXZhdxgAAA==')
    rpp.append('  >')

    all_track_keys = list(dict.fromkeys(list(audio_files.keys()) + list(midi_files.keys())))
    if not all_track_keys:
        all_track_keys = list(DEFAULT_TRACK_SPECS.keys())

    for idx, tr_key in enumerate(all_track_keys, start=1):
        spec = DEFAULT_TRACK_SPECS.get(tr_key, {
            "name": tr_key,
            "color": 16777215,
            "vol": 1.0,
            "pan": 0.0,
            "vst": []
        })

        tr_name = spec["name"]
        tr_color = spec["color"]
        vol_linear = spec["vol"]
        pan = spec["pan"]

        rpp.append('  <TRACK')
        rpp.append(f'    NAME "{tr_name}"')
        rpp.append(f'    PEAKCOL {tr_color}')
        rpp.append(f'    VOLPAN {vol_linear:.6f} {pan:.6f} -1 -1 1')
        rpp.append('    MUTESOLO 0 0 0')
        rpp.append('    IPHASE 0')
        rpp.append('    ISBUS 0 0')
        rpp.append('    SHOWINMIX 1 0.6 1 0.5 0 0 0')
        rpp.append('    REC 0 0 0 0 0 0 0')

        # Link Stem WAV item
        stem_path = audio_files.get(tr_key)
        if stem_path and os.path.exists(stem_path):
            rel_wav = os.path.relpath(stem_path, rpp_dir).replace("/", "\\")
            rpp.append('    <ITEM')
            rpp.append('      POSITION 0.00000000000000')
            rpp.append('      SNAPOFFS 0.00000000000000')
            rpp.append(f'      LENGTH {dur_sec:.6f}')
            rpp.append('      LOOP 0')
            rpp.append('      ALLTAKES 0')
            rpp.append('      MUTE 0')
            rpp.append(f'      NAME "{os.path.basename(stem_path)}"')
            rpp.append('      VOLPAN 1.00000000000000 0.00000000000000 1.00000000000000 1.00000000000000 0')
            rpp.append('      SOFFS 0.00000000000000')
            rpp.append('      PLAYRATE 1.00000000000000 1 0.00000000000000 -1')
            rpp.append('      CHANMODE 0')
            rpp.append('      <SOURCE WAVE')
            rpp.append(f'        FILE "{rel_wav}"')
            rpp.append('      >')
            rpp.append('    >')

        # Link MIDI item
        mid_path = midi_files.get(tr_key)
        if mid_path and os.path.exists(mid_path):
            rel_mid = os.path.relpath(mid_path, rpp_dir).replace("/", "\\")
            rpp.append('    <ITEM')
            rpp.append('      POSITION 0.00000000000000')
            rpp.append('      SNAPOFFS 0.00000000000000')
            rpp.append(f'      LENGTH {dur_sec:.6f}')
            rpp.append('      LOOP 0')
            rpp.append('      ALLTAKES 0')
            rpp.append('      MUTE 0')
            rpp.append(f'      NAME "{os.path.basename(mid_path)}"')
            rpp.append('      VOLPAN 1.00000000000000 0.00000000000000 1.00000000000000 1.00000000000000 0')
            rpp.append('      SOFFS 0.00000000000000')
            rpp.append('      PLAYRATE 1.00000000000000 1 0.00000000000000 -1')
            rpp.append('      CHANMODE 0')
            rpp.append('      <SOURCE MIDI')
            rpp.append(f'        FILE "{rel_mid}"')
            rpp.append('      >')
            rpp.append('    >')

        # VST FX Chain
        vsts = spec.get("vst", [])
        if vsts:
            rpp.append('    <FXCHAIN')
            rpp.append('      SHOW 0')
            rpp.append('      LASTSEL 0')
            rpp.append('      DOCKED 0')
            rpp.append('      BYPASS 0 0 0')
            for v_entry in vsts:
                rpp.append(f'      <{v_entry}')
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
    def build_project(blueprint, audio_files, midi_files, output_rpp_path, output_master_wav_path=None):
        return build_rpp_session(blueprint, audio_files, midi_files, output_rpp_path, output_master_wav_path)

    @staticmethod
    def render_with_reaper(reaper_exe, rpp_path, expected_output_wav):
        if not reaper_exe or not os.path.exists(reaper_exe):
            return False, "REAPER executable not configured."
        if not os.path.exists(rpp_path):
            return False, f"RPP project file not found: {rpp_path}"

        print(f"  🎛️ [REAPER Engine] Attempting background render via '{reaper_exe}'...")
        cmd = [reaper_exe, "-renderproject", rpp_path]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8)
            if os.path.exists(expected_output_wav) and os.path.getsize(expected_output_wav) > 1024:
                return True, expected_output_wav
            else:
                return False, "REAPER background render skipped (ready for interactive GUI export)."
        except subprocess.TimeoutExpired:
            return False, "REAPER background render timed out (interactive GUI mode active)."
        except Exception as e:
            return False, str(e)
