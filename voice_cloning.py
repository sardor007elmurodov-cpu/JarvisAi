"""
JARVIS Voice Cloning Module (Phase 8)
Train custom voice or use ElevenLabs API
"""
import os
from utils import setup_logger

class VoiceCloning:
    """
    Voice cloning for JARVIS using ElevenLabs or local TTS
    """
    def __init__(self):
        self.logger = setup_logger("VoiceCloning")
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
        self.use_elevenlabs = bool(self.api_key)
        
        if self.use_elevenlabs:
            try:
                from elevenlabs import generate, set_api_key
                set_api_key(self.api_key)
                self.elevenlabs_available = True
                self.logger.info("ElevenLabs API initialized")
            except Exception as e:
                self.logger.error(f"ElevenLabs init error: {e}")
                self.elevenlabs_available = False
        else:
            self.elevenlabs_available = False
            self.logger.info("Voice cloning: ElevenLabs not configured")
    
    def generate_speech_elevenlabs(self, text, output_file="output.mp3"):
        """
        Generate speech using ElevenLabs API
        """
        if not self.elevenlabs_available:
            return False
            
        try:
            from elevenlabs import generate, save
            
            audio = generate(
                text=text,
                voice=self.voice_id if self.voice_id else "Antoni",  # Default voice
                model="eleven_multilingual_v2"
            )
            
            save(audio, output_file)
            self.logger.info(f"Speech saved to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"ElevenLabs generation error: {e}")
            return False
    
    def train_local_voice(self, audio_samples_folder):
        """
        Train local voice using Coqui TTS (XTTS-v2)
        Requires audio samples in folder
        """
        try:
            from TTS.api import TTS
            
            # Load XTTS model
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Get reference audio
            import glob
            wav_files = glob.glob(f"{audio_samples_folder}/*.wav")
            
            if not wav_files:
                return "No .wav files found in folder"
            
            # Use first sample as reference
            reference_audio = wav_files[0]
            
            self.local_tts = tts
            self.reference_audio = reference_audio
            
            return f"Voice trained with {len(wav_files)} samples"
        except Exception as e:
            self.logger.error(f"Local training error: {e}")
            return f"Error: {str(e)}"
    
    def generate_speech_local(self, text, output_file="output.wav"):
        """
        Generate speech using local trained voice
        """
        try:
            if not hasattr(self, 'local_tts'):
                return "Local voice not trained yet"
            
            self.local_tts.tts_to_file(
                text=text,
                file_path=output_file,
                speaker_wav=self.reference_audio,
                language="uz"  # Uzbek support
            )
            
            return f"Speech saved to {output_file}"
        except Exception as e:
            self.logger.error(f"Local generation error: {e}")
            return f"Error: {str(e)}"
    
    def speak_with_custom_voice(self, text):
        """
        Generate and play speech with custom voice
        """
        output_file = "jarvis_speech.mp3"
        
        if self.elevenlabs_available:
            success = self.generate_speech_elevenlabs(text, output_file)
        elif hasattr(self, 'local_tts'):
            output_file = "jarvis_speech.wav"
            result = self.generate_speech_local(text, output_file)
            success = "Error" not in result
        else:
            return "Voice cloning not configured"
        
        if success:
            # Play audio
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
                return "Speech played successfully"
            except:
                return f"Audio generated: {output_file}"
        else:
            return "Speech generation failed"

if __name__ == "__main__":
    cloning = VoiceCloning()
    if cloning.elevenlabs_available:
        print("ElevenLabs ready")
    else:
        print("Set ELEVENLABS_API_KEY environment variable")
        print("Or use local TTS with train_local_voice()")
