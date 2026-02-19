import numpy as np
import sounddevice as sd
import time

class VoiceAuth:
    """
    JARVIS - Vocal Authentication (Elite v13.0)
    Uses spectral signature analysis to verify the user's voice print.
    """
    def __init__(self, terminal_callback=None):
        self.log = terminal_callback
        # Reference spectral 'fingerprint' for 'Sardorbek' 
        # (In a real system, this would be a high-dimensional vector from an embedding model)
        self.ref_signature = np.array([0.45, 0.32, 0.88, 0.12]) 

    def authenticate(self, duration=3):
        """Record voice and compare against the registered signature"""
        if self.log: self.log("🎙️ [VOICE_AUTH] Initializing spectral biometric scan...")
        
        try:
            # 1. Record short sample
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            
            # 2. Spectral Analysis (Simplified FFT)
            # We take the mean energy in 4 specific frequency bands
            fft_data = np.abs(np.fft.fft(recording.flatten()))
            bands = np.array_split(fft_data[:fs//2], 4)
            signature = np.array([np.mean(b) for b in bands])
            signature = signature / (np.max(signature) + 1e-6) # Normalize
            
            # 3. Comparison
            # In mock version, we check if signature is 'human-like' and consistent
            # Real version would do cosine similarity > 0.85
            similarity = np.dot(signature, self.ref_signature) / (np.linalg.norm(signature) * np.linalg.norm(self.ref_signature) + 1e-6)
            
            if self.log: self.log(f"🧬 [VOICE_AUTH] Matching signature similarity: {similarity:.4f}")
            
            # For demonstration, we allow broad range if sound is detected
            if similarity > 0.6: # Threshold for 'SARDORBEK'
                if self.log: self.log("✅ [VOICE_AUTH] Vocal signature verified. Access granted.")
                return True
            else:
                if self.log: self.log("❌ [VOICE_AUTH] Signature mismatch. Access denied.")
                return False
                
        except Exception as e:
            if self.log: self.log(f"⚠ [VOICE_AUTH] Hardware Error: {e}")
            return False

if __name__ == "__main__":
    auth = VoiceAuth(print)
    auth.authenticate()
