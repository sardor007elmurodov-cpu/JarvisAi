import os
import glob
from datetime import datetime, timedelta
from pathlib import Path
from fuzzywuzzy import fuzz
from utils import setup_logger

class SmartFileSearch:
    """
    JARVIS Smart File Search - AI-powered file discovery
    Uses natural language queries to find files across the system.
    """
    def __init__(self):
        self.logger = setup_logger("SmartFileSearch")
        self.common_locations = [
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~\\Videos"),
        ]
        
    def search_by_date(self, query, days_ago=30, file_type=None):
        """
        Search files modified within a date range
        Args:
            query: Search term
            days_ago: Number of days to look back
            file_type: File extension filter (e.g., 'pdf', 'docx')
        """
        results = []
        cutoff_date = datetime.now() - timedelta(days=days_ago)
        
        for location in self.common_locations:
            if not os.path.exists(location):
                continue
                
            pattern = f"**/*.{file_type}" if file_type else "**/*"
            
            try:
                for file_path in Path(location).glob(pattern):
                    if not file_path.is_file():
                        continue
                        
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if mod_time >= cutoff_date:
                        # Fuzzy match on filename
                        filename = file_path.stem
                        if query.lower() in filename.lower() or fuzz.partial_ratio(query.lower(), filename.lower()) > 60:
                            results.append({
                                "path": str(file_path),
                                "name": file_path.name,
                                "modified": mod_time.strftime("%Y-%m-%d %H:%M"),
                                "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
                            })
            except Exception as e:
                self.logger.warning(f"Error searching {location}: {e}")
                
        return results
    
    def search_by_content(self, query, file_types=['txt', 'md', 'py', 'log']):
        """
        Search within file contents (text files only)
        Args:
            query: Text to search for
            file_types: List of file extensions to search
        """
        results = []
        
        for location in self.common_locations:
            if not os.path.exists(location):
                continue
                
            for ext in file_types:
                try:
                    for file_path in Path(location).glob(f"**/*.{ext}"):
                        if not file_path.is_file():
                            continue
                            
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    # Find line number
                                    lines = content.split('\\n')
                                    line_nums = [i+1 for i, line in enumerate(lines) if query.lower() in line.lower()]
                                    
                                    results.append({
                                        "path": str(file_path),
                                        "name": file_path.name,
                                        "matches": len(line_nums),
                                        "lines": line_nums[:5]  # First 5 matches
                                    })
                        except:
                            pass
                except Exception as e:
                    self.logger.warning(f"Error searching contents in {location}: {e}")
                    
        return results
    
    def fuzzy_file_search(self, query, threshold=70):
        """
        Find files with similar names using fuzzy matching
        Args:
            query: Filename to search for
            threshold: Minimum similarity score (0-100)
        """
        results = []
        
        for location in self.common_locations:
            if not os.path.exists(location):
                continue
                
            try:
                for file_path in Path(location).glob("**/*"):
                    if not file_path.is_file():
                        continue
                        
                    filename = file_path.stem
                    score = fuzz.partial_ratio(query.lower(), filename.lower())
                    
                    if score >= threshold:
                        results.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "similarity": score,
                            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
                        })
            except Exception as e:
                self.logger.warning(f"Error fuzzy searching {location}: {e}")
                
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:20]  # Top 20 results
    
    def quick_find(self, query):
        """
        Smart combined search - tries all methods and returns best results
        """
        self.logger.info(f"Quick find: {query}")
        
        # Try exact name match first
        exact_results = self.fuzzy_file_search(query, threshold=90)
        if exact_results:
            return exact_results[:5]
            
        # Try content search for common text files
        content_results = self.search_by_content(query)
        if content_results:
            return content_results[:5]
            
        # Fall back to fuzzy search
        fuzzy_results = self.fuzzy_file_search(query, threshold=60)
        return fuzzy_results[:5]

if __name__ == "__main__":
    # Test
    search = SmartFileSearch()
    results = search.quick_find("test")
    for r in results:
        print(r)
