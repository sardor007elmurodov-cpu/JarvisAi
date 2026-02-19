import google.genai as genai
from google.genai import types
import config
import os
import PIL.Image
import requests

class GeminiBrain:
    """
    JARVIS - LLM Brain (Gemini 2.0 SDK)
    Handles complex reasoning and natural conversation using the latest google-genai SDK.
    """
    
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model_name = config.AI_MODEL_NAME
        self.system_prompt = config.SYSTEM_PROMPT
        self.client = None
        self._initialized = False
        
        self._setup()

    def _setup(self):
        """Setup the Gemini API client"""
        if not self.api_key or self.api_key.strip() == "YOUR_GEMINI_API_KEY":
            print("⚠ Gemini API Key topilmadi. LLM Brain o'chirilgan.")
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            self.config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.7,
                top_p=0.95,
                top_k=64,
                max_output_tokens=1024,
                tools=[types.Tool(google_search=types.GoogleSearchRetrieval)]
            )
            
            # Test initialization (Removed to prevent blocking UI startup)
            # self.generate_response("Test initialization. Reply with 'OK'.")
            self._initialized = True
            print(f"✅ Gemini Brain initialized ({self.model_name}) [v2.0 SDK]")
        except Exception as e:
            print(f"⚠ Gemini Brain xatolik: {e}")

    def sync_temperament(self, temperament):
        """Update system instructions based on current mood (Elite v13.0)"""
        base_prompt = config.SYSTEM_PROMPT
        
        if temperament == "ENTHUSIASTIC":
            extra = "\nSHAXSIYAT YANGILANISHI (BIO-SYNC: JOY): Kayfiyatingiz xushnud. Hazil-mutoyiba ishlating, gaplaringizda jo'shqinlik va do'stona ruh bo'lsin. Foydalanuvchi bilan birga quvoning."
        elif temperament == "CALM":
            extra = "\nSHAXSIYAT YANGILANISHI (BIO-SYNC: STRESS): Foydalanuvchi charchagan yoki stressda. Juda qisqa, xotirjam va professional javob bering. Ortqicha gap va hazil qilmang. Faqat yordam bering."
        else:
            extra = "" # Default professional
            
        self.config.system_instruction = base_prompt + extra
        # self.logger.info(f"🧠 Brain temperament synchronized: {temperament}")

    def generate_response(self, prompt):
        """Generate a response from the LLM with multi-provider fallback support"""
        # Auto-sync temperament before generating
        self.sync_temperament(config.CURRENT_TEMPERAMENT)
        
        # 0. Try OpenAI (Preferred if available)
        openai_res = self._generate_openai_response(prompt)
        if openai_res: return openai_res

        # 1. Try DeepSeek First
        deepseek_res = self._generate_deepseek_response(prompt)
        if deepseek_res: return deepseek_res

        # 2. Try Gemini
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self.config
                )
                return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    print(f"⚠ Gemini API Quota Exceeded (429). Falling back to Groq...")
                else:
                    print(f"⚠ Gemini Brain Error: {e}")
        
        # 3. Try Groq (Fast Fallback)
        groq_res = self._generate_groq_fallback(prompt)
        if groq_res and "Janob" in groq_res: return groq_res # Validate response
        
        # 4. Try Hugging Face (Free Tier)
        hf_res = self._generate_huggingface_fallback(prompt)
        if hf_res: return hf_res

        # 5. Try Mistral (Free Tier)
        mistral_res = self._generate_mistral_fallback(prompt)
        if mistral_res: return mistral_res
        
        return self._generate_local_fallback(prompt)

    def _generate_openai_response(self, prompt):
        """OpenAI GPT-4o Integration (Elite v20.0)"""
        if not config.OPENAI_API_KEY:
             return None
             
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o", # Using GPT-4o for speed and intelligence
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 512
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ OpenAI Response: {content[:50]}...")
                return content
            else:
                if response.status_code == 429:
                    print("⚠ OpenAI Quota Exceeded (429).")
                elif response.status_code == 401:
                    print("⚠ OpenAI API Key Invalid (401).")
                else:
                    print(f"⚠ OpenAI Error: {response.text}")
                return None
        except Exception as e:
            print(f"⚠ OpenAI Connection Error: {e}")
            return None

    def _generate_deepseek_response(self, prompt):
        """DeepSeek API Implementation (Elite v19.5)"""
        import requests
        import json
        
        api_key = getattr(config, "DEEPSEEK_API_KEY", "")
        if not api_key or "sk-" not in api_key: return None

        try:
            url = "https://api.deepseek.com/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": getattr(config, "DEEPSEEK_MODEL_NAME", "deepseek-chat"),
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            return None
        except Exception:
            return None

    def _generate_groq_fallback(self, prompt):
        """Groq API Fallback (Free Tier - Llama 3)"""
        import requests
        import json
        
        api_key = getattr(config, "GROQ_API_KEY", "")
        model = getattr(config, "FALLBACK_MODEL_NAME", "llama-3.3-70b-versatile")
        
        # Groq ishlamasa yoki kalit bo'lmasa, Lokal AI-ga o'tamiz
        if not api_key or "gsk_" not in api_key:
            return self._generate_local_fallback(prompt)

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=7)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return self._generate_local_fallback(prompt)
        except Exception:
            return self._generate_local_fallback(prompt)

    
    def _generate_huggingface_fallback(self, prompt):
        """Hugging Face Inference API (Free)"""
        import requests
        import json
        
        api_key = getattr(config, "HUGGINGFACE_API_KEY", "")
        if not api_key or "YOUR_" in api_key: return None
        
        try:
            url = f"https://api-inference.huggingface.co/models/{getattr(config, 'HUGGINGFACE_MODEL_NAME', 'mistralai/Mistral-7B-Instruct-v0.2')}"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "inputs": f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:",
                "parameters": {"max_new_tokens": 250, "temperature": 0.7}
            }
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and 'generated_text' in result[0]:
                    return result[0]['generated_text'].split("Assistant:")[-1].strip()
            return None
        except: return None

    def _generate_mistral_fallback(self, prompt):
        """Mistral AI Platform (Free Tier)"""
        import requests
        import json
        
        api_key = getattr(config, "MISTRAL_API_KEY", "")
        if not api_key or "YOUR_" in api_key: return None
        
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": getattr(config, "MISTRAL_MODEL_NAME", "mistral-small-latest"),
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post(url, headers=headers, json=data, timeout=8)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
        except: return None

    def _generate_local_fallback(self, prompt):
        """Lokal AI Fallback (Ollama)"""
        try:
            from local_llm import LocalLLM
            local_ai = LocalLLM()
            if local_ai.is_available():
                print("ℹ Local LLM (Ollama) ishlatilmoqda...")
                return local_ai.generate_response(prompt)
            else:
                return "Janob, barcha AI xizmatlarida (Gemini, Groq, Local) uzilish yuz berdi."
        except Exception as e:
            return f"Janob, AI brain butunlay ishdan chiqdi: {e}"
            
    def analyze_image(self, image_path, prompt):
        """
        Analyze an image (screenshot) using Gemini Vision capabilities.
        """
        if not self.client:
            return None
            
        try:
            img = PIL.Image.open(image_path)
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, img],
                    config=self.config
                )
                return response.text
            finally:
                img.close()
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠ Gemini Vision Quota Exceeded. Falling back to text-only insight...")
                # Groq doesn't support vision for free as easily, so we fallback to text
                return self._generate_groq_fallback(f"[VISION_ERROR] User prompt was: {prompt}. Please explain that image analysis is temporarily unavailable but you are standing by for text commands.")
            print(f"⚠ AI Vision Error: {e}")
            return None

    def extract_and_save_facts(self, user_text, memory_engine):
        """
        Analyze text for user facts and save to memory.
        Runs in background.
        """
        if len(user_text) < 10: return
        
        prompt = f"""
        Analyze this user input: "{user_text}"
        Extract any specific facts about the user (name, preferences, habits, plans, relationships).
        If no facts are present, return "NO_FACTS".
        Format: FACT: <fact> | CATEGORY: <category>
        """
        
        try:
            # Use Groq for speed/cost if available, or Gemini
            response = self._generate_groq_fallback(prompt)
            if not response or "NO_FACTS" in response:
                return
            
            # Parse response
            lines = response.split('\n')
            for line in lines:
                if "FACT:" in line and "CATEGORY:" in line:
                    parts = line.split("|")
                    fact = parts[0].replace("FACT:", "").strip()
                    category = parts[1].replace("CATEGORY:", "").strip()
                    
                    # Verify duplicates logic could be here, but for now just add
                    memory_engine.add_fact(fact, category)
                    print(f"🧠 MEMORY STORED: {fact} ({category})")
                    
        except Exception as e:
            print(f"Fact extraction error: {e}")

if __name__ == "__main__":
    brain = GeminiBrain()
    if brain._initialized:
        print(brain.generate_response("Salom, JARVIS"))
