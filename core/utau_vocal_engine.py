"""Moresampler / UTAU Micro-timing Vocal Engine with -45ms Consonant Compensation."""
FRICATIVE_CHARS = ["す", "つ", "さ", "し", "せ", "そ", "か", "き", "く", "け", "こ", "た", "ち", "て", "と", "ぱ", "ば"]
def calculate_pre_utterance_compensation(lyric, sample_rate=44100):
    return int(0.045 * sample_rate) if any(c in lyric for c in FRICATIVE_CHARS) else 0
