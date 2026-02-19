
import os
import time
import threading
from utils import setup_logger

class OfflineVoiceEngine:
    """
    JARVIS Offline Voice Intelligence (Whisper + Silero).
    Provides 0-latency, private STT and TTS.
    """
    def __init__(self):
        self.logger = setup_logger("OfflineVoice")
        self.model_size = "tiny" # or 'base', 'small'
        self.model = None
        self._initialized = False

    def load_whisper(self):
        """Load Whisper model for offline STT"""
        try:
            from faster_whisper import WhisperModel
            self.logger.info(f"Loading Whisper ({self.model_size}) model...")
            # Run on CPU with INT8 by default to save resources
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            self._initialized = True
            self.logger.info("✅ Whisper AI loaded successfully.")
            return True
        except ImportError:
            self.logger.warning("❌ faster-whisper not installed. Run: pip install faster-whisper")
        except Exception as e:
            self.logger.error(f"Whisper load error: {e}")
        return False

    def transcribe(self, audio_file):
        """Transcribe audio file to text using Whisper"""
        if not self._initialized:
            return None
        
        try:
            segments, info = self.model.transcribe(audio_file, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()
            self.logger.info(f"Whisper heard: {text}")
            return text
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return None

    def synthesize(self, text, output_file="response.wav"):
        """
        Offline TTS using Silero (High Quality) or pyttsx3 (Standard).
        For now, we stick to pyttsx3 as a reliable offline fallback 
        unless Silero is manually configured.
        """
        import pyttsx3
        try:
            engine = pyttsx3.init()
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            return True
        except Exception as e:
            self.logger.error(f"Offline TTS error: {e}")
            return False

if __name__ == "__main__":
    ov = OfflineVoiceEngine()
    if ov.load_whisper():
        print("Whisper ready.")
    else:
        print("Whisper not available.")
