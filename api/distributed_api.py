import socket
import json
import threading
import os
from apps.ml_app import MLApp
from apps.monitor_app import MonitorApp
from apps.image_app import ImageApp

class DistributedAPI:
    def __init__(self, node_id, discovery, scheduler, port=5001):
        self.node_id = node_id
        self.discovery = discovery
        self.scheduler = scheduler
        self.port = port
        self.running = False
        self.my_ip = os.getenv('NODE_IP', '127.0.0.1')
        
        # Apps Locales
        self.ml_app = MLApp(node_id)
        self.monitor_app = MonitorApp(node_id)
        self.image_app = ImageApp(node_id)

    def forward_request(self, target_ip, msg):
        """Envía la tarea a otro nodo y espera su respuesta"""
        try:
            # Conectar con el nodo remoto (Puerto 5001 que es la API)
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.settimeout(5) # 5 segundos máximo de espera
            remote_socket.connect((target_ip, 5001))
            
            # Marcar mensaje como 'FORWARDED' para evitar bucles infinitos
            msg['is_forwarded'] = True
            
            remote_socket.send(json.dumps(msg).encode())
            response_data = remote_socket.recv(8192)
            remote_socket.close()
            
            return json.loads(response_data.decode())
        except Exception as e:
            print(f" [API] ❌ Error forwarding to {target_ip}: {e}")
            return {'status': 'error', 'msg': 'Remote node failed'}

    def process_local(self, msg):
        """Ejecuta la tarea en ESTE nodo"""
        if msg['type'] == 'ML_TRAIN':
            return self.ml_app.train(msg['data'])
        elif msg['type'] == 'MONITOR':
            return self.monitor_app.get_stats()
        elif msg['type'] == 'IMAGE_PROC':
            return self.image_app.process(msg['data'])
        return {'status': 'error', 'msg': 'Unknown command'}

    def _handle_client(self, client):
        try:
            data = client.recv(8192)
            if not data: return
            msg = json.loads(data.decode())
            
            # 1. Ver si el mensaje ya fue reenviado (para que quien lo recibe lo ejecute sí o sí)
            is_forwarded = msg.get('is_forwarded', False)
            
            target_ip = "local"
            
            # 2. Si NO es reenviado, preguntamos al Scheduler quién debe hacerlo
            if not is_forwarded:
                target_ip = self.scheduler.decide_node()
            
            response = {}

            # 3. Ejecución
            if target_ip == "local":
                print(f" [API] ⚙️ Processing {msg['type']} LOCALLY")
                response = self.process_local(msg)
            else:
                # DELEGACIÓN (Load Balancing en acción)
                print(f" [API] 📡 Forwarding {msg['type']} to {target_ip}")
                response = self.forward_request(target_ip, msg)
                # Añadimos metadata para saber quién lo hizo realmente
                response['executed_by'] = target_ip
            
            client.send(json.dumps(response).encode())
            
        except Exception as e:
            print(f" [API] Error: {e}")
        finally:
            client.close()

    def start(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(10)
        print(f" [API] Listening on TCP {self.port}")
        
        def run_server():
            while self.running:
                client, addr = server.accept()
                threading.Thread(target=self._handle_client, args=(client,)).start()
        
        threading.Thread(target=run_server, daemon=True).start()

    def stop(self): self.running = False
