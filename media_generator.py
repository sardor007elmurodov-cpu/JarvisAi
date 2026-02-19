
import os
import time
import base64
from utils import setup_logger

class MediaGenerator:
    """
    JARVIS Media Generation Engine
    Generates images and videos using Hugging Face Inference API.
    """
    def __init__(self):
        self.logger = setup_logger("MediaGen")
        # Biz config.py dagi kalitni olamiz
        try:
             import config
             self.api_key = config.HUGGINGFACE_API_KEY
        except:
             self.api_key = ""

    def generate_image(self, prompt):
        """
        Generate image using Stable Diffusion (via Hugging Face)
        """
        if not self.api_key or "YOUR_" in self.api_key:
             return "Hugging Face API kaliti kiritilmagan."
        
        self.logger.info(f"Generating image for: {prompt}")
        import requests
        
        # Free & Fast Model: Stable Diffusion XL or similar
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                # Save image
                timestamp = int(time.time())
                filename = f"image_{timestamp}.jpg"
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                # Try to open it
                os.startfile(filename)
                return f"Rasm tayyor: {filename}"
            else:
                return f"Xatolik: {response.text}"
                
        except Exception as e:
            return f"Error: {e}"

    def generate_video(self, prompt):
        """
        Generate short video using ModelScope (via Hugging Face)
        Note: Free tier might be slow or have queue.
        """
        if not self.api_key or "YOUR_" in self.api_key:
             return "Hugging Face API kaliti kiritilmagan."

        self.logger.info(f"Generating video for: {prompt}")
        import requests
        
        # Model: damo-vilab/text-to-video-ms-1.7b
        API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                timestamp = int(time.time())
                filename = f"video_{timestamp}.mp4"
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                # Try to open it
                os.startfile(filename)
                return f"Video tayyor: {filename}"
            else:
                 # Check if loading
                if "loading" in response.text.lower():
                     return "Model yuklanmoqda (sovuq start). Iltimos, 1 daqiqadan keyin qayta urining."
                return f"Xatolik: {response.text}"
        except Exception as e:
            return f"Error: {e}"
