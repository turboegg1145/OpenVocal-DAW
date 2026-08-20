# 🎙️ OpenVocal-DAW: Full-Stack AI Vocaloid & DAW Production Engine

<p align="center">
  <a href="#english"><img src="https://img.shields.io/badge/Language-English-blue.svg" alt="English"/></a>
  <a href="#chinese"><img src="https://img.shields.io/badge/语言-中文简体-red.svg" alt="中文"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"/></a>
  <a href="https://github.com/turboegg1145/OpenVocal-DAW"><img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Status"/></a>
</p>

---

## 🌟 Introduction / 项目简介

**Stop generating flat, black-box audio. Start generating professional DAW sessions.**

**OpenVocal-DAW** is an end-to-end, open-source technical music production pipeline designed for virtual singers (Kasane Teto, Vocaloid, UTAU, CeVIO) and DAW creators. 

Unlike black-box generative music tools that spit out un-editable, muddy stereo WAVs, **OpenVocal-DAW** builds real, multi-track, commercial-grade music productions from the ground up:
* 🎼 **Harmonic Matrix**: Circle-of-fifths modulation, modal interchange, and strict voice leading.
* 🎹 **6-Track SMF-1 MIDI**: Structured multi-track scores for Vocals, Keys, Guitars, Bass, Drums, and Synths.
* 🎤 **Micro-Timing Vocal Engine**: -45ms consonant compensation engine for UTAU / Moresampler to eliminate plosive dragging.
* 🎛️ **Vital VST3 Matrix**: Automated sound design (16-Voice SuperSaws, Spectral Plucks, Sidechained Reese Bass).
* 🎚️ **REAPER DAW Assembly**: Automatic generation of fully illuminated `.rpp` sessions with active FX chains and routings.
* 🎬 **PV Timeline & Storyboard**: Millisecond-accurate lyric timestamps (`lyrics_timeline.json`) and cinematic director scripts.

---

<a name="chinese"></a>
## 🇨🇳 中文说明与核心架构

传统黑盒 AI 音乐（如 Suno / Udio）最大的痛点是：**无法分轨、无法进宿主二次编辑、歌姬咬字含糊、和声不可控**。

**OpenVocal-DAW** 带来全新的工程级白盒全链路工作流：

```
                    [ 歌词 / 风格 / BPM / 调性输入 ]
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ 1. 五度圈和声矩阵 (Harmony) │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ 2. 6 轨 SMF-1 MIDI 谱面生成 │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
      ┌─────────────────────┐           ┌─────────────────────┐
      │ 3. 歌姬微时序干声合成  │           │ 4. Vital VST3 分轨合成│
      │ (-45ms 辅音补偿)    │           │ (SuperSaw/Pluck/Bass)│
      └──────────┬──────────┘           └──────────┬──────────┘
                 └────────────────┬────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ 5. 商业混音母带 (-0.30dBFS) │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
    ┌──────────────────────────┐     ┌──────────────────────────┐
    │ 6. REAPER 10 轨工程组装   │     │ 7. 毫秒级 PV 歌词与分镜   │
    │    (project.rpp 激活)    │     │    (lyrics_timeline.json) │
    └──────────────────────────┘     └──────────────────────────┘
```

### ✨ 核心技术优势：
1. **白盒可控 (100% DAW Ready)**：每一次生成均产出标准 MIDI、24-bit 无损分轨与 REAPER 工程，制作人可随时在 DAW 中替换音源插件或微调乐句；
2. **-45ms 辅音预发音微时序补偿**：攻克虚拟歌姬（UTAU/Vocaloid）塞音/擦音（k, t, s, p, b）拖拍失重问题，母音重心咬住节拍律动；
3. **现代波表合成器（Vital VST3）矩阵**：自动化编排波表齐奏、光谱扭曲 Pluck 与侧链 Reese Bass；
4. **PV 自动化全套资产就绪**：输出逐字毫秒级时码 JSON，直接对接卡拉OK字幕与粒子特效制作。

---

## ⚡ Quick Start / 快速上手

### 1. 安装依赖
```bash
git clone https://github.com/turboegg1145/OpenVocal-DAW.git
cd OpenVocal-DAW
pip install -r requirements.txt
```

### 2. 一键生成完整工程
```bash
# 生成现代赛博流行 (Modern Cyber Synth-Pop) 歌曲
python make_song.py --title "NEON_PULSE" --bpm 130 --genre cyber_pop

# 生成全速歌姬摇滚 (Speed J-Rock) 歌曲
python make_song.py --title "IGNITION" --bpm 185 --genre j_rock
```

### 3. 输出目录说明
生成的完整资产将自动存放于 `projects/<song_title>/`：
* `export/<song_title>_Master.wav` - 24-bit 终极商业母带（-0.30 dBFS True-Peak）
* `export/<song_title>_Inst.wav` - 纯伴奏无损母带
* `export/lyrics_timeline.json` - 毫秒级 PV 歌词时间戳
* `reaper/<song_title>.rpp` - REAPER 10 轨点亮工程
* `midi/` - 6 大标准 SMF-1 分轨 MIDI（Vocal, Keys, Bass, Drums, Guitar, Synth）
* `vocal/` - 重音 Teto 微时序纯净干声
* `stems/` - Vital 波表合成器与伴奏独立分轨

---

## 📁 Repository Structure / 仓库结构

```text
OpenVocal-DAW/
├── core/                          # 核心流水线模块
│   ├── harmony_matrix.py          # 和声与五度圈转调矩阵
│   ├── midi_generator.py          # 6 轨 SMF-1 MIDI 生成器
│   ├── utau_vocal_engine.py       # Moresampler / UTAU 微时序引擎
│   ├── vital_dsp_bridge.py        # Vital VST3 & 物理建模音频渲染
│   ├── mixing_mastering.py        # 动态人声雕刻与商业级母带
│   ├── reaper_project_builder.py  # REAPER .rpp 全点亮工程组装
│   └── pv_timeline_generator.py   # PV 歌词时间轴与导演分镜生成
├── examples/                      # 经典示范工程
│   └── neon_pulse_v2/             # 《NEON PULSE v2》完整资产范例
│       ├── lyrics_timeline.json   # 毫秒级歌词时间戳
│       ├── pv_narrative_script.md # 赛博朋克叙事 PV 分镜脚本
│       ├── song_blueprint.json    # 乐理和声与旋律总谱
│       └── project_neon_pulse.rpp # REAPER 工程文件
├── make_song.py                   # CLI 一键生成入口
├── requirements.txt               # Python 依赖
└── LICENSE                        # MIT License
```

---

## 🤝 Contributing & License

欢迎提出 Issue 与 Pull Request！  
本项目采用 **MIT License** 开源许可证，可自由用于个人学习、二创与商业音乐制作。

<p align="center">Made with ❤️ for Kasane Teto, Vocaloid Producers & Digital Music Creators Worldwide.</p>
