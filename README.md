# OpenVocal-DAW 🎵

> **Autonomous AI Vocal & Multi-Track DAW Production Engine**  
> 一套打通 **【AI 智能体 ➔ 现代 OpenUtau 歌姬调教 ➔ 专业 REAPER 编曲混音宿主】** 的全自动端到端工业级音乐生产线。

---

## 🌟 核心架构与设计哲学

1. ⚙️ **用户自主输入驱动的环境配置（`init_env.py` Setup Wizard）**：
   - 以用户输入为核心，在终端分步绑定你的本地 **OpenUtau 主程序路径**、**OpenUtau 歌手声库目录（Singers）**、**REAPER 宿主路径** 与 **VST 插件目录**。
   - 支持直接从文件资源管理器【拖拽文件/文件夹】进终端输入；
   - 彻底告别所有死板的硬编码绝对路径，全量配置保存在本地 `openvocal_config.json` 中。

2. 🎤 **100% 现代 OpenUtau 深度生态集成**：
   - 自动读取 OpenUtau 官方 Singers 声库与首选项，原生输出现代化 `.ustx`（YAML 架构）工程文件；
   - 智能派发多语言音素化器（`JapaneseCVPhoneticizer`、`ChinesePinyinPhoneticizer`、`ArpasingPhoneticizer` 等），保留完整的表情控制与音高曲线；
   - 支持并发声学切片直出 24-bit 无损人声干声，打通全自动出歌。

3. 🎛️ **声明式双层 REAPER 宿主工程（Declarative 10-Track DAW Architecture）**：
   - 自动生成满血 `.rpp` 宿主工程，内嵌 24-bit 无损分轨音频（Stems）与多轨 VST 插件链（`MT-PowerDrumKit`、`Ample Bass`、`NeoPiano`、`Ample Guitar`、`ValhallaSupermassive` 空间混响总线）。
   - 每条乐器轨道下方并行内嵌标准 **MIDI 卷帘**，随时可二次精修或更换音源。

4. 🎚️ **自适应多相滤波 DSP 重采样（Adaptive Resampler）**：
   - 内置高阶多相滤波重采样算法，若接入 48kHz 或 96kHz 等非标采样率声库，自动平滑无损对齐至广播级 44.1kHz，保证音高与时间 100% 同步不跑调。

5. 📁 **工业级结构化工程目录（Structured Export）**：
   - 每首歌专属独立文件夹，内部采用便携式相对路径，无论拷贝到哪台电脑或 Mac，REAPER 均可 100% 免弹窗秒开。

---

## 🚀 极速上手：三步开启音乐制作

### 第一步：安装 Python 依赖（只需一次）
```bash
pip install -r requirements.txt
```

### 第二步：运行环境初始化向导（输入你的本地路径）
```bash
python init_env.py
```
👉 **交互式输入**：按终端提示输入或直接从资源管理器【拖拽】你的 `OpenUtau.exe` 路径、`Singers` 声库文件夹、`reaper.exe` 路径或 VST 插件目录（未安装的项目可直接回车跳过）。  
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

## 🎤 核心教程二：如何使用自定义 OpenUtau 歌手 / 你自己的音色？

### 1. 使用你存放在 OpenUtau 里的任意声库
运行 `python init_env.py` 指定你的 OpenUtau `Singers` 文件夹，或在蓝图中指定声库名：
```json
{
  "title": "My Song",
  "singer": "你的声库文件夹名 (如 guzhengxing / teto_tandoku)"
}
```

### 2. 使用 DiffSinger AI 神经网络模型
在 `song_blueprint.json` 中指定 DiffSinger 模型名与音素化器：
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
│   ├── env_detector.py             # 用户环境配置管理器 (openvocal_config.json)
│   ├── openutau_ustx_builder.py    # OpenUtau .ustx YAML 工程生成器
│   ├── harmony_matrix.py           # 现代和声矩阵与多轨音符/音频合成器
│   ├── reaper_project_builder.py   # 声明式 REAPER .rpp 10 轨宿主工程生成器
│   ├── utau_vocal_engine.py        # OpenUtau 多线程真实声库切片重采样引擎
│   └── mastering_dsp.py            # 自适应多相重采样与 -0.3 dBFS 限制器
├── examples/
│   └── neon_pulse/                 # 1:1 完整示例歌曲蓝图与工程
│       └── song_blueprint.json
├── init_env.py                     # 交互式用户输入配置向导 (User Setup Wizard)
├── make_song.py                    # 一键全自动歌曲生成主程序
├── requirements.txt
├── LICENSE                         # MIT 开源协议
└── README.md
```

---

## 📄 License
Released under the **MIT License**.
