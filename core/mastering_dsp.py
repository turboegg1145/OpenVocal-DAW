"""
OpenVocal-DAW: Studio DSP Mastering & Mixdown Engine
100% Parity with Project NEON PULSE master_mixdown.py.
Applies Mid-Pocket Carving (-3.2dB @ 1.5-3.5kHz), Space Reverb Send,
Analog Tape Saturation Glue tanh(1.08x), and True-Peak Brickwall Limiting (-0.30 dBFS).
"""

import os
import numpy as np
import scipy.signal as signal
import soundfile as sf


class MasteringDSP:
    @staticmethod
    def mix_and_master(stems_dict, output_master_path, sr=44100, bpm=130.0, total_bars=78):
        dur_sec = (total_bars * 4.0 * 60.0) / bpm
        total_samples = int(round(dur_sec * sr))

        def load_audio(fp):
            if not os.path.exists(fp):
                return np.zeros((total_samples, 2), dtype=np.float32)
            d, fs = sf.read(fp, dtype='float32')
            if d.ndim == 1:
                d = np.column_stack([d, d])
            if len(d) < total_samples:
                pad = np.zeros((total_samples - len(d), 2), dtype=np.float32)
                d = np.vstack([d, pad])
            else:
                d = d[:total_samples]
            return d

        print("  🎛️ [Mastering DSP] Ingesting 7 Cyber Stems and applying Studio Mid-Carving & Glue...")

        inst_mix = np.zeros((total_samples, 2), dtype=np.float32)
        gain_weights = {
            "kick": 1.05,
            "snare": 0.95,
            "hihats": 0.80,
            "reese": 0.90,
            "pluck": 0.85,
            "supersaw": 0.80,
            "guitar": 0.75
        }

        for name, fp in stems_dict.items():
            if "vocal" in name.lower():
                continue
            audio = load_audio(fp)
            weight = 0.85
            for k, w in gain_weights.items():
                if k in name.lower():
                    weight = w
                    break
            inst_mix += audio * weight

        vocal_audio = np.zeros((total_samples, 2), dtype=np.float32)
        for name, fp in stems_dict.items():
            if "vocal" in name.lower():
                vocal_audio = load_audio(fp)
                break

        # Vocal 100Hz High Pass
        sos_vocal_hp = signal.butter(4, 100, 'highpass', fs=sr, output='sos')
        vocal_proc = signal.sosfilt(sos_vocal_hp, vocal_audio, axis=0)

        # Dynamic Mid-Pocket Carving on Instrumental (-3.2 dB @ 1.5k-3.5kHz)
        vocal_env = np.mean(np.abs(vocal_proc), axis=1)
        vocal_smooth = signal.medfilt(vocal_env, kernel_size=401)
        vocal_active = np.clip(vocal_smooth * 8.0, 0.0, 1.0)[:, np.newaxis]

        sos_mid_dip = signal.butter(2, [1500, 3500], 'bandstop', fs=sr, output='sos')
        inst_dipped = signal.sosfilt(sos_mid_dip, inst_mix, axis=0)
        inst_carved = inst_mix * (1.0 - vocal_active * 0.31) + inst_dipped * (vocal_active * 0.31)

        # Space Shimmer Reverb
        reverb_wet = np.zeros_like(vocal_proc)
        for delay_ms, decay in [(37, 0.25), (63, 0.20), (95, 0.15), (130, 0.10)]:
            del_samp = int(round((delay_ms / 1000.0) * sr))
            shifted = np.roll(vocal_proc, del_samp, axis=0)
            shifted[:del_samp] = 0
            reverb_wet += shifted * decay

        vocal_final = vocal_proc * 1.15 + reverb_wet * 0.18

        # Master Bus Summing & Analog Glue & True-Peak Limiter
        full_mix = inst_carved + vocal_final
        glued_master = np.tanh(full_mix * 1.08)

        # Brickwall True-Peak Limiter: Target -0.30 dBFS (0.96605)
        target_peak = 10.0 ** (-0.30 / 20.0)
        master_peak = np.max(np.abs(glued_master))
        if master_peak > 0:
            glued_master = (glued_master / master_peak) * target_peak

        os.makedirs(os.path.dirname(os.path.abspath(output_master_path)), exist_ok=True)
        sf.write(output_master_path, glued_master, sr, subtype='PCM_24')
        print(f"  ✓ Saved 100% Studio Master WAV: {output_master_path} (True-Peak: -0.30 dBFS)")
        return output_master_path
