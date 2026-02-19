import asyncio
import threading
from bleak import BleakScanner
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import logging

class ConnectivityManager:
    """
    JARVIS - Connectivity Module
    Handles Bluetooth management and Remote Bridge for multiple devices.
    """
    
    def __init__(self, core=None):
        self.core = core
        self.bridge_running = False
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        
        # Suppress Flask logging for clean HUD
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def _setup_routes(self):
        @self.app.route('/command', methods=['POST'])
        def remote_command():
            data = request.json
            cmd = data.get("command")
            if cmd and self.core:
                # Execute command via JARVIS Core
                self.core.process_command(cmd)
                return jsonify({"status": "success", "message": f"Command '{cmd}' received."})
            return jsonify({"status": "error", "message": "Invalid command."}), 400

        @self.app.route('/status', methods=['GET'])
        def status():
            return jsonify({
                "status": "online",
                "identity": "JARVIS PRIME",
                "system": socket.gethostname()
            })

    async def _scan_bluetooth(self):
        """Scan for nearby Bluetooth devices"""
        try:
            print("📡 Scanning for Bluetooth devices...")
            devices = await BleakScanner.discover()
            return [{"name": d.name or "Unknown", "address": d.address} for d in devices]
        except Exception as e:
            return f"Bluetooth scan error: {str(e)}"

    def get_bluetooth_devices(self):
        """Synchronous wrapper for BT scan"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._scan_bluetooth())
        loop.close()
        return result

    def start_remote_bridge(self, port=5000):
        """Start the JARVIS Remote Bridge in a background thread"""
        if self.bridge_running:
            return "Remote Bridge is already active."
            
        def run_flask():
            self.bridge_running = True
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"🌐 JARVIS Remote Bridge active at http://{local_ip}:{port}")
            self.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

        threading.Thread(target=run_flask, daemon=True).start()
        return "Remote Bridge started successfully."

if __name__ == "__main__":
    # Test
    cm = ConnectivityManager()
    devices = cm.get_bluetooth_devices()
    print("Found devices:", devices)
