"""
JARVIS - Global Eye (Dunyoviy Ong)
Dunyo bo'ylab nimalar sodir bo'layotganini (Trendlarni) kuzatish tizimi.
Manbalar: Google Trends (RSS), Wttr.in (Ob-havo), MarketMonitor.
"""
import requests
import xml.etree.ElementTree as ET
import json
import time
import os
import random
from config import GEMINI_API_KEY, AI_MODEL_NAME
from utils import setup_logger
from market_monitor import MarketMonitor

class GlobalEye:
    def __init__(self):
        self.logger = setup_logger("GlobalEye")
        self.market = MarketMonitor()
        self.last_analysis = {
            "mood": "CALM", 
            "summary": "Tizim barqaror kutmoqda.", 
            "color": "#00e0ff",
            "weather": {"temp": "N/A", "condition": "N/A"},
            "market": "N/A"
        }
        self.last_fetch_time = 0
        self.cache_duration = 300 # 5 minutes cache

    def get_weather(self, city="Tashkent"):
        """Wttr.in orqali ob-havo ma'lumotlarini olish"""
        try:
            # format=%t+%C returns "Temperature Condition" e.g. "+25C Sunny"
            url = f"https://wttr.in/{city}?format=%t|%C"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                parts = response.text.strip().split("|")
                if len(parts) >= 2:
                    return {"temp": parts[0].strip(), "condition": parts[1].strip()}
            return {"temp": "N/A", "condition": "Unknown"}
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            return {"temp": "N/A", "condition": "Error"}

    def get_trends(self, country="US"):
        """Google Trends RSS orqali mavzularni olish"""
        try:
            url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={country}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                trends = []
                # Namespace handling usually required for RSS extensions, but simple findall might work for basic items
                # If standard RSS, iterate items
                for item in root.findall(".//item"):
                    title = item.find("title").text
                    trends.append(title)
                    if len(trends) >= 5: break
                return trends
            return []
        except Exception as e:
            self.logger.error(f"Trends error: {e}")
            return []

    def analyze_world(self):
        """Dunyodagi vaziyatni tahlil qilish va HUD uchun strukturaviy ma'lumot qaytarish"""
        # Cache check
        if time.time() - self.last_fetch_time < self.cache_duration:
            return self.last_analysis

        self.logger.info("Analyzing global trends (Refresh)...")
        
        # 1. Weather
        weather = self.get_weather("Tashkent")
        
        # 2. Market
        btc = self.market.get_raw_crypto_price("bitcoin")
        market_status = f"BTC: ${btc:,.0f}" if btc else "Market: Stable"

        # 3. Trends (Mood Analysis)
        trends = self.get_trends("US") + self.get_trends("UZ")
        
        # Simple local sentiment analysis (fallback)
        mood = "CALM"
        color = "#00e0ff"
        summary = f"Ob-havo: {weather['temp']}, {weather['condition']}. Bozorda {market_status}. Dunyoda tinchlik."

        # Keywords for simple sentiment
        critical_keywords = ["war", "crash", "attack", "crisis", "urush", "halokat"]
        tense_keywords = ["conflict", "tension", "election", "protest", "nizo"]
        
        full_text = " ".join(trends).lower()
        if any(w in full_text for w in critical_keywords):
            mood = "CRITICAL"
            color = "#ff4444"
            summary = "Global xavf darajasi yuqori. Ehtiyotkorlik talab etiladi."
        elif any(w in full_text for w in tense_keywords):
            mood = "TENSE"
            color = "#ffaa00"
            summary = "Dunyoda keskinlik kuzatilmoqda. Yangiliklarni kuzating."

        # AI Analysis (Optional/Async could be better, skipping to avoid blocking/quota)
        # Using local heuristic is faster and safer for HUD
        
        self.last_analysis = {
            "mood": mood,
            "summary": summary,
            "color": color,
            "weather": weather,
            "market": market_status,
            "trends": trends[:3]
        }
        self.last_fetch_time = time.time()
        return self.last_analysis

if __name__ == "__main__":
    eye = GlobalEye()
    print(json.dumps(eye.analyze_world(), indent=2))

