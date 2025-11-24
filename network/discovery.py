import socket
import json
import threading
import time

class NodeDiscovery:
    def __init__(self, node_id, ip, port=5000):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.peers = {}
        self.running = False
        
    def broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Mensaje de "Hola"
        msg = {'type': 'HELLO', 'id': self.node_id, 'ip': self.ip, 'ts': time.time()}
        # IP Broadcast de la subnet de AWS (10.0.1.0/24 -> 10.0.1.255)
        target = '10.0.1.255'
        
        while self.running:
            try:
                sock.sendto(json.dumps(msg).encode(), (target, self.port))
                time.sleep(5)
            except Exception as e:
                print(f"[NET] Broadcast Error: {e}")
                time.sleep(5)

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        while self.running:
            try:
                data, _ = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                if msg['type'] == 'HELLO' and msg['id'] != self.node_id:
                    self.peers[msg['id']] = {'ip': msg['ip'], 'last_seen': time.time()}
            except: pass

    def start(self):
        self.running = True
        threading.Thread(target=self.broadcast_presence, daemon=True).start()
        threading.Thread(target=self.listen, daemon=True).start()

    def stop(self): self.running = False
    
    def get_peers(self):
        now = time.time()
        return {k:v for k,v in self.peers.items() if now - v['last_seen'] < 15}
