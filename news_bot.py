"""
JARVIS News Bot & Web Scraper
Auto-scrape news, summarize with AI, read aloud
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import setup_logger

class NewsBot:
    """
    Auto-scrape news from configured sites
    Summarize articles, read aloud, send digests
    """
    def __init__(self):
        self.logger = setup_logger("NewsBot")
        self.news_sources = [
            "https://kun.uz",
            "https://daryo.uz",
            "https://bbc.com/uzbek"
        ]
        
    def scrape_articles(self, url, limit=5):
        """
        Scrape articles from URL
        Returns list of {title, link, summary}
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Generic scraping (works for most news sites)
            for article in soup.find_all('article', limit=limit):
                try:
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href')
                        
                        # Make absolute URL
                        if link and not link.startswith('http'):
                            from urllib.parse import urljoin
                            link = urljoin(url, link)
                        
                        articles.append({
                            'title': title,
                            'link': link,
                            'source': url
                        })
                except:
                    continue
                    
            return articles
        except Exception as e:
            self.logger.error(f"Scrape error for {url}: {e}")
            return []
    
    def get_daily_digest(self, sources=None):
        """
        Get news digest from all sources
        """
        if sources is None:
            sources = self.news_sources
            
        all_articles = []
        for source in sources:
            articles = self.scrape_articles(source, limit=3)
            all_articles.extend(articles)
        
        return all_articles
    
    def summarize_article(self, url):
        """
        Fetch article and summarize with AI
        """
        try:
            from llm_brain import GeminiBrain
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article text
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs[:10]])
            
            if not article_text:
                return "Maqola matnini olishda xatolik"
            
            brain = GeminiBrain()
            summary = brain.generate_response(f"Ushbu maqolani qisqacha xulosalang:\\n\\n{article_text[:2000]}")
            
            return summary
        except Exception as e:
            self.logger.error(f"Summarize error: {e}")
            return "Xulosalashda xatolik"

if __name__ == "__main__":
    bot = NewsBot()
    digest = bot.get_daily_digest()
    print(f"Found {len(digest)} articles")
