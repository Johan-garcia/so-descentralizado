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
        
        # LISTA DE IPs CONOCIDAS DEL CLUSTER
        # AWS no permite Broadcast, así que debemos apuntar directo.
        # Asegúrate de que estas sean las IPs PRIVADAS correctas de tus 3 nodos
        self.known_nodes = [
            '10.0.1.10', 
            '10.0.1.11', 
            '10.0.1.12',
            '10.0.1.226' # Agrego la tuya que vi en el log por si acaso
        ]
        
    def broadcast_presence(self):
        # Ahora usamos Unicast (TCP/UDP directo) en lugar de Broadcast
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        msg = {'type': 'HELLO', 'id': self.node_id, 'ip': self.ip, 'ts': time.time()}
        
        while self.running:
            for target_ip in self.known_nodes:
                # No enviarse a sí mismo
                if target_ip == self.ip:
                    continue
                    
                try:
                    # Enviar saludo directo a la IP
                    sock.sendto(json.dumps(msg).encode(), (target_ip, self.port))
                except Exception as e:
                    pass # Es normal si un nodo está apagado
            
            time.sleep(2) # Saludar cada 2 segundos

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                
                if msg['type'] == 'HELLO' and msg['id'] != self.node_id:
                    # Guardamos al amigo encontrado
                    self.peers[msg['id']] = {'ip': msg['ip'], 'last_seen': time.time()}
                    # print(f"[NET] Vi a {msg['id']} en {msg['ip']}") # Debug opcional
            except: pass

    def start(self):
        self.running = True
        threading.Thread(target=self.broadcast_presence, daemon=True).start()
        threading.Thread(target=self.listen, daemon=True).start()

    def stop(self): self.running = False
    
    def get_peers(self):
        now = time.time()
        # Filtrar nodos que no hemos visto en los últimos 10 segundos
        active_peers = {k:v for k,v in self.peers.items() if now - v['last_seen'] < 10}
        return active_peers
