import pyttsx3
import speech_recognition as sr
import sys

def test_tts():
    print("Testing TTS...")
    try:
        engine = pyttsx3.init()
        engine.say("Testing voice system.")
        engine.runAndWait()
        print("TTS Success")
    except Exception as e:
        print(f"TTS Failed: {e}")

def test_mic():
    print("Testing Microphone...")
    try:
        r = sr.Recognizer()
        print(f"Available Microphones: {sr.Microphone.list_microphone_names()}")
        with sr.Microphone() as source:
            print("Say something...")
            # r.adjust_for_ambient_noise(source, duration=1)
            # audio = r.listen(source, timeout=3)
            # print("Heard something")
            print("Microphone access confirmed")
        print("Mic Success")
    except Exception as e:
        print(f"Mic Failed: {e}")

if __name__ == "__main__":
    test_tts()
    test_mic()
