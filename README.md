# OpenVocal-DAW 🎵

> **Autonomous AI Vocal & Multi-Track DAW Production Engine**  
> 一套打通 **【AI 智能体 ➔ 现代虚拟歌手（OpenUtau/UTAU） ➔ 专业编曲宿主（REAPER DAW）】** 的全自动端到端工业级音乐生产线。

---

## 🌟 核心亮点与特性

1. ⚙️ **跨平台环境初始化向导（`init_env.py` Setup Wizard）**：
   - 交互式配置你的本地 REAPER 路径、UTAU 重采样器（moresampler / resampler）、歌手声库与 VST 插件目录。
   - 
2. 🎛️ **声明式双层 REAPER 宿主工程（Declarative 10-Track DAW Architecture）**：
   - 自动生成满血 `.rpp` 宿主工程，内嵌 24-bit 无损分轨音频（Stems）与多轨 VST 插件链（`MT-PowerDrumKit`、`Ample Bass`、`NeoPiano`、`Ample Guitar`、`ValhallaSupermassive` 空间混响总线）。
   - 每条乐器轨道下方并行内嵌标准 **MIDI 卷帘**，随时可二次精修或更换音源。

3. 🎤 **原生虚拟歌手真实人声直出（One-Step Vocal Synthesis）**：
   - 内置多线程重采样切片引擎，自动加载配置的声库与 `oto.ini` 原音设定，一键秒级直出带真人发音咬字的干声与成品母带！
   - 同步输出 OpenUtau v0.6+ YAML 工程格式（`.ustx`）。

4. 📁 **工业级结构化工程目录（Structured Export）**：
   - 每首歌专属独立文件夹，内部采用便携式相对路径，无论拷贝到哪台电脑或 Mac，REAPER 均可 100% 免弹窗秒开。

5. 💡 **零外部软件强依赖（Zero-Dependency Core Fallback）**：
   - 纯 Python 物理声学算法兜底，**即使全新电脑完全没装 REAPER/UTAU，也能 100% 成功生成可听可用的成品音乐与工程**。

---

## 🚀 极速上手：三步开启音乐制作

### 第一步：安装 Python 依赖库（只需一次）
```bash
pip install -r requirements.txt
```

### 第二步：运行环境初始化向导（配置你的本地路径）
```bash
python init_env.py
```
👉 **交互式输入**：按终端提示输入或直接从资源管理器【拖拽】你的 `reaper.exe` 路径、`moresampler.exe` 引擎路径、声库文件夹或 VST 插件目录（如果未安装可直接回车跳过）。  
*(提示：你也可以使用 `python init_env.py --auto` 进行全自动智能探测绑定)*

---

### 第三步：一键生成完整歌曲全套资产
```bash
python make_song.py examples/neon_pulse/song_blueprint.json
```

---

## 📂 生成的专业工程目录结构

运行完成后，`export/` 目录下会自动生成以歌曲命名的专属文件夹：
```
export/NEON PULSE v2 (霓虹脉冲 v2) - Definitive Master/
│
├── 🎵 NEON PULSE v2_Master.wav         ➔ 【直接播放】母带级成品音频（带真人声与完整混音）
├── 🎛️ NEON PULSE v2.rpp                ➔ 【双击秒开】10 轨 REAPER 满血宿主工程（含 5 大 VST 插件）
├── 🎤 NEON PULSE v2.ustx               ➔ 【双击秒开】OpenUtau 歌姬调教工程
│
├── 🎧 stems/                           ➔ 【24-bit 无损分轨音频库】
│   ├── 01_Lead_Vocal.wav               (主唱人声干声)
│   ├── 02_SuperSaw_Pad.wav             (超锯齿和弦波形)
│   ├── 03_Cyber_Pluck.wav              (赛博琶音波形)
│   ├── 04_Reese_Bass.wav               (低频贝斯波形)
│   ├── 05_Cyber_Drums.wav              (赛博鼓组波形)
│   └── 06_Funk_Guitar.wav              (Funk 吉他扫弦波形)
│
└── 🎹 midi/                            ➔ 【标准 MIDI 序列库】
    ├── 01_Lead_Vocal.mid               (人声主旋律 MIDI)
    ├── 02_SuperSaw_Pad.mid             (超锯齿和弦 MIDI)
    ├── 03_Cyber_Pluck.mid              (赛博琶音 MIDI)
    ├── 04_Reese_Bass.mid               (低频贝斯 MIDI)
    ├── 05_Cyber_Drums.mid              (赛博鼓组 MIDI)
    └── 06_Funk_Guitar.mid              (Funk 吉他 MIDI)
```

---

## 🎹 核心教程一：如何换用你自己的 REAPER 乐器音色？

导出的 REAPER 伴奏轨完全支持替换为你自己的顶级第三方 VSTi 乐器插件：

### 方式 A：在 REAPER 界面中一键挂载（即插即用）
1. 双击打开导出的 `<歌曲名>.rpp`；
2. 点击要换音色的轨道上的 **`FX`** 按钮；
3. 选择你电脑里安装的乐器插件（例如 `Addictive Keys`、`Kontakt`、`Serum`）；
4. 将该轨道自带的音频块静音（按 `Alt + M`）或直接删除；
5. **底下的 MIDI 卷帘就会立刻驱动你的顶级乐器插件发出华丽真实的音色！**

### 方式 B：在蓝图中声明式定义你的乐器与插件链
在 `song_blueprint.json` 中配置 `daw_tracks` 节点即可实现全自动挂载。

---

## 🎤 核心教程二：如何使用自定义歌手 / 你自己的音色？

### 1. 使用你自己的 UTAU 录音声库（一键直出真人声音）
运行 `python init_env.py` 指定你的声库文件夹，或者在命令行/蓝图中直接传参：
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

---

## 📂 项目架构

```
OpenVocal-DAW/
├── core/
│   ├── env_detector.py             # 智能环境探测器与配置管理器
│   ├── openutau_ustx_builder.py    # OpenUtau .ustx YAML 工程生成器
│   ├── harmony_matrix.py           # 现代和声矩阵与多轨音符/音频合成器
│   ├── reaper_project_builder.py   # 声明式 REAPER .rpp 10 轨宿主工程生成器
│   ├── utau_vocal_engine.py        # 多线程真实声库切片重采样引擎
│   └── mastering_dsp.py            # 磁带胶水饱和度与 -0.3 dBFS 真实峰值限制器
├── examples/
│   └── neon_pulse/                 # 1:1 完整示例歌曲蓝图与工程
│       └── song_blueprint.json
├── init_env.py                     # 交互式环境配置向导 (Setup Wizard)
├── make_song.py                    # 一键全自动歌曲生成主程序
├── requirements.txt
├── LICENSE                         # MIT 开源协议
└── README.md
```

---

## 📄 License
Released under the **MIT License**.
