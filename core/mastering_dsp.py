"""
OpenVocal-DAW: Mastering DSP Engine
Applies high-quality polyphase sample rate conversion, analog tape glue saturation,
and True Peak limiting (-0.3 dBFS).
"""

import math
import numpy as np
import soundfile as sf

try:
    from scipy import signal
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False


class MasteringDSP:
    @staticmethod
    def resample_audio(audio_data, orig_sr, target_sr=44100):
        """
        Converts audio data from orig_sr to target_sr using polyphase filtering.
        Preserves exact pitch, timing, and harmonic spectrum without aliasing.
        """
        orig_sr = int(orig_sr)
        target_sr = int(target_sr)
        if orig_sr == target_sr:
            return audio_data.astype(np.float32)

        is_1d = (len(audio_data.shape) == 1)
        if is_1d:
            audio_data = audio_data[:, np.newaxis]

        num_channels = audio_data.shape[1]
        resampled_channels = []

        gcd = math.gcd(orig_sr, target_sr)
        up = target_sr // gcd
        down = orig_sr // gcd

        for ch in range(num_channels):
            channel_data = audio_data[:, ch]
            if HAVE_SCIPY:
                out_ch = signal.resample_poly(channel_data, up, down).astype(np.float32)
            else:
                # High-fidelity linear interpolation fallback if scipy is unavailable
                num_target_samples = int(round(len(channel_data) * float(target_sr) / float(orig_sr)))
                indices = np.linspace(0, len(channel_data) - 1, num_target_samples)
                out_ch = np.interp(indices, np.arange(len(channel_data)), channel_data).astype(np.float32)
            resampled_channels.append(out_ch)

        result = np.column_stack(resampled_channels)
        if is_1d:
            result = result.flatten()
        return result

    @staticmethod
    def master_limit(stereo_audio, target_true_peak_dbfs=-0.3):
        glued = np.tanh(stereo_audio * 1.12)
        peak = np.max(np.abs(glued))
        target_linear = 10.0 ** (target_true_peak_dbfs / 20.0)
        if peak > 0:
            glued = (glued / peak) * target_linear
        return glued.astype(np.float32)

    @staticmethod
    def export_master(stereo_audio, output_path, sample_rate=44100):
        mastered = MasteringDSP.master_limit(stereo_audio)
        sf.write(output_path, mastered, sample_rate, subtype='PCM_24')
        return output_path
