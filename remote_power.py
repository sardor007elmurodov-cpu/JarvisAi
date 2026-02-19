"""
JARVIS - Remote Power (Uzoqdan Yoqish)
Wake-on-LAN (WoL) texnologiyasi orqali kompyuterni yoqish.

DIQQAT: Bu skriptni BOSHQA qurilmadan (masalan, telefondan) ishlatish kerak.
Chunki o'chiq kompyuter o'zini o'zi yoqa olmaydi.
"""
import socket
import struct

def wake_on_lan(mac_address):
    """Magic Packet yuborish"""
    # MAC manzil formatini to'g'irlash (AA:BB:CC...)
    if len(mac_address) == 12:
        pass
    elif len(mac_address) == 17:
        sep = mac_address[2]
        mac_address = mac_address.replace(sep, '')
    else:
        raise ValueError("Noto'g'ri MAC manzil formati")

    # Magic Packet tuzilishi: 6 ta 0xFF, keyin 16 marta MAC manzil
    data = b'\xFF' * 6 + (bytes.fromhex(mac_address) * 16)
    
    # Broadcast orqali yuborish
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data, ('<broadcast>', 9))
    print(f"Magic Packet yuborildi: {mac_address}")

# O'zingizning MAC manzilingizni shu yerga yozing
# Aniqlash uchun cmd: 'getmac' yoki 'ipconfig /all'
TARGET_MAC = "00-00-00-00-00-00" 

if __name__ == "__main__":
    wake_on_lan(TARGET_MAC)
