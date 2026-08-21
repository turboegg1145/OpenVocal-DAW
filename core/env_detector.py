"""
OpenVocal-DAW: Environment & OpenUtau Profile Manager
Manages user-specified paths for OpenUtau, Singers, REAPER, and VST plugins.
"""

import os
import sys
import json

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
    def save_config(config_dict, project_root=None):
        cfg_path = EnvDetector.get_config_path(project_root)
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        return cfg_path

    @staticmethod
    def get_default_hints(project_root=None):
        if not project_root:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        appdata = os.environ.get("APPDATA", "")
        localappdata = os.environ.get("LOCALAPPDATA", "")
        progfiles = os.environ.get("ProgramFiles", r"C:\Program Files")
        progfiles_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        userprofile = os.environ.get("USERPROFILE", "")

        hints = {
            "openutau_exe": None,
            "openutau_singers_dir": None,
            "reaper_exe": None,
            "vst_directories": [],
            "resampler_exe": None
        }

        # 1. OpenUtau hints
        for p in [r"E:\utau\OpenUtau\OpenUtau.exe", os.path.join(localappdata, "Programs", "OpenUtau", "OpenUtau.exe")]:
            if os.path.exists(p):
                hints["openutau_exe"] = p
                break

        # 2. OpenUtau Singers hints
        for p in [os.path.join(userprofile, "Documents", "OpenUtau", "Singers"), os.path.join(appdata, "OpenUtau", "Singers")]:
            if os.path.exists(p):
                hints["openutau_singers_dir"] = p
                break

        # 3. REAPER hints
        for p in [os.path.join(progfiles, "REAPER (x64)", "reaper.exe"), os.path.join(progfiles, "REAPER", "reaper.exe")]:
            if os.path.exists(p):
                hints["reaper_exe"] = p
                break

        # 4. VST hints
        for p in [os.path.join(progfiles, "Common Files", "VST3"), os.path.join(progfiles, "Steinberg", "VstPlugins")]:
            if os.path.exists(p):
                hints["vst_directories"].append(p)

        return hints
