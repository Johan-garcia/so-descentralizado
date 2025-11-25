import socket
import json
import threading
import os
from apps.ml_app import MLApp
from apps.image_app import ImageApp
from apps.monitor_app import MonitorApp # Asumiendo que esta ya existe de antes

class DistributedAPI:
    def __init__(self, node_id, discovery, scheduler, port=5001):
        self.node_id = node_id
        self.discovery = discovery
        self.scheduler = scheduler
        self.port = port
        self.running = False
        
        # Instanciamos las Apps
        self.ml_app = MLApp(node_id)
        self.image_app = ImageApp(node_id)
        self.monitor_app = MonitorApp(node_id)

    def forward_request(self, target_ip, msg):
        """Reenvía la tarea a otro nodo (Load Balancing)"""
        try:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(10) # Damos 10s porque procesar puede tardar
            remote.connect((target_ip, 5001))
            
            msg['is_forwarded'] = True
            remote.send(json.dumps(msg).encode())
            
            # Esperar respuesta grande
            response_data = remote.recv(16384) 
            remote.close()
            return json.loads(response_data.decode())
        except Exception as e:
            print(f" [API] ❌ Error forwarding to {target_ip}: {e}")
            return {'status': 'error', 'msg': f'Node {target_ip} failed'}

    def process_local(self, msg):
        """Ejecuta la lógica en ESTE nodo"""
        msg_type = msg.get('type')
        data = msg.get('data')

        if msg_type == 'ML_TRAIN':
            return self.ml_app.run_task(data)
            
        elif msg_type == 'IMAGE_PROC':
            return self.image_app.process(data)
            
        elif msg_type == 'MONITOR':
            return self.monitor_app.get_stats()
            
        return {'status': 'error', 'msg': 'Unknown command'}

    def _handle_client(self, client):
        try:
            raw_data = client.recv(16384) # Buffer aumentado para archivos
            if not raw_data: return
            
            msg = json.loads(raw_data.decode())
            
            # 1. Lógica de Distribución (Scheduler)
            is_forwarded = msg.get('is_forwarded', False)
            target_ip = "local"
            
            if not is_forwarded:
                # Si soy el primer nodo en recibirlo, decido quién trabaja
                target_ip = self.scheduler.decide_node()
            
            # 2. Ejecución o Delegación
            response = {}
            if target_ip == "local":
                print(f" [API] ⚙️ Executing {msg['type']} LOCALLY")
                response = self.process_local(msg)
            else:
                print(f" [API] 📡 Delegating to {target_ip}")
                response = self.forward_request(target_ip, msg)
            
            # 3. Responder al cliente
            client.send(json.dumps(response).encode())
            
        except Exception as e:
            print(f" [API] Error: {e}")
            err_resp = {'status': 'error', 'msg': str(e)}
            client.send(json.dumps(err_resp).encode())
        finally:
            client.close()

    def start(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(20)
        print(f" [API] Distributed API listening on port {self.port}")
        
        def run():
            while self.running:
                client, addr = server.accept()
                threading.Thread(target=self._handle_client, args=(client,)).start()
        
        threading.Thread(target=run, daemon=True).start()

    def stop(self): self.running = False
