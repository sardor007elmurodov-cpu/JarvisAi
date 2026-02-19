---
description: JARVIS-ni VPS serverga o'rnatish va Gibrid rejimga o'tkazish
---
# JARVIS VPS Deployment Workflow

Ushbu qo'llanma JARVIS tizimini VPS serverga o'rnatish va mahalliy kompyuterni (PC) masofadan boshqarishni sozlaydi.

## 1. Tayyorgarlik (VPS tarafida)
1. VPS serveringizga (Ubuntu/Linux tavsiya etiladi) kiring.
2. Python 3.10+ o'rnating: `sudo apt update && sudo apt install python3-pip python3-venv git -y`
3. Loyihani klonlang yoki fayllarni yuklang.
4. Virtual muhit yarating: `python3 -m venv venv && source venv/bin/activate`
5. Kutubxonalarni o'rnating: `pip install -r requirements.txt` (Ogohlantirish: Linuxda GUI kutubxonalari xato berishi mumkin, bu normal holat).

## 2. Serverni ishga tushirish (Brain & Telegram)
1. `.env` faylini VPS-da yarating va API keylarni kiriting.
2. VPS-da JARVIS "Miyya" rejimini ishga tushiring:
   ```bash
   python vps_agent.py
   ```
   Bu rejimda JARVIS Telegram bot orqali ishlaydi va tadqiqotlarni (Research) serverning o'zida bajaradi.

## 3. Mahalliy PC-ni ulaymiz (Client Mode)
1. O'zingizni kompyuteringizda (PC) `cloud_bridge_client.py` ni oching.
2. `CLOUD_SERVER_URL` qatoriga VPS IP manzilingizni yozing (masalan: `http://95.217.xx.xx:5000`).
3. PC-da ko'p resurs yeydigan HUD-ni yopib, faqat ko'prikni ishga tushiring:
   ```powershell
   python cloud_bridge_client.py
   ```

## 4. Tekshirish
Telegram botga "/research AI kelajagi" deb yozing. 
1. **VPS** qidiruvni bajaradi va hisobotni shakllantiradi.
2. **VPS** hisobotni PC-ga "Command" sifatida yuboradi.
3. **PC** dagi client buyruqni qabul qiladi va Word faylini yaratadi.

// turbo
## 5. Autostart sozlash (Linux VPS)
Server o'chib qolsa ham o'zi yonishi uchun:
`pm2 start vps_agent.py --interpreter python3`
