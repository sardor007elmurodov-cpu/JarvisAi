import os

def cleanup_parser():
    path = "parser.py"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # We want to keep:
    # 1. Lines 1 to 534 (Imports, Class start, parse, _detect_action, _extract_parameters, and some helpers)
    # 2. Then we want to append the unique methods that were duplicated or messy.
    
    clean_lines = lines[:534] # Keep up to _extract_typed_text end
    
    # Add the clean helpers (re-implemented or pulled from the end correctly)
    clean_helpers = """
    def _extract_key(self, text):
        \"\"\"Tugma nomini extract qilish\"\"\"
        key_map = {
            "enter": "enter", "probel": "space", "space": "space",
            "backspace": "backspace", "delete": "delete",
            "esc": "esc", "escape": "escape", "tab": "tab",
            "alt": "alt", "ctrl": "ctrl", "shift": "shift", "win": "win"
        }
        for key_name, key_code in key_map.items():
            if key_name in text:
                return key_code
        words = text.split()
        return words[-1] if words else "enter"

    def _extract_hotkey(self, text):
        \"\"\"Hotkey kombinatsiyasini extract qilish\"\"\"
        keys = []
        if "ctrl" in text: keys.append("ctrl")
        if "alt" in text: keys.append("alt")
        if "shift" in text: keys.append("shift")
        if "win" in text: keys.append("win")
        words = text.split()
        if words:
            main_key = words[-1]
            if main_key not in keys:
                keys.append(main_key)
        return keys if keys else None

    def _extract_coordinates(self, text):
        \"\"\"Koordinatalarni extract qilish (x, y)\"\"\"
        numbers = re.findall(r'\\d+', text)
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        return 0, 0

    def _extract_mouse_button(self, text):
        \"\"\"Sichqoncha tugmasini aniqlash\"\"\"
        if "o'ng" in text or "right" in text: return "right"
        if "o'rta" in text or "middle" in text: return "middle"
        return "left"

    def _extract_scroll_amount(self, text):
        \"\"\"Scroll miqdorini extract qilish\"\"\"
        numbers = re.findall(r'-?\\d+', text)
        if numbers:
            amount = int(numbers[0])
            if "past" in text or "down" in text: return -abs(amount)
            return abs(amount)
        return 300

    def _extract_telegram_params(self, text):
        \"\"\"Telegram uchun kontakt va xabarni ajratish\"\"\"
        clean = text
        for p in UZ_PATTERNS.get("send_telegram_message", []):
            clean = clean.replace(p, "").strip()
        parts = clean.split("ga ", 1)
        if len(parts) == 2:
            contact = parts[0].strip().title()
            message = parts[1].replace("deb yoz", "").replace("yoz", "").strip()
            return contact, message
        return "Unknown", clean

    def _extract_time(self, text):
        \"\"\"HH:MM formatidagi vaqtni ajratish\"\"\"
        match = re.search(r'(\\d{1,2})[:\\s-](\\d{2})', text)
        if match:
            h, m = match.groups()
            return f"{int(h):02d}:{int(m):02d}"
        return "09:00"

    def _extract_duration(self, text):
        \"\"\"Daqiqalarni ajratish\"\"\"
        nums = re.findall(r'\\d+', text)
        if nums:
            val = int(nums[0])
            if "soat" in text or "hour" in text: return val * 60
            return val
        return 1

    def _extract_automation_action(self, text, keywords):
        \"\"\"Avtomatizatsiya ichidagi asosiy buyruqni ajratish\"\"\"
        clean = text
        for k in keywords:
            if k in clean:
                parts = clean.split(k)
                clean = parts[-1].strip()
        return clean

if __name__ == "__main__":
    # Test
    parser = CommandParser()
    test_commands = ["Chrome och", "YouTube och", "Google'da Python qidir", "Enter bos", "Kompyuterni o'chir"]
    for cmd in test_commands:
        result = parser.parse(cmd)
        print(f"{cmd} -> {result}")
"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)
        f.write(clean_helpers)

if __name__ == "__main__":
    cleanup_parser()
    print("Cleanup done.")
