# OpenVocal-DAW 🎵

> **Autonomous AI Vocal Synthesis & DAW Multi-Track Production Toolkit + Modern OpenUtau MCP Server**  
> An open-source, end-to-end framework integrating **OpenUtau (.ustx) project generation**, **DiffSinger / neural voice model tuning**, **SoundQuest harmonic sequencing**, **automated REAPER DAW project assembly**, and **Native OpenUtau Model Context Protocol (MCP) Server support**.

---

## 🌟 Key Features

1. 🎤 **Modern OpenUtau Engine & MCP Server**:
   - Native YAML-based **`.ustx` project generator** (compatible with OpenUtau v0.6+).
   - Automated multi-track layout (Lead, Harmony, Backing) with Singer ID and Phoneticizer bindings (`OpenUtau.Core.DefaultPhoneticizer`, `JapaneseVCVPhoneticizer`, `DiffSingerPhoneticizer`).
   - DiffSinger / neural expression curve generation (Dynamics `dyn`, Tension `tns`, Breathiness `bre`, Voicing `voi`).
   - 25ms cosine-squared crossfading acoustic preview synthesis ($w_{in} + w_{out} = 1.0$).
   - **Native OpenUtau MCP Server (`mcp_server/server.py`)** providing 5 standardized JSON-RPC 2.0 tools for LLMs & AI agents.

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

## 🤖 OpenUtau MCP Server (Model Context Protocol)

`OpenVocal-DAW` includes a dedicated **OpenUtau MCP Server** enabling LLM agents (Antigravity, Claude, Cursor, VS Code) to directly build, inspect, and fine-tune OpenUtau projects.

### Exposed MCP Tools:
* 🛠️ `openutau_build_ustx`: Build a native modern OpenUtau project file (`.ustx`) with multi-track layout, phoneticizers, and singer bindings.
* 🔍 `openutau_inspect_project`: Inspect and parse an existing OpenUtau `.ustx` project file, returning tracks, singers, notes, and metadata.
* 🎛️ `openutau_tune_expression`: Configure expression curves for DiffSinger/neural voices (Dynamics `dyn`, Tension `tns`, Breathiness `bre`) and vibrato.
* 🔄 `openutau_convert_blueprint`: Convert an entire `song_blueprint.json` into a clean, ready-to-open OpenUtau `.ustx` project.
* 🎶 `openutau_synthesize_preview`: Acoustically synthesize a vocal preview WAV directly from notes with 25ms cosine-squared crossfading.

### MCP Configuration Example (`mcpSettings.json`):
```json
{
  "mcpServers": {
    "openutau-mcp": {
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

### Self-Test OpenUtau MCP Server
```bash
python mcp_server/test_openutau_mcp.py
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
│   ├── openutau_ustx_builder.py   # Modern OpenUtau .ustx YAML project builder
│   ├── utau_vocal_engine.py       # Acoustic synthesis & DSP engine
│   ├── harmony_matrix.py          # SoundQuest harmonic sequencer & MIDI builder
│   ├── reaper_project_builder.py  # Dual-layer REAPER .rpp project generator
│   └── mastering_dsp.py           # Tape glue & True-Peak limiter (-0.3 dBFS)
├── mcp_server/
│   ├── __init__.py
│   ├── server.py                  # Standard Stdio JSON-RPC 2.0 OpenUtau MCP Server
│   ├── openutau_tools.py          # Modern OpenUtau .ustx & DiffSinger tuning tools
│   └── test_openutau_mcp.py       # Stdio RPC integration test suite
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
