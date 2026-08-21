#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenVocal-DAW: Interactive Environment Setup Wizard (User-Input Driven)
Guides the user step-by-step to specify and bind their exact local paths for
OpenUtau, Singer Voicebanks, REAPER, and VST plugins.
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


def prompt_user_input(step_num, title, description, hint_val=None, must_exist=False):
    print("\n" + "=" * 70)
    print(f"【步骤 {step_num}/4】{title}")
    print(f"说明: {description}")
    default_str = f" [推荐建议: {hint_val}]" if hint_val else " [无默认值，按回车可跳过]"
    
    while True:
        try:
            print(f"提示: 支持直接从 Windows 资源管理器【拖拽文件或文件夹】到此终端窗口中！{default_str}")
            val = input("👉 请输入你的本地完整路径: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[!] 取消输入，保留推荐值。")
            return hint_val

        # Strip outer quotes if dragged and dropped
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1].strip()
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1].strip()

        if not val:
            val = hint_val

        if not val:
            if must_exist:
                print("❌ 该项为必须项，请输入有效路径！")
                continue
            return None

        if os.path.exists(val):
            abs_p = os.path.abspath(val)
            print(f"✓ 已确认有效路径: {abs_p}")
            return abs_p
        else:
            if must_exist:
                print(f"❌ 路径不存在: '{val}'，请重新输入！")
            else:
                confirm = input(f"⚠️ 警告: 路径 '{val}' 当前在磁盘上不存在，是否仍要保存？(y/n) [y]: ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return val


def run_setup_wizard(auto_mode=False):
    print("*" * 70)
    print("      🎵 OpenVocal-DAW 音乐制作环境配置向导 (User Setup Wizard)")
    print("*" * 70)
    print("欢迎使用 OpenVocal-DAW！请根据你的本地电脑实际安装情况输入以下路径。")
    print("所有配置将保存至本地 openvocal_config.json，完全由你自主决定！\n")

    hints = EnvDetector.get_default_hints(PROJECT_ROOT)
    existing = EnvDetector.load_config(PROJECT_ROOT) or {}

    h_openutau = existing.get("openutau_exe") or hints.get("openutau_exe")
    h_singers = existing.get("openutau_singers_dir") or hints.get("openutau_singers_dir")
    h_reaper = existing.get("reaper_exe") or hints.get("reaper_exe")
    h_vsts = existing.get("vst_directories") or hints.get("vst_directories", [])

    if auto_mode:
        print("⚡ 正在执行全自动探测模式 (--auto)...")
        cfg = {
            "openutau_exe": h_openutau,
            "openutau_singers_dir": h_singers,
            "reaper_exe": h_reaper,
            "vst_directories": h_vsts
        }
    else:
        # Step 1: OpenUtau Executable
        openutau_path = prompt_user_input(
            1,
            "配置 OpenUtau 主程序路径 (OpenUtau.exe)",
            "你的现代歌姬调教宿主 OpenUtau 主程序位置 (如 E:\\utau\\OpenUtau\\OpenUtau.exe)。",
            hint_val=h_openutau
        )

        # Step 2: OpenUtau Singers Directory
        singers_path = prompt_user_input(
            2,
            "配置 OpenUtau 歌手声库文件夹 (Singers 目录)",
            "包含你所有歌姬声库的文件夹 (如 C:\\Users\\用户名\\Documents\\OpenUtau\\Singers)。",
            hint_val=h_singers
        )

        # Step 3: REAPER DAW Executable
        reaper_path = prompt_user_input(
            3,
            "配置 REAPER 编曲宿主路径 (reaper.exe)",
            "用于编曲混音的 REAPER 主程序位置 (如 C:\\Program Files\\REAPER (x64)\\reaper.exe，未安装可回车跳过)。",
            hint_val=h_reaper
        )

        # Step 4: VST Plugin Directory
        vst_hint_str = ";".join(h_vsts) if h_vsts else None
        vst_raw = prompt_user_input(
            4,
            "配置 VST 插件文件夹路径 (VSTPlugins / VST3)",
            "你的常用 VST 乐器/效果器目录 (如 MT-PowerDrumKit、Ample Bass 等，多个目录用分号 ';' 分隔)。",
            hint_val=vst_hint_str
        )
        vst_dirs = [p.strip() for p in vst_raw.split(";") if p.strip()] if vst_raw else []

        cfg = {
            "openutau_exe": openutau_path,
            "openutau_singers_dir": singers_path,
            "reaper_exe": reaper_path,
            "vst_directories": vst_dirs
        }

    saved_p = EnvDetector.save_config(cfg, PROJECT_ROOT)

    print("\n" + "=" * 70)
    print("🎉 配置保存成功！你的本地制作环境清单：")
    print(f"📄 配置文件: {saved_p}")
    print(f"  • OpenUtau 宿主路径 : {cfg['openutau_exe'] or '未指定 (纯代码生成模式)'}")
    print(f"  • 歌手声库总目录   : {cfg['openutau_singers_dir'] or '未指定'}")
    print(f"  • REAPER 宿主路径   : {cfg['reaper_exe'] or '未指定'}")
    print(f"  • VST 插件目录列表 : {cfg['vst_directories']}")
    print("=" * 70)
    print("\n🚀 现在你可以直接一键生成完整歌曲资产了：")
    print("   python make_song.py examples/neon_pulse/song_blueprint.json")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="OpenVocal-DAW Environment Setup Wizard")
    parser.add_argument("--auto", action="store_true", help="Use detected default paths without interactive prompts")
    args = parser.parse_args()
    run_setup_wizard(auto_mode=args.auto)


if __name__ == "__main__":
    main()
