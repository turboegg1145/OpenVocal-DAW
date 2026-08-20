# OpenVocal-DAW 🎵

> **Autonomous AI Vocal & Multi-Track DAW Production Engine**  
> 一套打通 **【AI 智能体 ➔ 现代虚拟歌手（OpenUtau） ➔ 专业编曲宿主（REAPER DAW）】** 的全自动端到端工业级音乐生产线。

---

## 🌟 核心亮点与特性

1. 🎛️ **双层 REAPER 宿主工程自动化（Dual-Layer Architecture）**：
   - 自动生成 `.rpp` 宿主工程，内嵌 24-bit 无损分轨音频（Stems），**双击打开按空格键直接响**。
   - 每条乐器轨道下方并行内嵌标准 **MIDI 卷帘**（钢琴、贝斯、鼓点、吉他、合成器），支持随时二次精修或更换音源插件。

2. 🎤 **OpenUtau 原生多轨工程生成（.ustx）**：
   - 原生支持 OpenUtau v0.6+ 标准 YAML 工程格式，自动排布歌词假名、音高曲线、颤音与音素化器绑定。
   - 无论是否预装目标声库均可安全加载，支持在 OpenUtau 中一键切换任意 UTAU 或 DiffSinger 音源。

3. 🎼 **SoundQuest 现代和声矩阵与时钟锁定**：
   - 严格遵循 1920 ticks/bar 时钟对齐（$480\text{ PPQ} \times 4$），彻底杜绝 MIDI 音符错位。
   - 遵循功能和声学与避音规则，支持主属副属、同主音借用（Modal Interchange）等高级曲式。

4. 🎚️ **母带级 DSP 渲染链**：
   - 模拟磁带胶水饱和度建模（`tanh` 软削波算法）。
   - True-Peak 真实峰值砖墙限制器，死锁在 $-0.3\text{ dBFS}$，自动优化动态响度。

5. 💡 **零外部软件强依赖（Zero-Dependency Core）**：
   - 生成 `.rpp`、`.ustx` 与 24-bit 试听音频完全基于纯 Python 数学计算，**即使电脑上完全没有安装 REAPER 或 UTAU 也绝不会报错**。

---

## 🚀 小白极速上手教程

### 第一步：环境配置（只需运行一次）
在终端（PowerShell 或 CMD）中运行：
```bash
pip install -r requirements.txt
```
*(依赖库：`pyyaml`, `numpy`, `soundfile`, `mido`, `scipy`)*

---

### 第二步：一键生成全套音乐资产
运行主程序并传入蓝图文件：
```bash
python make_song.py examples/neon_pulse/song_blueprint.json
```

**运行完成后，你会在 `export/` 文件夹中收获 4 样交付物**：
* 🎼 **`project.ustx`**：**OpenUtau 虚拟歌手工程**（双击在 OpenUtau 软件中打开精修）；
* 🎛️ **`project.rpp`**：**REAPER 编曲宿主工程**（双击在 REAPER 中打开播放与混音）；
* 🎤 **`vocal_dry.wav`**：**24-bit 无损人声干声**；
* 🎵 **`master.wav`**：**母带级完整歌曲音频**（直接双击用系统播放器听或发给朋友）。

---

## 📝 进阶：如何定制你自己的歌？

只需用记事本打开 `song_blueprint.json`，修改参数即可：

```json
{
  "title": "My_First_Song",
  "bpm": 128.0,
  "total_bars": 32,
  "vocal_score": {
    "0": [
      ["こ", 480, 68, 100],
      ["ん", 480, 71, 100],
      ["に", 480, 73, 100],
      ["ち", 480, 75, 100]
    ]
  }
}
```
* **`title`**：歌曲名称
* **`bpm`**：歌曲速度
* **`vocal_score`**：歌词与旋律格式为 `[歌词假名, 持续时长ticks, 音高MIDI号, 力度]`（例如 60 是中央 C，68 是 G#4）。

保存后重新运行 `python make_song.py your_blueprint.json`，你的专属新歌即刻生成！

---

## ❓ 常见疑问解答 (FAQ)

#### Q1：如果我电脑里没装 REAPER 或 OpenUtau，运行会报错吗？
> **答：绝对不会！**  
> 整个生成引擎是纯代码编写的，不需要启动宿主软件。导出的 `.wav` 音频在任何电脑/手机上都能直接听，工程文件（`.rpp` / `.ustx`）则会完好保存在本地，随时备用。

#### Q2：它怎么知道我用什么歌姬？如果我没装这个歌姬怎么办？
> **答：乐谱与声库完全解耦。**  
> `.ustx` 本质是一张通用的工程乐谱。如果在 OpenUtau 里打开未安装的歌姬，界面不会报错，所有音符和假名依然整齐排布，只需在 OpenUtau 下拉菜单中换成你本地现有的任意歌姬，音符就会立刻自动套用并演唱。

---

## 📂 项目结构全景

```
OpenVocal-DAW/
├── core/
│   ├── openutau_ustx_builder.py    # 现代 OpenUtau .ustx YAML 工程生成器
│   ├── harmony_matrix.py           # SoundQuest 和声矩阵 (1920 ticks/bar 时钟锁定)
│   ├── reaper_project_builder.py   # 双层 REAPER .rpp 宿主工程生成器
│   ├── utau_vocal_engine.py        # 人声声学物理合成与共振峰渲染器
│   └── mastering_dsp.py            # 磁带胶水饱和度与 -0.3 dBFS 限制器
├── examples/
│   └── neon_pulse/                 # 示例歌曲蓝图、REAPER 与 OpenUtau 工程
│       ├── song_blueprint.json
│       ├── project_neon_pulse.rpp
│       └── project_neon_pulse.ustx
├── make_song.py                    # 全自动端到端歌曲生产主程序
├── requirements.txt
├── LICENSE                         # MIT 开源协议
└── README.md
```

---

## 🔗 相关生态生态扩展
* 🤖 **[OpenUtau-MCP](https://github.com/turboegg1145/OpenUtau-MCP)**：专为 Claude Desktop / Cursor / Antigravity 打造的 OpenUtau 智能体调教插件。

---

## 📄 License
MIT License (c) 2026 turboegg1145
