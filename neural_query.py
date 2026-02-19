"""
JARVIS - Neural Query & RAG Engine (Elite v15.0)
Allows searching through local files and documents using semantic meaning.
"""
import os
import re
from pathlib import Path
from llm_brain import GeminiBrain

class NeuralQueryEngine:
    def __init__(self, brain=None, hub_path="C:/JARVIS_HUB"):
        self.brain = brain if brain else GeminiBrain()
        self.hub_path = Path(hub_path)
        self.max_tokens_per_file = 2000
        
    def search(self, query, project_filter=None):
        """
        Search for files related to a query using semantic context.
        """
        results = []
        search_path = self.hub_path / project_filter if project_filter else self.hub_path
        
        if not search_path.exists():
            return f"Hub path {search_path} does not exist."
            
        # 1. Collect potential files (limiting to text/code for RAG)
        potential_files = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.js', '.html', '.json')):
                    potential_files.append(Path(root) / file)
        
        if not potential_files:
            return "No relevant documents found in the hub."

        # 2. Smart Ranking (Ask AI which files are most relevant based on names)
        file_list_str = "\n".join([str(f.relative_to(self.hub_path)) for f in potential_files[:50]]) # Limit to first 50 for selection
        
        selection_prompt = f"""
        User is searching for: "{query}"
        Here is a list of local files:
        {file_list_str}
        
        Identify the top 3 files (absolute paths) that are most likely to contain the answer.
        Return ONLY the file paths, one per line. If none are relevant, return 'NONE'.
        """
        
        selected_files_raw = self.brain.generate_response(selection_prompt)
        if not selected_files_raw or "NONE" in selected_files_raw:
            return "I couldn't find any documents matching that specific semantic query."

        selected_files = [f.strip() for f in selected_files_raw.split('\n') if f.strip() and '/' in f or '\\' in f]
        
        # 3. RAG Step: Analyze contents of selected files
        context_snippets = []
        for file_rel_path in selected_files:
            full_path = self.hub_path / file_rel_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(self.max_tokens_per_file)
                        context_snippets.append(f"--- FILE: {file_rel_path} ---\n{content}")
                except: continue

        if not context_snippets:
            return "Found files but couldn't read their contents."

        # 4. Final Answer Generation
        final_prompt = f"""
        You are JARVIS Search Engine. Use the following file contexts to answer the user query.
        
        USER QUERY: "{query}"
        
        CONTEXT FROM LOCAL FILES:
        {" ".join(context_snippets)}
        
        Provide a concise answer based ONLY on the provided local data. If the information isn't there, say you don't know based on local files.
        """
        
        return self.brain.generate_response(final_prompt)

if __name__ == "__main__":
    nq = NeuralQueryEngine()
    print(nq.search("How do the HUD animations work?"))
