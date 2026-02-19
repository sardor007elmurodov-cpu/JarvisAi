"""
JARVIS - Cloud Relay Server
Foydalanuvchi: Ushbu kodni 'Render' yoki 'PythonAnywhere' kabi bepul hostingga joylashtiring.
Vazifasi: Noutbuk o'chiq bo'lganda ham buyruqlarni qabul qilish.

Noutbukni yoqish (Wake-on-LAN) uchun:
1. Bu server "Wake Up" buyrug'ini oladi.
2. Uy tarmog'idagi BOShQA qurilma (masalan, telefondagi ilova yoki ESP32) bu buyruqni o'qiydi.
3. O'sha qurilma noutbukka "Magic Packet" yuboradi.

Eslatma: Bulutdan to'g'ridan-to'g'ri uydagi o'chiq kompyuterni yoqib bo'lmaydi (NAT/Firewall tufayli).
Shuning uchun o'rtada "Bridge" kerak.
"""
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Buyruqlar navbati
PENDING_COMMANDS = []

@app.route('/')
def home():
    return "JARVIS Cloud Relay is Running. Use /send to send commands."

@app.route('/send', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('command')
    if cmd:
        PENDING_COMMANDS.append(cmd)
        return jsonify({"status": "queued", "command": cmd})
    return jsonify({"error": "No command provided"}), 400

@app.route('/get', methods=['GET'])
def get_commands():
    # Uy tarmog'idagi "Bridge" bu yerdan o'qiydi
    if PENDING_COMMANDS:
        cmd = PENDING_COMMANDS.pop(0)
        return jsonify({"command": cmd})
    return jsonify({"command": None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
