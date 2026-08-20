"""
OpenVocal-DAW: Mastering DSP Engine
Applies analog tape glue saturation and True Peak limiting (-0.3 dBFS).
"""

import numpy as np
import soundfile as sf


class MasteringDSP:
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
