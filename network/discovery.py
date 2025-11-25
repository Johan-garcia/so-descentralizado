import socket
import json
import threading
import time

class NodeDiscovery:
    def __init__(self, node_id, port=5000):
        self.node_id = node_id
        self.port = port
        self.peers = {}
        self.running = False
        
        # 1. DETECTAR MI IP REAL (CRÍTICO PARA QUE FUNCIONE EN AWS)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.my_ip = s.getsockname()[0]
            s.close()
        except:
            self.my_ip = '127.0.0.1'
            
        print(f" [NET] 🌍 Mi IP pública es: {self.my_ip} (Ya no soy 127.0.0.1)")

        # 2. LISTA DE AMIGOS (Tus IPs reales)
        self.known_nodes = [
            '10.0.1.226', 
            '10.0.1.41', 
            '10.0.1.126'
        ]
        
    def broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = {'type': 'HELLO', 'id': self.node_id, 'ip': self.my_ip}
        
        while self.running:
            for target_ip in self.known_nodes:
                if target_ip == self.my_ip: continue
                try:
                    sock.sendto(json.dumps(msg).encode(), (target_ip, self.port))
                except: pass
            time.sleep(2)

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
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
