import os
import time
import pyautogui
import google.genai as genai
from PIL import Image
from config import GEMINI_API_KEY, AI_MODEL_NAME

class JARVISVisionAgent:
    """
    JARVIS - Vision-to-Action Agent (Elite v13.0)
    Uses Gemini Vision to identify GUI elements and perform autonomous actions.
    """
    def __init__(self, terminal_callback=None):
        self.log = terminal_callback
        self.api_key = GEMINI_API_KEY
        self.model_id = 'gemini-1.5-flash' # Using Flash for speed/UI tasks
        self.client = genai.Client(api_key=self.api_key)
        self.screenshot_path = os.path.join(os.getcwd(), "temp_vision.png")

    def find_and_click(self, description):
        """
        Capture screen, ask Gemini for element coordinates, and click.
        """
        if self.log: self.log(f"👁️ [VISION] Scouting screen for: '{description}'...")
        
        try:
            # 1. Capture screen
            screenshot = pyautogui.screenshot()
            screenshot.save(self.screenshot_path)
            
            # 2. Analyze with Gemini
            img = Image.open(self.screenshot_path)
            prompt = f"""
            Identify the exact center coordinates (x, y) of the element: "{description}".
            The screen resolution is {screenshot.width}x{screenshot.height}.
            Return JSON only: {{"found": true, "x": center_x, "y": center_y}}
            If not found, return {{"found": false}}.
            """
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, img]
            )
            
            import json
            import re
            
            # Extract JSON
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if data.get("found"):
                    x, y = data["x"], data["y"]
                    if self.log: self.log(f"🎯 [VISION] Target located at ({x}, {y}). Executing click...")
                    
                    # 3. Action
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    return f"Muvaffaqiyatli bajarildi, janob. '{description}' bosildi."
                else:
                    return f"Afsuski, '{description}' elementini ekranda topa olmadim."
            
            return "Vision tahlili natija bermadi."
            
        except Exception as e:
            if self.log: self.log(f"❌ [VISION] Error: {str(e)}")
            return f"Vision xatosi: {str(e)}"
        finally:
            if os.path.exists(self.screenshot_path):
                os.remove(self.screenshot_path)

    def describe_scene(self):
        """Analyze what's currently happening on screen for context"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(self.screenshot_path)
            img = Image.open(self.screenshot_path)
            
            prompt = "Describe what is currently visible on this desktop screen."
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, img]
            )
            return response.text
        except: return "Ekran ko'rinmadi."
