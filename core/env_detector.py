"""
OpenVocal-DAW: Environment & OpenUtau Profile Manager
Manages user-specified paths for OpenUtau, Singers, REAPER, and VST plugins.
"""

import os
import sys
import json
import winreg

CONFIG_FILENAME = "openvocal_config.json"


class EnvDetector:
    @staticmethod
    def get_config_path(project_root=None):
        if not project_root:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(project_root, CONFIG_FILENAME)

    @staticmethod
    def load_config(project_root=None):
        cfg_path = EnvDetector.get_config_path(project_root)
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return EnvDetector.get_default_hints(project_root)

    @staticmethod
    def load_or_detect_all(project_root=None):
        return EnvDetector.load_config(project_root)

    @staticmethod
    def save_config(config_dict, project_root=None):
        cfg_path = EnvDetector.get_config_path(project_root)
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        return cfg_path

    @staticmethod
    def get_default_hints(project_root=None):
        # Scan user standard locations
        hints = {
            "openutau_exe": "",
            "openutau_singers_dir": "",
            "reaper_exe": "",
            "vst_directories": [
                "C:\\Program Files\\Common Files\\VST3",
                "C:\\Program Files\\Steinberg\\VstPlugins"
            ]
        }
        for exe_cand in [r"E:\utau\OpenUtau\OpenUtau.exe", r"C:\Users\43316\Documents\OpenUtau\OpenUtau.exe"]:
            if os.path.exists(exe_cand):
                hints["openutau_exe"] = exe_cand
                break
        singers_cand = r"C:\Users\43316\Documents\OpenUtau\Singers"
        if os.path.exists(singers_cand):
            hints["openutau_singers_dir"] = singers_cand

        for reaper_cand in [r"E:\REAPER\reaper.exe", r"C:\Program Files\REAPER (x64)\reaper.exe"]:
            if os.path.exists(reaper_cand):
                hints["reaper_exe"] = reaper_cand
                break
        return hints


EnvironmentDetector = EnvDetector
