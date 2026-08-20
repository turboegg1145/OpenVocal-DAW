# OpenVocal-DAW 🎵

> **Autonomous AI Vocal & Multi-Track DAW Production Engine**  
> 一套打通 **【AI 智能体 ➔ 现代虚拟歌手（OpenUtau） ➔ 专业编曲宿主（REAPER DAW）】** 的全自动端到端工业级音乐生产线。

---

## 🌟 核心亮点与特性

1. 🎛️ **双层 REAPER 宿主工程自动化（Dual-Layer Architecture）**：
   - 自动生成 `.rpp` 宿主工程，内嵌 24-bit 无损分轨音频（Stems），**双击打开按空格键直接响**。
   - 每条乐器轨道下方并行内嵌标准 **MIDI 卷帘**（钢琴、贝斯、鼓点、合成器），支持随时挂载自己的顶级 VSTi 乐器插件。

2. 🎤 **原生虚拟歌手真实人声直出（One-Step Vocal Synthesis）**：
   - 内置多线程重采样切片引擎，自动探测本地 UTAU 声库（如重音 Teto），一键直出带真人发音咬字的干声与成品母带！
   - 同步输出 OpenUtau v0.6+ YAML 工程格式（`.ustx`），方便进阶用户在 OpenUtau 软件中二次精细调教。

3. 📁 **工业级结构化工程目录（Structured Export）**：
   - 每首歌拥有专属独立文件夹，内部采用便携式相对路径，无论拷贝到哪台电脑或 Mac，REAPER 均可 100% 免弹窗秒开。

4. 🎼 **SoundQuest 现代和声矩阵与时钟锁定**：
   - 严格遵循 1920 ticks/bar 时钟对齐（$480\text{ PPQ} \times 4$），彻底杜绝 MIDI 音符错位。
   - 遵循功能和声学与避音规则，自动生成真实伴奏织体。

5. 🎚️ **母带级 DSP 渲染链**：
   - 模拟磁带胶水饱和度建模（`tanh` 软削波算法）+ True-Peak $-0.3\text{ dBFS}$ 真实峰值砖墙限制器。

6. 💡 **零外部软件强依赖（Zero-Dependency Core）**：
   - 纯 Python 物理声学兜底计算，**即使全新电脑完全没装 REAPER/UTAU，也能 100% 成功生成可听可用的成品音乐与工程**。

---

## 🚀 极速上手：一键生成完整歌曲

### 1. 安装依赖（只需一次）
```bash
pip install -r requirements.txt
```

### 2. 一键运行生成
```bash
python make_song.py examples/neon_pulse/song_blueprint.json
```

### 3. 生成的专业工程目录结构
运行完成后，`export/` 目录下会自动生成以歌曲命名的专属文件夹：
```
export/NEON PULSE v2 (霓虹脉冲 v2) - Definitive Master/
│
├── 🎵 NEON PULSE v2_Master.wav         ➔ 【直接播放】母带级成品音频（带真人声与完整混音）
├── 🎛️ NEON PULSE v2.rpp                ➔ 【双击秒开】REAPER 5 轨双层宿主工程
├── 🎤 NEON PULSE v2.ustx               ➔ 【双击秒开】OpenUtau 歌姬工程
│
├── 🎧 stems/                           ➔ 【24-bit 无损分轨音频库】
│   ├── 01_Lead_Vocal.wav               (主唱人声干声)
│   ├── 02_Grand_Piano.wav              (钢琴伴奏波形)
│   ├── 03_Bass.wav                     (贝斯律动波形)
│   ├── 04_Drums.wav                    (完整鼓组波形)
│   └── 05_Synth_Lead.wav               (合成器琶音波形)
│
└── 🎹 midi/                            ➔ 【标准 MIDI 序列库】
    ├── 01_Lead_Vocal.mid               (人声主旋律 MIDI)
    ├── 02_Grand_Piano.mid              (4声部和弦织体 MIDI)
    ├── 03_Bass.mid                     (低频根音与律动 MIDI)
    ├── 04_Drums.mid                    (标准 GM 打击乐 MIDI)
    └── 05_Synth_Lead.mid               (合成器副旋律 MIDI)
```

---

## 🎹 核心教程一：如何换用你自己的 REAPER 乐器音色？

导出的 REAPER 伴奏轨（钢琴、贝斯、鼓组、合成器）**完全支持替换为你自己的顶级第三方 VSTi 乐器插件**（如 Addictive Keys、Ample Bass、Kontakt、Serum、Vital、MT-PowerDrumKit 等）。

### 方式 A：在 REAPER 界面中一键挂载（即插即用）
1. 双击打开导出的 `<歌曲名>.rpp`；
2. 点击要换音色的轨道（例如 `02_Grand_Piano`）上的 **`FX`** 按钮；
3. 选择你电脑里安装的乐器插件（例如 `Addictive Keys`）；
4. 将该轨道自带的音频块静音（选中音频块按 `Alt + M`）或直接删除；
5. **底下的 MIDI 卷帘就会立刻驱动你的顶级乐器插件发出华丽真实的音色！**

