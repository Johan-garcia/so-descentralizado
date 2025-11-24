class DistributedScheduler:
    def __init__(self, node_id, discovery):
        self.node_id = node_id
        self.discovery = discovery
        self.task_count = 0
        self.reputation = 1.0

    def schedule_task(self, task_type, data):
        # Algoritmo de decisión simple basado en la lista de peers
        # Si hay peers, delega (Round Robin simple o Random)
        # Si no, ejecuta local
        peers = self.discovery.get_peers()
        if peers:
            # Aquí iría la lógica matemática de reputación
            # Por simplicidad, retornamos un peer random
            import random
            target_id = random.choice(list(peers.keys()))
            return target_id
        else:
            return "local"
5.2. API del Sistema (Comunicación entre Nodos)
Archivo: api/distributed_api.py

import socket
import json
import threading
# Importar Apps
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
        
        # Instancias de las Apps
        self.ml_app = MLApp(node_id)
        self.monitor_app = MonitorApp(node_id)
        self.image_app = ImageApp(node_id)

    def _handle_client(self, client):
        try:
            data = client.recv(8192)
            msg = json.loads(data.decode())
            response = {'status': 'error'}

            # Enrutamiento de mensajes a las Apps
            if msg['type'] == 'ML_TRAIN':
                response = self.ml_app.train(msg['data'])
            elif msg['type'] == 'MONITOR':
                response = self.monitor_app.get_stats()
            elif msg['type'] == 'IMAGE_PROC':
                response = self.image_app.process(msg['data'])
            
            client.send(json.dumps(response).encode())
        except Exception as e:
            print(f"API Error: {e}")
        finally:
            client.close()

    def start(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        def run_server():
            while self.running:
                client, _ = server.accept()
                threading.Thread(target=self._handle_client, args=(client,)).start()
        
        threading.Thread(target=run_server, daemon=True).start()

    def stop(self): self.running = False
