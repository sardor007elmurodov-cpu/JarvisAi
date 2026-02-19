"""
JARVIS - Vector Memory Core
Google Gemini Embeddings yordamida "cheksiz xotira" tizimi.
Matn va hujjatlarni vektor ko'rinishida saqlaydi va ma'no bo'yicha qidiradi.
"""
import json
import os
import numpy as np
import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import setup_logger

class MemoryCore:
    def __init__(self):
        self.logger = setup_logger("MemoryCore")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = "models/embedding-001"
        
        self.memory_file = os.path.join(os.getcwd(), "data", "vector_memory.json")
        self.memories = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert stored lists back to numpy arrays for calculation (optional/on-the-fly)
                    return data
            except Exception as e:
                self.logger.error(f"Memory load error: {e}")
        return []

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def get_embedding(self, text):
        """Matnni vektorga aylantirish"""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document",
                title="JARVIS Memory"
            )
            return result['embedding']
        except Exception as e:
            self.logger.error(f"Embedding error: {e}")
            return None

    def add_memory(self, text, source="User"):
        """Xotiraga ma'lumot qo'shish"""
        vector = self.get_embedding(text)
        if not vector:
            return "Xotiraga saqlashda xatolik (API Error)."
            
        memory_item = {
            "text": text,
            "vector": vector,
            "source": source,
            "timestamp": str(os.path.getmtime(self.memory_file)) if os.path.exists(self.memory_file) else "New"
        }
        
        self.memories.append(memory_item)
        self._save_memory()
        return "Ma'lumot xotiraga muvaffaqiyatli saqlandi."

    def search_memory(self, query, top_k=3):
        """Xotiradan qidirish (Cosine Similarity)"""
        if not self.memories:
            return []
            
        query_vector = self.get_embedding(query)
        if not query_vector:
            return []
            
        q_vec = np.array(query_vector)
        results = []
        
        for mem in self.memories:
            m_vec = np.array(mem["vector"])
            # Cosine Similarity Formula
            similarity = np.dot(q_vec, m_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(m_vec))
            results.append((similarity, mem))
            
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [r[1] for r in results[:top_k] if r[0] > 0.6] # Threshold 0.6

if __name__ == "__main__":
    mem = MemoryCore()
    # Test
    # print(mem.add_memory("Mening ismim Sardor va men dasturchiman."))
    res = mem.search_memory("Men kimmam?")
    for r in res:
        print(f"Topildi: {r['text']}")
