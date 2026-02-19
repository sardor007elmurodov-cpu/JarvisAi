"""
JARVIS Smart Media Player
Auto-download subtitles, intelligent volume, voice commands
"""
import os
from pathlib import Path
from utils import setup_logger

class SmartMediaPlayer:
    """
    Smart media controls with subtitle support and voice commands
    """
    def __init__(self):
        self.logger = setup_logger("SmartMediaPlayer")
        self.current_file = None
        self.current_position = 0
        
    def scan_media_library(self, folder):
        """
        Scan folder for media files
        Returns list of video/audio files
        """
        media_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.mp3', '.flac', '.wav']
        media_files = []
        
        try:
            for file_path in Path(folder).rglob('*'):
                if file_path.suffix.lower() in media_extensions:
                    media_files.append({
                        'path': str(file_path),
                        'name': file_path.stem,
                        'type': 'video' if file_path.suffix in ['.mp4', '.mkv', '.avi', '.mov'] else 'audio',
                        'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2)
                    })
        except Exception as e:
            self.logger.error(f"Scan error: {e}")
            
        return media_files
    
    def download_subtitles(self, video_path, language='eng'):
        """
        Auto-download subtitles for video
        Uses subliminal library
        """
        try:
            import subliminal
            
            video = subliminal.Video.fromname(video_path)
            subtitles = subliminal.download_best_subtitles([video], {subliminal.Language(language)})
            
            if video in subtitles and subtitles[video]:
                subtitle = subtitles[video][0]
                subliminal.save_subtitles(video, [subtitle])
                return f"Subtitles downloaded: {subtitle.language}"
            else:
                return "No subtitles found"
        except Exception as e:
            self.logger.error(f"Subtitle download error: {e}")
            return f"Error: {str(e)}"
    
    def seek_by_voice(self, offset_seconds):
        """
        Seek in current media by seconds
        Positive = forward, Negative = backward
        """
        try:
            import pyautogui
            
            if offset_seconds > 0:
                # Right arrow for forward
                times = abs(offset_seconds) // 5  # 5 seconds per press
                for _ in range(times):
                    pyautogui.press('right')
            else:
                # Left arrow for backward
                times = abs(offset_seconds) // 5
                for _ in range(times):
                    pyautogui.press('left')
                    
            return f"Seeked {offset_seconds} seconds"
        except Exception as e:
            self.logger.error(f"Seek error: {e}")
            return "Seek failed"
    
    def toggle_play_pause(self):
        """
        Toggle play/pause (works with most players)
        """
        try:
            import pyautogui
            pyautogui.press('space')
            return "Toggled play/pause"
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    player = SmartMediaPlayer()
    files = player.scan_media_library("C:\\Users\\user\\Videos")
    print(f"Found {len(files)} media files")
