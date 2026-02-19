"""
JARVIS - Web Remote Control Server
Flask asosida ishlaydigan lokal veb-server.
Telefondan boshqarish uchun interfeys.
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
import os
import config

app = Flask(__name__)
app.secret_key = config.WEB_SETTINGS["secret_key"]

COMMAND_FILE = os.path.join(os.getcwd(), "data", "remote_command.txt")
os.makedirs(os.path.dirname(COMMAND_FILE), exist_ok=True)

def is_logged_in():
    return session.get('logged_in')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == config.WEB_SETTINGS["password"]:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Noto'g'ri parol!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    if not is_logged_in():
        return jsonify({"status": "error", "message": "Avtorizatsiya talab qilinadi"}), 401
        
    data = request.json
    command = data.get('command')
    
    if command:
        try:
            with open(COMMAND_FILE, "w", encoding="utf-8") as f:
                f.write(command)
            return jsonify({"status": "success", "message": f"Buyruq yuborildi: {command}"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "error", "message": "Buyruq topilmadi"}), 400

import psutil
import time

@app.route('/status')
def get_status():
    if not is_logged_in():
        return jsonify({"status": "error"}), 401
    
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    # Get last notification/log if possible
    log_file = os.path.join(os.getcwd(), "logs", "jarvis_main.log")
    last_log = "Tizim onlayn..."
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()
                if lines:
                    last_log = lines[-1].strip()
    except: pass

    return jsonify({
        "status": "success",
        "cpu": cpu,
        "ram": ram,
        "last_log": last_log,
        "timestamp": time.strftime("%H:%M:%S")
    })


# --- CAMERA STREAMING ---
import cv2

camera = None

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def gen_frames():  
    while True:
        try:
            cam = get_camera()
            success, frame = cam.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if not is_logged_in(): return "Auth Required", 401
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- MOBILE ENDPOINTS ---

@app.route('/speak', methods=['POST'])
def remote_speak():
    if not is_logged_in(): return jsonify({"status":"error"}), 401
    text = request.json.get('text')
    if text:
        # Use execute mechanism
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            f.write(f"ovozida ayt {text}")
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/typer', methods=['POST'])
def remote_typer():
    if not is_logged_in(): return jsonify({"status":"error"}), 401
    text = request.json.get('text')
    if text:
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            f.write(f"write_in_app text='{text}'") # Direct execution
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/mood_status')
def mood_status():
    if not is_logged_in(): return jsonify({"status":"error"}), 401
    # Mock mood for now or read from a status file
    return jsonify({"mood": "NEUTRAL", "color": "#00e0ff"})

if __name__ == '__main__':
    host = config.WEB_SETTINGS.get('host', '0.0.0.0')
    port = config.WEB_SETTINGS.get('port', 5000)
    print(f"JARVIS Web Gateway: http://{host}:{port}")
    # Threaded=True for streaming
    app.run(host=host, port=port, debug=False, threaded=True)
