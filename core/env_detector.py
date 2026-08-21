"""
OpenVocal-DAW: Environment Detector & Profile Manager
Discovers local REAPER, UTAU / OpenUtau singers, Resamplers, and VST plugins
without any hardcoded paths.
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
        # Auto-discover if config doesn't exist
        return EnvDetector.auto_discover(project_root)

    @staticmethod
    def save_config(config_dict, project_root=None):
        cfg_path = EnvDetector.get_config_path(project_root)
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        return cfg_path

    @staticmethod
    def auto_discover(project_root=None):
        if not project_root:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        appdata = os.environ.get("APPDATA", "")
        localappdata = os.environ.get("LOCALAPPDATA", "")
        progfiles = os.environ.get("ProgramFiles", r"C:\Program Files")
        progfiles_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        userprofile = os.environ.get("USERPROFILE", "")

        config = {
            "reaper_exe": None,
            "resampler_exe": None,
            "voicebank_dir": None,
            "available_voicebanks": {},
            "vst_directories": [],
            "openutau_singers_dir": None
        }

        # Parent directory search tree
        search_dirs = [
            project_root,
            os.path.abspath(os.path.join(project_root, "..")),
            os.path.abspath(os.path.join(project_root, "..", "..")),
        ]

        # 1. REAPER Detection
        reaper_candidates = [
            os.path.join(progfiles, "REAPER (x64)", "reaper.exe"),
            os.path.join(progfiles, "REAPER", "reaper.exe"),
            os.path.join(progfiles_x86, "REAPER", "reaper.exe"),
            os.path.join(localappdata, "Programs", "REAPER", "reaper.exe"),
            r"C:\REAPER\reaper.exe",
            r"D:\REAPER\reaper.exe"
        ]
        for p in reaper_candidates:
            if os.path.exists(p):
                config["reaper_exe"] = p
                break

        # 2. Resamplers Detection (Moresampler / Resampler)
        for pdir in search_dirs:
            for eng in ["moresampler.exe", "resampler.exe", "world4utau.exe", "fresamp.exe"]:
                local_cand = os.path.join(pdir, "utau_engines", eng)
                if os.path.exists(local_cand) and not config["resampler_exe"]:
                    config["resampler_exe"] = local_cand
                    break

        if not config["resampler_exe"]:
            sys_resamplers = [
                os.path.join(localappdata, "Programs", "OpenUtau", "Resamplers", "moresampler.exe"),
                os.path.join(localappdata, "Programs", "OpenUtau", "Resamplers", "resampler.exe"),
                os.path.join(progfiles_x86, "UTAU", "resampler.exe"),
                os.path.join(progfiles_x86, "UTAU", "moresampler.exe"),
                os.path.join(appdata, "OpenUtau", "Resamplers", "moresampler.exe"),
            ]
            for p in sys_resamplers:
                if os.path.exists(p):
                    config["resampler_exe"] = p
                    break

        # 3. Voicebanks Detection
        discovered_vbs = {}
        for pdir in search_dirs:
            vb_root = os.path.join(pdir, "voicebanks")
            if os.path.exists(vb_root):
                for item in os.listdir(vb_root):
                    item_p = os.path.join(vb_root, item)
                    if os.path.isdir(item_p) and os.path.exists(os.path.join(item_p, "oto.ini")):
                        discovered_vbs[item] = item_p

        sys_vb_dirs = [
            os.path.join(appdata, "OpenUtau", "Singers"),
            os.path.join(progfiles_x86, "UTAU", "voice"),
            os.path.join(userprofile, "Documents", "OpenUtau", "Singers"),
        ]
        for vdir in sys_vb_dirs:
            if os.path.exists(vdir):
                if not config["openutau_singers_dir"]:
                    config["openutau_singers_dir"] = vdir
                for item in os.listdir(vdir):
                    item_p = os.path.join(vdir, item)
                    if os.path.isdir(item_p) and (os.path.exists(os.path.join(item_p, "oto.ini")) or os.path.exists(os.path.join(item_p, "character.yaml"))):
                        if item not in discovered_vbs:
                            discovered_vbs[item] = item_p

        config["available_voicebanks"] = discovered_vbs
        if discovered_vbs:
            teto_matches = [k for k in discovered_vbs if "teto" in k.lower()]
            config["voicebank_dir"] = discovered_vbs[teto_matches[0]] if teto_matches else list(discovered_vbs.values())[0]

        # 4. VST Directories
        sys_vsts = [
            os.path.join(progfiles, "Common Files", "VST3"),
            os.path.join(progfiles_x86, "Common Files", "VST3"),
            os.path.join(progfiles, "VSTPlugins"),
            os.path.join(progfiles, "Steinberg", "VstPlugins"),
            os.path.join(localappdata, "Programs", "Common", "VST3"),
        ]
        for vd in sys_vsts:
            if os.path.exists(vd) and vd not in config["vst_directories"]:
                config["vst_directories"].append(vd)

        for pdir in search_dirs:
            inst_dir = os.path.join(pdir, "instruments")
            if os.path.exists(inst_dir) and inst_dir not in config["vst_directories"]:
                config["vst_directories"].append(inst_dir)

        return config
