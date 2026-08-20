# OpenVocal-DAW 🎵

> **Autonomous AI Vocal Synthesis & DAW Multi-Track Production Toolkit + UTAU MCP Server**  
> An open-source, end-to-end framework integrating **UTAU / OpenUtau acoustic vocal synthesis**, **SoundQuest harmonic sequencing**, **automated REAPER DAW project assembly**, and **Native Model Context Protocol (MCP) Server support**.

---

## 🌟 Key Features

1. 🎤 **Precision UTAU Vocal Engine & MCP Server**:
   - Automated phonetic alias resolution (`oto.ini` parser with Shift-JIS / CP932 / UTF-8 / GBK support).
   - Pre-utterance timing shift alignment so vowel nuclei land strictly on the beat grid.
   - Formant-optimized rendering (`Flags=g0` / `Flags=g-2`) with 25ms cosine-squared crossfading ($w_{in} + w_{out} = 1.0$).
   - Strict float 0.0 silence (-180 dBFS) rest gating (zero wavtool clicking/artifacts).
   - **Native MCP Server (`mcp_server/server.py`)** providing 5 standardized JSON-RPC 2.0 tools for LLMs & AI agents.

2. 🎹 **SoundQuest Harmonic Matrix & Sequencer**:
   - Enforces 1920 ticks/bar clock lock ($480\text{ PPQ} \times 4$).
   - Multi-track standard MIDI generation for Grand Piano, Precision Bass, Acoustic/Electric Guitar, Drums, and Synths.
   - Harmonic avoidance check and functional chord progressions.

3. 🎛️ **Dual-Layer REAPER DAW Automation**:
   - Automated `.rpp` session generation mounting 24-bit lossless audio stems for instant playback.
   - Parallel MIDI take items embedded under audio stems for immediate piano-roll editing.
   - Automated render configuration and VST plugin chain mounting (Piano One, Ample Bass, MT Power DrumKit, Vital, Valhalla Supermassive).

4. 🎚️ **Mastering DSP Suite**:
   - Analog tape glue saturation modeling (`tanh` soft-clipping).
   - True-Peak brickwall limiter locked to $-0.3\text{ dBFS}$ with dynamic LUFS loudness optimization.

---

## 🤖 UTAU MCP Server (Model Context Protocol)

`OpenVocal-DAW` includes a zero-dependency **UTAU MCP Server** enabling LLM agents (Antigravity, Claude, Cursor, VS Code) to perform real-time vocal tuning and synthesis directly.

### Exposed MCP Tools:
* 🔍 `utau_inspect_voicebank`: Inspect voicebank metadata, phoneme boundaries, oto.ini aliases, and timing parameters.
* 🎵 `utau_render_note`: Synthesize a single vocal note with specific pitch, duration, and formant flags (`Flags=g0` / `Flags=g-2`).
* 🎶 `utau_render_phrase`: Synthesize a connected vocal phrase with 25ms cosine-squared crossfading on the beat grid.
* 🎛️ `utau_tune_pitch_curve`: Generate micro-tuned pitch bend, portamento, and vibrato (`VBR`) envelopes.
* 🚀 `utau_render_full_track`: Compile an entire song blueprint (`song_blueprint.json`) into a pristine 24-bit master vocal track.

### MCP Configuration Example (`mcpSettings.json`):
```json
{
  "mcpServers": {
    "utau-mcp": {
      "command": "python",
      "args": ["F:/antigravity lol/github项目/OpenVocal-DAW/mcp_server/server.py"]
    }
  }
}
```

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/turboegg1145/OpenVocal-DAW.git
cd OpenVocal-DAW
pip install -r requirements.txt
```

### Self-Test MCP Server
```bash
python mcp_server/test_mcp.py
```

### Render a Song from Blueprint
```bash
python make_song.py examples/neon_pulse/song_blueprint.json
```

---

## 📂 Project Architecture

```
OpenVocal-DAW/
├── core/
│   ├── __init__.py
│   ├── utau_vocal_engine.py       # UTAU physics & acoustic synthesis engine
│   ├── harmony_matrix.py          # SoundQuest harmonic sequencer & MIDI builder
│   ├── reaper_project_builder.py  # Dual-layer REAPER .rpp project generator
│   └── mastering_dsp.py           # Tape glue & True-Peak limiter (-0.3 dBFS)
├── mcp_server/
│   ├── __init__.py
│   ├── server.py                  # Standard Stdio JSON-RPC 2.0 MCP Server
│   ├── utau_tools.py              # Atomic MCP vocal tuning & synthesis tools
│   └── test_mcp.py                # Stdio RPC integration test suite
├── examples/
│   └── neon_pulse/                # Example Song Blueprint & REAPER Session
│       ├── song_blueprint.json
│       └── project_neon_pulse.rpp
├── make_song.py                   # Master production CLI
├── requirements.txt
├── LICENSE                        # MIT License
└── README.md
```

---

## 📄 License
MIT License (c) 2026 turboegg1145
