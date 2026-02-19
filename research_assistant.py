"""
JARVIS - Research Assistant
DuckDuckGo orqali qidiruv va Gemini orqali tahlil.
"""
import os
from duckduckgo_search import DDGS
import google.genai as genai
from datetime import datetime
from utils import setup_logger

class ResearchAssistant:
    def __init__(self):
        from config import GEMINI_API_KEY, AI_MODEL_NAME
        self.logger = setup_logger("ResearchAssistant")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = AI_MODEL_NAME
        
        # Tadqiqotlar papkasi
        self.research_dir = os.path.join(os.getcwd(), "research")
        if not os.path.exists(self.research_dir):
            os.makedirs(self.research_dir)

    def search_web(self, query, max_results=10):
        """Internetdan ma'lumot qidirish (Elite v22.0)"""
        try:
            results = []
            with DDGS() as ddgs:
                # Use news as well for better variety
                news = list(ddgs.news(query, max_results=3))
                for n in news:
                    results.append({
                        "title": f"[NEWS] {n['title']}",
                        "snippet": n['body'],
                        "link": n['href']
                    })
                
                # Standard text search
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r['title'],
                        "snippet": r['body'],
                        "link": r['href']
                    })
            return results
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []

    async def perform_research(self, topic, format="word", depth="standard"):
        """
        Mavzu bo'yicha tadqiqot o'tkazish.
        depth: 'standard' yoki 'deep' (chuqurlashtirilgan qidiruv)
        """
        self.logger.info(f"Researching topic: {topic} (Depth: {depth})")
        
        # 1. Birlamchi Qidiruv
        queries = [topic]
        if depth == "deep":
            # AI orqali mavzuni bo'laklarga bo'lish (Vast improvement)
            sub_prompt = f"""'{topic}' mavzusini chuqur, mukammal va har tomonlama o'rganish uchun 5 ta eng muhim professional qidiruv so'rovlarini (queries) o'zbek tilida yozing. 
            Ushbu so'rovlar mavzuning turli qirralarini (tarixi, texnologiyasi, kelajagi, muammolari va global ta'siri) qamrab olishi lozim.
            Faqat so'rovlarni o'zini vergul bilan ajratib qaytaring, boshqa hech narsa yozmang."""
            try:
                sub_res = self.client.models.generate_content(model=self.model_name, contents=sub_prompt)
                sub_queries = [q.strip() for q in sub_res.text.split(",") if q.strip()]
                queries.extend(sub_queries[:5])
                self.logger.info(f"Sub-queries generated: {sub_queries}")
            except Exception as e:
                self.logger.warning(f"Sub-query generation failed: {e}")
        
        all_results = []
        for q in queries:
            self.logger.info(f"Searching for: {q}...")
            # Increased results per query for deeper context
            search_count = 8 if depth == "deep" else 5
            all_results.extend(self.search_web(q, max_results=search_count))
            
        if not all_results:
            return "Kechirasiz, janob. Hech qanday ma'lumot topilmadi."

        # 2. Ma'lumotlarni saralash (Dublikatlarni o'chirish)
        seen_links = set()
        unique_results = []
        for r in all_results:
            if r['link'] not in seen_links:
                seen_links.add(r['link'])
                unique_results.append(r)
        
        # 3. Hisobot yaratish
        context = ""
        sources = []
        for i, r in enumerate(unique_results[:15], 1): # Max 15 sources
            context += f"[{i}] {r['title']}\nURL: {r['link']}\nINFO: {r['snippet']}\n\n"
            sources.append({"id": i, "title": r['title'], "url": r['link']})
        
        prompt = f"""
        Siz J.A.R.V.I.S Elite Research Engine'siz. 
        Mavzu: {topic}
        Turi: {'Chuqur tahlil' if depth == 'deep' else 'Standard hisobot'}

        KO'RSATMALAR:
        1. Professional, akademik va tushunarli tilda yozing.
        2. Ma'lumotlarni mantiqiy bo'limlarga ajrating (Abstract, Method, Analysis, Future Outlook, Conclusion).
        3. Har bir muhim fakt uchun [number] ko'rinishida manbaga tayaning.
        4. O'zbek tilida, professional JARVIS tonida yozing.

        MANBALAR:
        {context}
        """

        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            raw_result = response.text
            
            # 4. Hisobotni saqlash
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"research_{topic.replace(' ', '_')[:20]}_{timestamp}.md"
            filepath = os.path.join(self.research_dir, report_filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# RESEARCH REPORT: {topic}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(f"Depth: {depth}\n\n")
                f.write(raw_result)
                f.write("\n\n## BIBLIOGRAPHY\n")
                for s in sources:
                    f.write(f"[{s['id']}] {s['title']} - {s['url']}\n")

            # Word/PPT avtomatizatsiyasi
            from background_automation import BackgroundAutomation
            auto = BackgroundAutomation()
            
            if format == "word":
                auto.start_word_task(raw_result, visible=False)
                return f"✅ Hisobot tayyorlandi va Word-ga eksport qilindi: {report_filename}"
            elif format == "pp":
                # ... PPT logic ...
                return f"🎨 PowerPoint tayyorlanmoqda: {topic}"
                
            return f"✅ Tadqiqot yakunlandi. Fayl: {report_filename}\n\nQisqacha: " + raw_result[:300] + "..."
            
        except Exception as e:
            self.logger.error(f"Research Processing Error: {e}")
            return f"Xatolik: {e}"

if __name__ == "__main__":
    # Test
    ra = ResearchAssistant()
    import asyncio
    print("AI kelajagi haqida tadqiqot...")
    asyncio.run(ra.perform_research("Artificial Intelligence future trends 2026"))
