"""
JARVIS - Voice Transformer
Ovozni yozib olib, unga effekt berish va qayta eshittirish.
Effektlar:
- Robot (Metallik)
- Chipmunk (Tez va ingichka)
- Iron Man (Past va yo'g'on)
"""
import sounddevice as sd
import numpy as np
import scipy.signal
import time
from utils import setup_logger

class VoiceTransformer:
    def __init__(self):
        self.logger = setup_logger("VoiceTransformer")
        self.sample_rate = 44100
        self.duration = 5 # 5 soniya yozib oladi

    def process_voice(self, effect="iron_man"):
        """Ovozni yozish va o'zgartirish"""
        try:
            self.logger.info("Recording...")
            
            # 1. Yozib olish
            recording = sd.rec(int(self.duration * self.sample_rate), 
                             samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()
            
            self.logger.info("Processing...")
            
            # 2. Effekt berish
            if effect == "robot":
                processed = self._apply_robot(recording)
            elif effect == "chipmunk":
                processed = self._apply_pitch_shift(recording, 1.5)
            elif effect == "iron_man":
                processed = self._apply_pitch_shift(recording, 0.7)
            else:
                processed = recording
                
            # 3. Ijro etish
            self.logger.info("Playing...")
            sd.play(processed, self.sample_rate)
            sd.wait()
            
            return f"{effect} effekti qo'llanildi."
            
        except Exception as e:
            self.logger.error(f"Voice transform error: {e}")
            return "Ovozni o'zgartirishda xatolik."

    def _apply_pitch_shift(self, data, factor):
        """Pitch o'zgartirish (Resampling usuli)"""
        # Oddiy resampling (tezlik va pitch o'zgaradi)
        # Haqiqiy pitch shift uchun FFT kerak, lekin bu oddiy va tez.
        indices = np.round(np.arange(0, len(data), factor))
        indices = indices[indices < len(data)].astype(int)
        return data[indices]

    def _apply_robot(self, data):
        """Robot effekti (Modulyatsiya)"""
        # Sinus to'lqin bilan ko'paytirish (Ring Modulation)
        t = np.arange(len(data)) / self.sample_rate
        carrier = 0.5 * np.sin(2 * np.pi * 50 * t) # 50 Hz g'o'ng'illash
        return data * carrier[:, np.newaxis]

if __name__ == "__main__":
    vt = VoiceTransformer()
    print("Gapiring (5 soniya)...")
    vt.process_voice("iron_man")