### 方式 B：在蓝图中全自动注入插件
在 `song_blueprint.json` 中配置乐器对应的 VST 名称：
```json
{
  "title": "My Song",
  "instruments": {
    "piano": { "vst": "Addictive Keys" },
    "bass":  { "vst": "ABPL.vst3" },
    "drums": { "vst": "MT-PowerDrumKit" },
    "synth": { "vst": "Serum" }
  }
}
```

---

## 🎤 核心教程二：如何使用自定义歌手 / 你自己的音色？

### 1. 使用你自己的 UTAU 录音声库（一键直出真人声音）
如果你有自己录制制作的声库（或任意包含 `.wav` 和 `oto.ini` 的声库文件夹）：
* **命令行传参法**：
  ```bash
  python make_song.py blueprint.json export/ "D:/MyVoicebanks/我的自定义声库"
  ```
* **蓝图配置法**：
  在 `song_blueprint.json` 中指定路径：
  ```json
  {
    "title": "My Song",
    "singer": "我的声库名",
    "voicebank_dir": "D:/MyVoicebanks/我的自定义声库"
  }
  ```

### 2. 使用你训练的 DiffSinger AI 神经网络模型
在 `song_blueprint.json` 中指定模型与音素化器：
```json
{
  "title": "My Song",
  "singer": "My_DiffSinger_Model",
  "phoneticizer": "OpenUtau.Core.DiffSinger.DiffSingerPhoneticizer"
}
```
运行后双击打开生成的 `.ustx`，OpenUtau 会自动调用你的深度学习模型进行极致逼真的拟人歌唱。

---

## 📝 进阶：如何写一首自己的歌（蓝图说明）

只需新建一个 `my_song.json`：
```json
{
  "title": "星空之城",
  "bpm": 128.0,
  "total_bars": 16,
  "chords": {
    "0-7": ["Gmaj7", "A7", "F#m7", "Bm7", "Gmaj7", "A7", "F#m7", "F#7"],
    "8-15": ["Bm", "Gmaj7", "A", "F#m7", "Bm", "Gmaj7", "A", "F#7"]
  },
  "vocal_score": {
    "0": [
      ["よ", 240, 62, 100],
      ["る", 240, 66, 105],
      ["の", 240, 71, 108],
      ["ま", 240, 74, 112],
      ["ち", 480, 71, 108],
      ["ひ", 240, 66, 102],
      ["か", 240, 62, 100]
    ],
    "1": [
      ["る", 480, 67, 105],
      ["R", 480, 60, 0]
    ]
  }
}
```
* **`chords`**：指定每个小节的和弦进行（和声矩阵会自动推导钢琴、贝斯、合成器和声）。
* **`vocal_score`**：按小节排布歌词与旋律，单音格式为 `[歌词假名, ticks时长, MIDI音高, 力度]`（480 ticks = 1 拍四分音符，中央 C = 60）。

---

## ❓ 常见疑问解答 (FAQ)

#### Q1：在全新电脑上运行会发生什么？
> **答：100% 成功生成，绝不报错！**  
> 伴奏（钢琴、贝斯、鼓组、合成器）完整无缺，人声会自动触发声学物理合成算法（准确的旋律与音准），同时工程文件（`.rpp` / `.ustx`）完好生成，随时可带到任何环境继续制作。

#### Q2：为什么 REAPER 打开不会报错丢失文件？
> **答：便携式相对路径。**  
> 所有轨道引用的音频与 MIDI 均使用 `stems/` 和 `midi/` 相对路径，即使将整个歌曲文件夹复制到他人电脑或 Mac 上，REAPER 也能直接找到全部文件。

---

## 📂 项目架构

```
OpenVocal-DAW/
├── core/
│   ├── openutau_ustx_builder.py    # OpenUtau .ustx YAML 工程生成器
│   ├── harmony_matrix.py           # SoundQuest 和声矩阵与 5 轨 MIDI/音频生成器
│   ├── reaper_project_builder.py   # 双层 REAPER .rpp 宿主工程生成器
│   ├── utau_vocal_engine.py        # 多线程真实声库切片重采样与物理合成引擎
│   └── mastering_dsp.py            # 磁带胶水饱和度与 -0.3 dBFS 真实峰值限制器
├── examples/
│   └── neon_pulse/                 # 示例歌曲完整蓝图与工程
│       ├── song_blueprint.json
│       ├── project_neon_pulse.rpp
│       └── project_neon_pulse.ustx
├── make_song.py                    # 一键全自动歌曲生成命令行入口
├── requirements.txt
├── LICENSE                         # MIT 开源协议
└── README.md
```

---

## 📄 License
Released under the **MIT License**.
