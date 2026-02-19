
import os
import time
import subprocess
import pyautogui
import threading
try:
    import win32com.client
    OFFICE_COM_AVAILABLE = True
except ImportError:
    OFFICE_COM_AVAILABLE = False
from utils import setup_logger

class BackgroundAutomation:
    """
    JARVIS Professional Background Automation Worker.
    Uses COM for silent Office work and PyAutoGUI for UI-bound apps.
    """
    def __init__(self):
        self.logger = setup_logger("BackgroundAutomation")
        self.is_running = False
        
    def start_word_task(self, text, visible=False):
        """Word-da matn yozish (Silent COM mode)"""
        threading.Thread(target=self._word_com_logic, args=(text, visible), daemon=True).start()
        
    def start_excel_task(self, data_list, visible=False):
        """Excel-da jadval to'ldirish (Silent COM mode)"""
        threading.Thread(target=self._excel_com_logic, args=(data_list, visible), daemon=True).start()
        
    def start_pp_task(self, slides_data, visible=False):
        """PowerPoint-da prezentatsiya yaratish (Silent COM mode)"""
        threading.Thread(target=self._pp_com_logic, args=(slides_data, visible), daemon=True).start()
        
    def start_telegram_chat(self, contact, message):
        """Telegram-da xabar yuborish (UI Automation)"""
        threading.Thread(target=self._telegram_logic, args=(contact, message), daemon=True).start()

    def _word_com_logic(self, text, visible):
        self.logger.info("Word COM automation started.")
        if not OFFICE_COM_AVAILABLE:
            self.logger.error("win32com not available. Falling back to UI automation is not supported for silent mode.")
            return

        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = visible
            doc = word.Documents.Add()
            
            # Professional Header
            selection = word.Selection
            selection.Font.Bold = True
            selection.Font.Size = 14
            selection.TypeText("JARVIS AUTO-GENERATED REPORT\n")
            selection.Font.Bold = False
            selection.Font.Size = 11
            selection.TypeText(f"Sana: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Main Content
            selection.TypeText(text)
            
            # Save to Desktop
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop, f"JARVIS_Report_{int(time.time())}.docx")
            doc.SaveAs(file_path)
            doc.Close()
            word.Quit()
            self.logger.info(f"Word document saved to: {file_path}")
        except Exception as e:
            self.logger.error(f"Word COM Error: {e}")

    def _excel_com_logic(self, data_list, visible):
        self.logger.info("Excel COM automation started.")
        if not OFFICE_COM_AVAILABLE: return

        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = visible
            wb = excel.Workbooks.Add()
            ws = wb.ActiveSheet
            
            ws.Cells(1, 1).Value = "JARVIS Data Export"
            ws.Cells(1, 1).Font.Bold = True
            
            # Populate data (assuming data_list is list of lists or strings)
            for row_idx, data in enumerate(data_list, start=2):
                if isinstance(data, list):
                    for col_idx, value in enumerate(data, start=1):
                        ws.Cells(row_idx, col_idx).Value = value
                else:
                    ws.Cells(row_idx, 1).Value = data
            
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop, f"JARVIS_Data_{int(time.time())}.xlsx")
            wb.SaveAs(file_path)
            wb.Close()
            excel.Quit()
            self.logger.info(f"Excel file saved to: {file_path}")
        except Exception as e:
            self.logger.error(f"Excel COM Error: {e}")

    def _pp_com_logic(self, slides_data, visible):
        self.logger.info("PowerPoint COM automation started.")
        if not OFFICE_COM_AVAILABLE: return

        try:
            pp = win32com.client.Dispatch("PowerPoint.Application")
            presentation = pp.Presentations.Add(WithWindow=visible)
            
            # Populate slides (assuming slides_data is a list of dicts: {"title": "", "content": ""})
            for slide_info in slides_data:
                slide = presentation.Slides.Add(presentation.Slides.Count + 1, 1) # 1 = ppLayoutText
                slide.Shapes.Title.TextFrame.TextRange.Text = slide_info.get("title", "JARVIS Presentation")
                slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = slide_info.get("content", "")
            
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop, f"JARVIS_Pres_{int(time.time())}.pptx")
            presentation.SaveAs(file_path)
            presentation.Close()
            pp.Quit()
            self.logger.info(f"PowerPoint presentation saved to: {file_path}")
        except Exception as e:
            self.logger.error(f"PowerPoint COM Error: {e}")

    def _telegram_logic(self, contact, message):
        self.logger.info(f"Telegram automation for {contact} started.")
        try:
            # Activate Telegram (assuming it's running in background)
            pyautogui.hotkey('ctrl', 'alt', 't') 
            time.sleep(2)
            
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.write(contact)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Human-like message typing
            pyautogui.write(message, interval=0.03)
            time.sleep(0.5)
            pyautogui.press('enter')
            self.logger.info("Telegram message sent.")
        except Exception as e:
            self.logger.error(f"Telegram automation error: {e}")

if __name__ == "__main__":
    worker = BackgroundAutomation()
    print("Professional Background Automation Worker Online.")
