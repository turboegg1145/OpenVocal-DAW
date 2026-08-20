# OpenVocal-DAW 🎵

> **Autonomous AI Vocal Synthesis & DAW Multi-Track Production Toolkit**  
> An open-source, end-to-end framework integrating **UTAU / OpenUtau acoustic vocal synthesis**, **SoundQuest harmonic sequencing**, and **automated REAPER DAW project assembly**.

---

## 🌟 Key Features

1. 🎤 **Precision UTAU Vocal Engine**:
   - Automated phonetic alias resolution (`oto.ini` parser with shift-jis/cp932/utf-8 support).
   - Pre-utterance timing shift alignment so vowel nuclei land strictly on beat grid.
   - Formant-optimized rendering (`Flags=g0` / `Flags=g-2`) with 25ms cosine-squared crossfading ($w_{in} + w_{out} = 1.0$).
   - Strict float 0.0 silence (-180 dBFS) rest gating (zero wavtool clicking/artifacts).

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
│   ├── utau_vocal_engine.py       # UTAU physics & acoustic synthesis engine
│   ├── harmony_matrix.py          # SoundQuest harmonic sequencer & MIDI builder
│   ├── reaper_project_builder.py  # Dual-layer REAPER .rpp project generator
│   └── mastering_dsp.py           # Tape glue & True-Peak limiter (-0.3 dBFS)
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
