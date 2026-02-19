"""
JARVIS - Voice Module
Ovoz tanish va matnni ovozga o'girish
"""

import os
import time
import threading


class TextToSpeech:
    """
    Matnni ovozga o'girish (Text-to-Speech)
    pyttsx3 kutubxonasidan foydalanadi
    """
    
    def __init__(self, rate=150, volume=1.0):
        """
        TTS ni ishga tushirish
        
        Args:
            rate (int): Ovoz tezligi (so'z/min)
            volume (float): Ovoz balandligi (0.0 - 1.0)
        """
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._initialized = False
        self._init_engine()
    
    def _init_engine(self):
        """TTS engine'ni boshlash"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # O'zbek tili sozlash (agar mavjud bo'lsa)
            voices = self.engine.getProperty('voices')
            
            # O'zbek ovozini qidirish
            uzbek_voice = None
            for voice in voices:
                # Check for 'uz' in language codes or 'uzbek' in name (case-insensitive)
                if 'uz' in voice.languages or 'uzbek' in voice.name.lower():
                    uzbek_voice = voice.id
                    break
            
            # Agar topilmasa - default, lekin tez
            if uzbek_voice:
                self.engine.setProperty('voice', uzbek_voice)
                print(f"✓ O'zbek ovozi topildi va o'rnatildi: {uzbek_voice}")
            else:
                print("⚠ O'zbek ovozi topilmadi. Standart ovoz ishlatiladi.")
            
            self.engine.setProperty('rate', 160)  # Tez
            self.engine.setProperty('volume', 0.9)
            
            self._initialized = True
            print("✓ TTS engine muvaffaqiyatli ishga tushdi")
        except ImportError:
            print("⚠ pyttsx3 kutubxonasi topilmadi. O'rnatish: pip install pyttsx3")
            self._initialized = False
        except Exception as e:
            print(f"⚠ TTS xatolik: {e}")
            self._initialized = False
    
    def speak(self, text):
        """
        Matnni ovozga o'girish (pyttsx3 orqali) - Fallback
        """
        if not self._initialized or not text or text.strip() == "":
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"pyttsx3 TTS xatoligi: {e}")

    async def _speak_edge(self, text, lang="uz"):
        """Edge TTS orqali gapirish (High Quality)"""
        import edge_tts
        import tempfile
        import os
        from playsound import playsound
        
        # Emoji va belgilarni tozalash (TTS xato bermasligi uchun)
        clean_text = text.replace('✅', '').replace('🕐', '').replace('📅', '')
        clean_text = clean_text.replace('⚠️', '').replace('💻', '').replace('◉', '')
        clean_text = clean_text.replace('⚙', '').replace('◆', '').replace('✖', '').strip()
        
        if not clean_text: return
        
        # Ovozlar xaritasi (Edge TTS nomi, pitch, rate)
        # Note: 'uz' codes often need 'uz-UZ' for some services
        voices = {
            "uz": "uz-UZ-SardorNeural", # Male JARVIS Voice
            "en": "en-US-ChristopherNeural", # Professional Male
            "ru": "ru-RU-DmitryNeural"
        }
        
        voice_name = voices.get(lang, "uz-UZ-SardorNeural")
        print(f"DEBUG: EdgeTTS attempting to speak with {voice_name}")
        
        try:
            # Create communication object
            communicate = edge_tts.Communicate(clean_text, voice_name)
            
            # Temporary file with .mp3 suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_filename = tmp_file.name
                
            await communicate.save(temp_filename)
            
            # Play the sound (Robust Method)
            try:
                # Try pygame first (smoother)
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.quit()
            except ImportError:
                # Fallback to playsound
                playsound(temp_filename)
            
            # Cleanup
            try:
                os.remove(temp_filename)
            except:
                pass
                
        except Exception as e:
            print(f"⚠ EdgeTTS Error (Falling back to Robot): {e}")
            # Fallback will take over in the main speak method
            raise e

    async def _speak_gtts(self, text, lang="uz"):
        """gTTS (Google TTS) orqali gapirish (Reliable Fallback)"""
        try:
            from gtts import gTTS
            import tempfile
            import os
            from playsound import playsound
            
            # gTTS "uz" ni qo'llab-quvvatlaydi
            tts_lang = "uz" if lang == "uz" else lang
            
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_filename = tmp_file.name
                
            tts.save(temp_filename)
            playsound(temp_filename)
            
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except Exception as e:
            # print(f"gTTS error: {e}")
            raise e

    def speak_async(self, text):
        """Asinxron ravishda gapirish"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
    
    def set_rate(self, rate):
        """Ovoz tezligini o'zgartirish"""
        self.rate = rate
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Ovoz balandligini o'zgartirish"""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.volume)
    
    def get_voices(self):
        """Mavjud ovozlar ro'yxatini olish"""
        if not self.engine:
            return []
        return self.engine.getProperty('voices')
    
    def set_voice(self, voice_id):
        """Ovoz turini o'zgartirish"""
        if self.engine:
            self.engine.setProperty('voice', voice_id)


