# OpenVocal-DAW 🎵

> **Autonomous AI Vocal & Multi-Track DAW Production Engine**  
> An open-source, end-to-end framework integrating **SoundQuest harmonic sequencing**, **OpenUtau (.ustx) multi-track generation**, **UTAU acoustic physics synthesis**, and **automated REAPER DAW project assembly**.

---

## 🌟 Core Highlights

1. 🎼 **Dual-Layer REAPER DAW Session Automation**:
   - Automated `.rpp` session generation mounting 24-bit lossless audio stems for instant playback.
   - Parallel MIDI take items embedded under audio stems for immediate piano-roll editing.
   - Automated render configuration and VST plugin chain mounting (Piano One, Ample Bass, MT Power DrumKit, Vital, Valhalla Supermassive).

2. 🎤 **OpenUtau (.ustx) Native Integration**:
   - Native YAML-based **`.ustx` project generator** (compatible with OpenUtau v0.6+).
   - Multi-track vocal arrangement (Lead, Harmony, Backing) with Singer ID and Phoneticizer bindings (`DefaultPhoneticizer`, `JapaneseVCVPhoneticizer`, `DiffSingerPhoneticizer`).

3. 🎹 **SoundQuest Harmonic Matrix & Sequencer**:
   - Enforces 1920 ticks/bar clock lock ($480\text{ PPQ} \times 4$).
   - Multi-track standard MIDI generation for Grand Piano, Precision Bass, Acoustic/Electric Guitar, Drums, and Synths.
   - Harmonic avoidance check and functional chord progressions.

4. 🎚️ **Mastering DSP Suite**:
   - Analog tape glue saturation modeling (`tanh` soft-clipping).
   - True-Peak brickwall limiter locked to $-0.3\text{ dBFS}$ with dynamic LUFS loudness optimization.

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/turboegg1145/OpenVocal-DAW.git
cd OpenVocal-DAW
pip install -r requirements.txt
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
├── examples/
│   └── neon_pulse/                # Example Song Blueprint, REAPER & OpenUtau Sessions
│       ├── song_blueprint.json
│       ├── project_neon_pulse.rpp
│       └── project_neon_pulse.ustx
├── make_song.py                   # Master production CLI
├── requirements.txt
├── LICENSE                        # MIT License
└── README.md
```

---

## 📄 License
MIT License (c) 2026 turboegg1145
