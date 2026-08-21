#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenVocal-DAW: Interactive Environment Setup & Configuration Wizard
Guides the user step-by-step to configure local paths for REAPER, UTAU Resampler,
Voicebanks, and VST plugins, saving everything to openvocal_config.json.
"""

import os
import sys
import json
import argparse

# Ensure UTF-8 stdout
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.env_detector import EnvDetector


def prompt_path(prompt_text, default_val=None, is_dir=False, must_exist=False):
    default_str = f" [默认: {default_val}]" if default_val else ""
    while True:
        try:
            val = input(f"{prompt_text}{default_str}
👉 请输入 (按回车使用默认): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("
[!] 取消输入，使用默认值。")
            return default_val
        
        # Strip outer quotes if user dragged and dropped path from Windows Explorer
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1].strip()
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1].strip()

        if not val:
            val = default_val

        if not val:
            if must_exist:
                print("❌ 该项不能为空，请输入有效路径！")
                continue
            return None

        if os.path.exists(val):
            return os.path.abspath(val)
        else:
            if must_exist:
                print(f"❌ 路径不存在: '{val}'，请重新输入！")
            else:
                confirm = input(f"⚠️ 警告: 路径 '{val}' 当前不存在。是否仍要保存？(y/n) [y]: ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return val


def run_interactive_wizard(auto_mode=False):
    print("=" * 70)
    print("      🎵 OpenVocal-DAW 制作环境初始化配置向导 (Setup Wizard)")
    print("=" * 70)
    print("欢迎使用 OpenVocal-DAW！本向导将帮助你绑定本地的 REAPER、UTAU 声库与插件。")
    print("提示：在 Windows 下你可以直接从资源管理器【拖拽文件夹或文件】到终端中！
")

    # 1. First run auto-discovery to get intelligent defaults
    detected = EnvDetector.auto_discover(PROJECT_ROOT)
    existing_cfg = EnvDetector.load_config(PROJECT_ROOT) or {}

    def_reaper = existing_cfg.get("reaper_exe") or detected.get("reaper_exe")
    def_resampler = existing_cfg.get("resampler_exe") or detected.get("resampler_exe")
    def_vb = existing_cfg.get("voicebank_dir") or detected.get("voicebank_dir")
    def_vsts = existing_cfg.get("vst_directories") or detected.get("vst_directories", [])

    if auto_mode:
        print("⚡ 正在执行全自动配置探测 (--auto)...")
        cfg = {
            "reaper_exe": def_reaper,
            "resampler_exe": def_resampler,
            "voicebank_dir": def_vb,
            "available_voicebanks": detected.get("available_voicebanks", {}),
            "vst_directories": def_vsts
        }
    else:
        # Step 1: REAPER Executable Path
        print("
" + "-" * 70)
        print("【步骤 1/4】配置 REAPER 宿主软件路径")
        print("说明：用于关联 REAPER 宿主。如果未安装可直接回车跳过。")
        reaper_path = prompt_path(
            "请输入 reaper.exe 的完整文件路径",
            default_val=def_reaper,
            is_dir=False
        )

        # Step 2: UTAU Resampler Engine Path
        print("
" + "-" * 70)
        print("【步骤 2/4】配置 UTAU 重采样引擎路径 (moresampler.exe / resampler.exe)")
        print("说明：用于人声切片重采样。若无将自动切换为 Python 纯数学物理合成。")
        resampler_path = prompt_path(
            "请输入 moresampler.exe 或 resampler.exe 的完整路径",
            default_val=def_resampler,
            is_dir=False
        )

        # Step 3: Default Voicebank Directory Path
        print("
" + "-" * 70)
        print("【步骤 3/4】配置默认虚拟歌手声库文件夹 (Voicebank Directory)")
        print("说明：包含 .wav 和 oto.ini 的声库文件夹（如重音 Teto、初音未来或你自己的声库）。")
        vb_path = prompt_path(
            "请输入声库文件夹路径",
            default_val=def_vb,
            is_dir=True
        )

        # Step 4: VST Plugin Directory Path
        print("
" + "-" * 70)
        print("【步骤 4/4】配置常用 VST 乐器与效果器插件目录")
        print("说明：你的 VST3/VST2 乐器插件存放路径（如 MT-PowerDrumKit、Ample Bass 等）。")
        def_vst_str = ";".join(def_vsts) if def_vsts else None
        vst_input = prompt_path(
            "请输入 VST 插件文件夹路径 (多个路径可用分号 ';' 分隔)",
            default_val=def_vst_str,
            is_dir=True
        )
        if vst_input:
            vst_dirs = [p.strip() for p in vst_input.split(";") if p.strip()]
        else:
            vst_dirs = []

        cfg = {
            "reaper_exe": reaper_path,
            "resampler_exe": resampler_path,
            "voicebank_dir": vb_path,
            "available_voicebanks": detected.get("available_voicebanks", {}),
            "vst_directories": vst_dirs
        }

        # Add custom vb if valid
        if vb_path and os.path.exists(vb_path):
            vb_name = os.path.basename(vb_path)
            cfg["available_voicebanks"][vb_name] = vb_path

    # Save to openvocal_config.json
    saved_file = EnvDetector.save_config(cfg, PROJECT_ROOT)

    print("
" + "=" * 70)
    print("🎉 配置完成！当前环境配置清单已保存：")
    print(f"📄 配置文件: {saved_file}")
    print(f"  • REAPER 路径      : {cfg['reaper_exe'] or '未配置 (纯代码模式)'}")
    print(f"  • 重采样引擎路径   : {cfg['resampler_exe'] or '未配置 (物理合成兜底)'}")
    print(f"  • 默认歌手声库路径 : {cfg['voicebank_dir'] or '未配置'}")
    print(f"  • VST 插件目录列表 : {cfg['vst_directories']}")
    print("=" * 70)
    print("
💡 下一步：现在你可以直接运行生成你的专属音乐了：")
    print("   python make_song.py examples/neon_pulse/song_blueprint.json")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="OpenVocal-DAW Environment Setup Wizard")
    parser.add_argument("--auto", action="store_true", help="Automatically detect and save default paths without interactive prompts")
    args = parser.parse_args()
    run_interactive_wizard(auto_mode=args.auto)


if __name__ == "__main__":
    main()