class SpeechRecognizer:
    """
    Ovozni matnga o'girish (Speech-to-Text)
    SpeechRecognition kutubxonasidan foydalanadi
    """
    
    def __init__(self, language="uz-UZ", fallback_language="en-US"):
        """
        STT ni ishga tushirish
        
        Args:
            language (str): Asosiy til
            fallback_language (str): Zaxira til
        """
        self.language = language
        self.fallback_language = fallback_language
        self.recognizer = None
        self.microphone = None
        self._initialized = False
        self._init_recognizer()
    
    def _init_recognizer(self):
        """Recognizer'ni boshlash"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            
            # --- OFFLINE VOICE INTEGRATION (Elite v20.0) ---
            try:
                from offline_voice import OfflineVoiceEngine
                self.offline_engine = OfflineVoiceEngine()
                
                def load_offline():
                    if self.offline_engine.load_whisper():
                        self.use_offline = True
                        print("✅ Offline Voice Intelligence: ACTIVE")
                    else:
                        self.use_offline = False
                
                # Load in background to avoid blocking initialization/UI
                import threading
                threading.Thread(target=load_offline, daemon=True).start()
                
            except Exception as e:
                print(f"⚠ Offline Voice Init Error: {e}")
                self.use_offline = False
            
            # Mikrofonni tekshirish
            try:
                self.microphone = sr.Microphone()
                # Mikrofon sozlamalarini optimizatsiya qilish (Elite recalibration)
                with self.microphone as source:
                    print("⚙ Mikrofon kalibratsiyasi...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                self._initialized = True
                print("✓ Mikrofon tayyor, Janob.")
            except Exception as e:
                print(f"⚠ Mikrofon xatoligi: {e}")
                self._initialized = False
                
        except ImportError:
            print("⚠ SpeechRecognition kutubxonasi topilmadi")
            print("  O'rnatish: pip install SpeechRecognition pyaudio")
            self._initialized = False
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Mikrofondan ovozni eshitish
        
        Args:
            timeout (int): Ovoz kutish vaqti (sekund)
            phrase_time_limit (int): Maksimal gapirish vaqti
            
        Returns:
            audio: Audio ma'lumotlari yoki None
        """
        if not self._initialized:
            return None
        
        try:
            import speech_recognition as sr
            with self.microphone as source:
                print("🎤 Tinglayapman...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                return audio
        except Exception as e:
            print(f"⚠ Tinglash xatoligi: {e}")
            return None
    
    def recognize(self, audio, blocker=None):
        """
        Audio'ni matnga o'girish (Google Speech API)
        """
        if not audio or not self.recognizer:
            return None
            
        # Discard if system was speaking during capture (safety double-check)
        if blocker and hasattr(blocker, 'is_speaking') and blocker.is_speaking:
            return None
        
        # 0. OFFLINE VOICE (Priority)
        if getattr(self, 'use_offline', False):
            import tempfile
            try:
                # Save audio to temp wav
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_filename = tmp_file.name
                    with open(tmp_filename, "wb") as f:
                        f.write(audio.get_wav_data())
                
                text = self.offline_engine.transcribe(tmp_filename)
                try: os.remove(tmp_filename)
                except: pass
                
                if text: return text
            except Exception as e:
                print(f"⚠ Offline STT Error: {e}")

        # 1. Avval asosiy tilda urinish (Online Google)
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except Exception:
            pass
        
        # Fallback tilida urinish
        try:
            text = self.recognizer.recognize_google(audio, language=self.fallback_language)
            return text
        except Exception as e:
            print(f"⚠ Tanib olish xatoligi: {e}")
            return None
    
    def listen_and_recognize(self, timeout=5, phrase_time_limit=10, blocker=None):
        """
        Tinglash va tanib olishni birlashtirish
        """
        # Block if something is speaking (Feedback loop prevention)
        if blocker and hasattr(blocker, 'is_speaking') and blocker.is_speaking:
            return None
            
        audio = self.listen(timeout, phrase_time_limit)
        if audio:
            return self.recognize(audio, blocker=blocker)
        return None
    
    def is_available(self):
        """Mikrofon mavjudligini tekshirish"""
        return self._initialized


class VoiceAssistant:
    """
    TTS va STT ni birlashtirgan Voice Assistant
    """
    
    def __init__(self, language="uz-UZ", fallback_language="en-US", 
                 speech_rate=150, volume=1.0, enable_tts=True, enable_stt=True):
        """
        Voice Assistant'ni ishga tushirish
        
        Args:
            language (str): Asosiy til
            fallback_language (str): Zaxira til
            speech_rate (int): Ovoz tezligi
            volume (float): Ovoz balandligi
            enable_tts (bool): TTS yoqilganmi
            enable_stt (bool): STT yoqilganmi
        """
        self.enable_tts = enable_tts
        self.enable_stt = enable_stt
        self.is_speaking = False # Feedback loop blocker
        import threading
        self.lock = threading.Lock()
        
        # TTS
        if enable_tts:
            self.tts = TextToSpeech(rate=speech_rate, volume=volume)
        else:
            self.tts = None
        
        # STT
        if enable_stt:
            self.stt = SpeechRecognizer(language=language, fallback_language=fallback_language)
        else:
            self.stt = None
    
    def speak(self, text, lang="uz"):
        """Matnni ovozga o'girish (Edge TTS -> Silent Fallback to pyttsx3)"""
        if not text: return
        
        # Prevent concurrent speech requests
        with self.lock:
            if self.tts:
                # 1. Edge TTS (High Quality)
                if self.enable_tts:
                    import asyncio
                    try:
                        self.is_speaking = True
                        asyncio.run(self.tts._speak_edge(text, lang))
                        self.is_speaking = False
                        return # Successful
                    except Exception as e:
                        if "403" not in str(e):
                            print(f"VoiceAssistant Speak Error: {e}")
                        self.is_speaking = False

                # 2. Google TTS (Reliable Human-like Fallback)
                try:
                    self.is_speaking = True
                    print("DEBUG: Falling back to Google TTS...")
                    import asyncio
                    
                    # Run gTTS Sync Logic directly
                    from gtts import gTTS
                    import tempfile, os
                    
                    try:
                        tts = gTTS(text=text, lang=tts_lang, slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                            temp_filename = tmp_file.name
                        tts.save(temp_filename)
                    except ValueError:
                        # Fallback for "Language not supported: uz" -> Try 'tr' (Turkish)
                        print("DEBUG: 'uz' not supported by gTTS, trying 'tr' (Turkish)...")
                        tts = gTTS(text=text, lang='tr', slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                            temp_filename = tmp_file.name
                        tts.save(temp_filename)
                    
                    # Play with Pygame (Robust)
                    try:
                        import pygame
                        pygame.mixer.init()
                        pygame.mixer.music.load(temp_filename)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                        pygame.mixer.quit()
                    except ImportError:
                        from playsound import playsound
                        playsound(temp_filename)
                        
                    try: os.remove(temp_filename)
                    except: pass
                        
                    self.is_speaking = False
                    return # Successful
                except Exception as gtts_e:
                    print(f"⚠ Google TTS Failed: {gtts_e}")
                    self.is_speaking = False

                # 3. Local Fallback (pyttsx3 - Robotic)
                try:
                    self.is_speaking = True
                    self.tts.speak(text)
                    self.is_speaking = False
                except Exception as local_e:
                    self.is_speaking = False
                    print(f"Local TTS failed: {local_e}")
                    print(f"[JARVIS] {text}")
            else:
                print(f"[JARVIS] {text}")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """Ovozni tinglash va matnga o'girish"""
        if self.stt and self.enable_stt and self.stt.is_available():
            # Pass self as blocker to prevent hearing self
            return self.stt.listen_and_recognize(
                timeout=timeout, 
                phrase_time_limit=phrase_time_limit, 
                blocker=self
            )
        return None
        
    def listen_for_wake_word(self, wake_words):
        """Uyg'otish so'zini tinglash (Elite version)"""
        if not self.stt or not self.stt.is_available():
            return False
            
        try:
            import speech_recognition as sr
            import winsound
            
            with self.stt.microphone as source:
                # Elite sensitivity: Faster ambient check (0.1s is enough for continuous loop)
                self.stt.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                self.stt.recognizer.dynamic_energy_threshold = True
                
                try:
                    audio = self.stt.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    text = self.stt.recognize(audio)
                    
                    if text:
                        text_lower = text.lower().strip()
                        print(f"👂 [DEBUG] Mic heard: '{text_lower}'")
                        for word in wake_words:
                            if word.lower() in text_lower:
                                # FEEDBACK: Play subtle beep to confirm wake word detected
                                winsound.Beep(800, 150) 
                                return True
                except sr.WaitTimeoutError:
                    pass
        except Exception:
            pass
        return False
    
    def is_speech_available(self):
        """STT mavjudligini tekshirish"""
        return self.stt and self.stt.is_available()
    
    def is_tts_available(self):
        """TTS mavjudligini tekshirish"""
        return self.tts and self.tts._initialized


# Test
if __name__ == "__main__":
    print("=== Voice Module Test ===\n")
    
    # TTS test
    print("1. TTS Test:")
    tts = TextToSpeech()
    if tts._initialized:
        tts.speak("Salom, men JARVISman")
    
    # STT test
    print("\n2. STT Test:")
    stt = SpeechRecognizer()
    if stt.is_available():
        print("Biror narsa ayting...")
        text = stt.listen_and_recognize()
        if text:
            print(f"Siz aytdingiz: {text}")
        else:
            print("Ovoz tanib olinmadi")
    
    print("\n=== Test tugadi ===")
