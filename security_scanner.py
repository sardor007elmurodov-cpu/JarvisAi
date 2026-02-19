"""
JARVIS - Security Scanner (Phase 4)
Real-time system security monitoring
"""

import psutil
import time
import threading
from datetime import datetime

class SecurityScanner:
    """
    Monitors system processes and network connections for suspicious activity
    """
    
    def __init__(self, alert_callback=None, face_auth=None):
        self.alert_callback = alert_callback
        self.face_auth = face_auth
        self.running = False
        self.thread = None
        self.last_face_check = 0
        
        # Suspicious process patterns
        self.suspicious_keywords = [
            "hack", "crack", "trojan", "virus", "malware", "keylog",
            "backdoor", "rootkit", "exploit", "inject"
        ]
        
        # CPU/Memory thresholds
        self.cpu_threshold = 90  # %
        self.memory_threshold = 85  # %
        
    def start(self):
        """Start background security monitoring"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print("✅ Security Scanner: Active")
    
    def stop(self):
        """Stop security monitoring"""
        self.running = False
        print("⚠️ Security Scanner: Deactivated")
    
    def _alert(self, level, message):
        """Send security alert"""
        if self.alert_callback:
            self.alert_callback(level, message)
        else:
            print(f"🛡️ [{level}] {message}")
            
    def set_vision_engine(self, face_auth):
        """Set the face authentication engine for sentinel monitoring"""
        self.face_auth = face_auth

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # 1. Check for suspicious processes
                self._scan_processes()
                
                # 2. Check system resources
                self._check_resources()
                
                # 3. Check network (basic)
                self._check_network()
                
                # 4. Sentinel Vision Check (Elite v16.0)
                # Note: Actual camera frame must be passed from executor/main
                
            except Exception as e:
                print(f"Security Scanner Error: {e}")
            
            time.sleep(10)  # Tighter check for v16.0 (10s)

    def process_vision_frame(self, frame):
        """Analyze a frame for security threats (Sentinel Mode)"""
        if not self.face_auth or time.time() - self.last_face_check < 5:
            return

        self.last_face_check = time.time()
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_auth.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 1:
            self._alert("CRITICAL", f"Tizim atrofida bir nechta shaxs aniqlandi ({len(faces)} kishi). Maxfiylik xavf ostida.")
        elif len(faces) == 1:
            is_master, conf = self.face_auth.identify_with_faces(frame, faces)
            if not is_master:
                self._alert("WARNING", "Notanish shaxs aniqlandi. Maxfiylik qalqoni ishga tushirildi.")

    
    def _scan_processes(self):
        """Scan running processes for suspicious names"""
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Check against suspicious keywords
                for keyword in self.suspicious_keywords:
                    if keyword in proc_name:
                        self._alert(
                            "CRITICAL",
                            f"Shubhali jarayon topildi: {proc.info['name']} (PID: {proc.pid})"
                        )
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def _check_resources(self):
        """Monitor CPU and Memory usage"""
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        
        if cpu > self.cpu_threshold:
            self._alert("WARNING", f"CPU yuqori: {cpu}%")
        
        if mem > self.memory_threshold:
            self._alert("WARNING", f"Xotira yuqori: {mem}%")
    
    def _check_network(self):
        """Basic network connection monitoring"""
        try:
            connections = psutil.net_connections(kind='inet')
            external_count = sum(1 for conn in connections if conn.status == 'ESTABLISHED')
            
            # Alert if too many external connections (possible data exfiltration)
            if external_count > 50:
                self._alert("INFO", f"Ko'p tarmoq ulanshlari: {external_count}")
        except (psutil.AccessDenied, AttributeError):
            pass  # Requires admin privileges
    
    def get_status_report(self):
        """Get current system status"""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            return {
                "cpu": cpu,
                "memory": mem,
                "disk": disk,
                "processes": len(psutil.pids()),
                "status": "SECURE" if cpu < 80 and mem < 80 else "ALERT"
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    def alert_handler(level, msg):
        print(f"[{datetime.now()}] {level}: {msg}")
    
    scanner = SecurityScanner(alert_callback=alert_handler)
    scanner.start()
    
    print("Security Scanner running... (Press Ctrl+C to stop)")
    try:
        while True:
            time.sleep(5)
            status = scanner.get_status_report()
            print(f"Status: {status}")
    except KeyboardInterrupt:
        scanner.stop()
