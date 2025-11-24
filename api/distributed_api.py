import socket
import json
import threading

class DistributedAPI:
    def __init__(self, node_id, discovery, port=5001):
        self.node_id = node_id
        self.discovery = discovery
        self.port = port
        self.handlers = {}
        self.running = False

    def register_handler(self, msg_type, handler_func):
        self.handlers[msg_type] = handler_func

    def send_message(self, target_node_id, msg_type, data):
        peers = self.discovery.get_peers()
        if target_node_id not in peers:
            return None
            
        target_ip = peers[target_node_id]['ip']
        msg = {'from': self.node_id, 'type': msg_type, 'data': data}
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target_ip, self.port))
                s.send(json.dumps(msg).encode())
                response = s.recv(4096)
                return json.loads(response.decode())
        except Exception as e:
            print(f"[API Error] Send to {target_node_id}: {e}")
            return None

    def _listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        while self.running:
            try:
                client, _ = server.accept()
                data = client.recv(4096)
                if not data: continue
                
                msg = json.loads(data.decode())
                response = {'status': 'error', 'msg': 'unknown type'}
                
                if msg['type'] in self.handlers:
                    result = self.handlers[msg['type']](msg['data'])
                    response = {'status': 'ok', 'result': result}
                
                client.send(json.dumps(response).encode())
                client.close()
            except Exception:
                pass

    def start(self):
        self.running = True
        threading.Thread(target=self._listen, daemon=True).start()

    def stop(self):
        self.running = False
