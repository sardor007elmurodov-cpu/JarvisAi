"""
JARVIS - Browser Helper
YouTube va boshqa saytlarda avtomatik yozish
"""

import time
import webbrowser
import pyautogui
from utils import setup_logger


class BrowserHelper:
    """
    Browser'da avtomatik yozish uchun helper class
    PyAutoGUI orqali koordinata va tab ishlatish
    """
    
    def __init__(self):
        self.logger = setup_logger("BrowserHelper")
        self.logger.info("BrowserHelper initialized")
    
    def youtube_search(self, query):
        """
        YouTube'da qidirish va birinchi natijani qo'yish (Elite v14.0)
        """
        self.logger.info(f"YouTube search & play: {query}")
        
        # YouTube qidiruv sahifasini ochish
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        
        # Sahifa yuklanishini kutish (5 sekund)
        time.sleep(5)
        
        # Birinchi videoni tanlash va qo'yish
        # YouTube strukturasiga ko'ra bir necha marta Tab va Enter
        self.logger.info("Automation: Playing the first result...")
        for _ in range(3): # Tablar soni sahifa strukturasiga qarab o'zgarishi mumkin
            pyautogui.press('tab')
            time.sleep(0.2)
        
        pyautogui.press('enter')
        
        return f"YouTube'da '{query}' qidirildi va ijro etilmoqda."
    
    def youtube_open_video(self, video_url):
        """
        YouTube video ochish
        
        Args:
            video_url (str): Video URL
            
        Returns:
            str: Natija
        """
        self.logger.info(f"Opening YouTube video: {video_url}")
        webbrowser.open(video_url)
        time.sleep(3)  # Ochilishini kutish
        
        return f"Video ochildi: {video_url}"
    
    def youtube_comment(self, video_url, comment_text):
        """
        YouTube video'ga komment yozish
        ESLATMA: Login qilgan bo'lish kerak
        
        Args:
            video_url (str): Video URL
            comment_text (str): Komment matni
            
        Returns:
            str: Natija
        """
        self.logger.info(f"Commenting on YouTube video: {comment_text}")
        
        # Video ochish
        webbrowser.open(video_url)
        time.sleep(5)  # Sahifa yuklanishini kutish
        
        # Scroll down to comments
        self.logger.info("Scrolling to comments section...")
        for _ in range(3):
            pyautogui.scroll(-300)
            time.sleep(0.5)
        
        # Tab bosish orqali komment box'ga o'tish
        self.logger.info("Finding comment box...")
        time.sleep(1)
        
        # Komment yozish (Tab va Enter)
        # ESLATMA: Bu sahifa strukturasiga bog'liq
        pyautogui.press('tab')  # Comment box'ga o'tish uchun
        time.sleep(0.5)
        
        pyautogui.write(comment_text, interval=0.05)
        time.sleep(0.5)
        
        self.logger.info("Comment written. Manual posting required.")
        return f"Komment yozildi (qo'lda Post bosing): {comment_text}"
    
    def web_fill_input(self, url, selector_hint, text):
        """
        Istalgan saytda input to'ldirish
        
        Args:
            url (str): Sayt URL'i
            selector_hint (str): Input maydoni haqida ma'lumot
            text (str): Yoziladigan matn
            
        Returns:
            str: Natija
        """
        self.logger.info(f"Filling input on {url}: {text}")
        
        # Sayt ochish
        webbrowser.open(url)
        time.sleep(3)
        
        # Tab bilan input box topish
        self.logger.info(f"Looking for input: {selector_hint}")
        time.sleep(1)
        
        # Matn yozish
        pyautogui.write(text, interval=0.05)
        
        return f"Matn kiritildi: {text}"
    
    def google_search_and_click(self, query, result_number=1):
        """
        Google'da qidirish va birinchi natijani ochish
        
        Args:
            query (str): Qidiruv so'rovi  
            result_number (int): Qaysi natijani ochish (1-10)
            
        Returns:
            str: Natija
        """
        self.logger.info(f"Google search and click: {query}, result #{result_number}")
        
        # Google qidiruv
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        time.sleep(3)
        
        # Tab bosish orqali natijalarga o'tish
        # Odatda 10-12 ta Tab kerak birinchi natijaga etish uchun
        tab_count = 10 + (result_number - 1) * 2
        
        for _ in range(tab_count):
            pyautogui.press('tab')
            time.sleep(0.1)
        
        # Enter bosish - natijani ochish
        pyautogui.press('enter')
        
        return f"Google natijasi #{result_number} ochildi: {query}"


# Test
if __name__ == "__main__":
    helper = BrowserHelper()
    
    # Test 1: YouTube qidiruv
    print("Test 1: YouTube search")
    result = helper.youtube_search("Python tutorial")
    print(f"Result: {result}")
    
    time.sleep(3)
    
    # Test 2: Google qidiruv
    print("\nTest 2: Google search and click")
    result = helper.google_search_and_click("GitHub")
    print(f"Result: {result}")
