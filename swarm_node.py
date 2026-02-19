"""
JARVIS - Swarm Mode (Ko'p Qurilmalik Rejim)
Bir nechta JARVIS nusxalarini bitta tarmoqqa ulash.
- UDP Discovery: Boshqa agentlarni avtomatik topish.
- TCP Communication: Buyruq va ma'lumot almashish.
"""
import socket
import threading
import time
import json
from utils import setup_logger

class SwarmNode:
    def __init__(self, port=5005):
        self.logger = setup_logger("SwarmNode")
        self.port = port
        self.nodes = {} # {ip: {"hostname": "name", "last_seen": time}}
        self.running = False

    def start_node(self):
        """Swarm rejimini ishga tushirish"""
        self.running = True
        
        # 1. TCP Server (Buyruqlarni qabul qilish)
        threading.Thread(target=self._tcp_server, daemon=True).start()
        
        # 2. UDP Listener (Discovery uchun)
        threading.Thread(target=self._udp_listener, daemon=True).start()
        
        self.logger.info(f"Swarm Node started on port {self.port}")
        return "Swarm rejimi ishga tushirildi. Tarmoq kuzatilmoqda."

    def stop_node(self):
        self.running = False

    def scan_network(self):
        """Tarmoqdagi boshqa JARVISlarni qidirish (Broadcast)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            message = json.dumps({"type": "DISCOVERY", "hostname": socket.gethostname()})
            sock.sendto(message.encode(), ('<broadcast>', self.port))
            
            return "Tarmoqqa qidiruv signali yuborildi."
        except Exception as e:
            return f"Qidiruv xatosi: {e}"

    def send_command(self, target_ip, command):
        """Boshqa JARVISga buyruq yuborish"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, self.port))
            
            data = json.dumps({"type": "COMMAND", "cmd": command})
            sock.send(data.encode())
            sock.close()
            return f"Buyruq yuborildi: {target_ip}"
        except Exception as e:
            return f"Yuborish xatosi: {e}"

    def get_nodes(self):
        """Topilgan qurilmalar ro'yxati"""
        active_nodes = []
        current_time = time.time()
        
        for ip, info in list(self.nodes.items()):
            if current_time - info['last_seen'] < 60: # 1 daqiqa faollik
                active_nodes.append(f"{ip} ({info['hostname']})")
                
        if not active_nodes:
            return "Hozircha boshqa qurilmalar topilmadi."
        return "Tarmoqdagi JARVISlar:\n" + "\n".join(active_nodes)

    def _tcp_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        while self.running:
            client, addr = server.accept()
            try:
                data = client.recv(1024).decode()
                msg = json.loads(data)
                
                if msg['type'] == 'COMMAND':
                    self.logger.info(f"Swarm Command from {addr}: {msg['cmd']}")
                    # Bu yerda buyruqni bajarish logikasi bo'lishi kerak
                    # Hozircha faylga yozib qo'yamiz (Web remote kabi)
                    with open("data/remote_command.txt", "w") as f:
                        f.write(msg['cmd'])
            except: pass
            client.close()

    def _udp_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        
        while self.running:
            data, addr = sock.recvfrom(1024)
            try:
                msg = json.loads(data.decode())
                if msg['type'] == 'DISCOVERY':
                    if addr[0] != self._get_local_ip():
                        self.nodes[addr[0]] = {"hostname": msg['hostname'], "last_seen": time.time()}
                        
                        # Biz ham javob qaytarishimiz kerak (Presence)
                        # Lekin loop bo'lmasligi uchun oddiyroq usul qilamiz
            except: pass

    def _get_local_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except: return "127.0.0.1"

if __name__ == "__main__":
    node = SwarmNode()
    node.start_node()
    node.scan_network()
    while True: time.sleep(1)
