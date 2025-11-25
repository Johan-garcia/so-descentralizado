import socket
import json
import threading
import struct
from apps.ml_app import MLApp
from apps.image_app import ImageApp
from apps.monitor_app import MonitorApp

class DistributedAPI:
    def __init__(self, node_id, discovery, scheduler, port=5001):
        self.node_id = node_id
        self.discovery = discovery
        self.scheduler = scheduler
        self.port = port
        self.running = False
        
        # Apps Locales
        self.ml_app = MLApp(node_id)
        self.image_app = ImageApp(node_id)
        self.monitor_app = MonitorApp(node_id)

    # --- Funciones de Comunicación Segura ---
    def _send_msg(self, sock, msg):
        msg_bytes = json.dumps(msg).encode()
        sock.sendall(struct.pack('>I', len(msg_bytes)) + msg_bytes)

    def _recv_msg(self, sock):
        try:
            raw_len = sock.recv(4)
            if not raw_len: return None
            msg_len = struct.unpack('>I', raw_len)[0]
            data = b''
            while len(data) < msg_len:
                packet = sock.recv(min(4096, msg_len - len(data)))
                if not packet: return None
                data += packet
            return json.loads(data.decode())
        except: return None

    def forward_request(self, target_ip, msg):
        """Envía una tarea a un nodo específico y espera respuesta"""
        try:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(15) # Tiempo extra para procesar
            remote.connect((target_ip, 5001))
            
            # Importante: Al reenviar, quitamos el modo 'parallel' para que el nodo 
            # receptor sepa que TIENE QUE EJECUTARLO ÉL (no volver a dividirlo)
            msg['mode'] = 'single' 
            msg['is_forwarded'] = True
            
            self._send_msg(remote, msg)
            response = self._recv_msg(remote)
            remote.close()
            return response
        except Exception as e:
            print(f" [API] ❌ Error enviando a {target_ip}: {e}")
            return None

    # --- LÓGICA DE PARALELISMO (MAP REDUCE) ---
    
    def _split_data(self, content, num_parts):
        """Divide el texto en N partes iguales respetando saltos de línea"""
        lines = content.strip().split('\n')
        total_lines = len(lines)
        if total_lines == 0: return []
        
        chunk_size = -(-total_lines // num_parts) # Ceiling division
        chunks = []
        
        for i in range(0, total_lines, chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunks.append('\n'.join(chunk_lines))
            
        return chunks

    def _aggregate_results(self, results, task_type):
        """Combina los resultados de los N nodos"""
        if not results: return {'status': 'error', 'msg': 'No results to aggregate'}
        
        # 1. Agregación para IA (Promedio de Pesos - Federated Averaging)
        if task_type == 'ML_TRAIN':
            valid_results = [r for r in results if r and r.get('status') == 'success' and 'weights' in r]
            if not valid_results: return {'status': 'error', 'msg': 'All nodes failed'}
            
            # Promediar pesos
            count = len(valid_results)
            num_weights = len(valid_results[0]['weights'])
            avg_weights = [0.0] * num_weights
            avg_bias = 0.0
            
            for res in valid_results:
                w = res['weights']
                b = res['bias']
                avg_bias += b
                for i in range(num_weights):
                    avg_weights[i] += w[i]
            
            final_weights = [x / count for x in avg_weights]
            final_bias = avg_bias / count
            
            return {
                'status': 'success',
                'distribution_mode': 'PARALLEL_FEDERATED',
                'nodes_involved': [r['executed_by'] for r in valid_results],
                'weights': final_weights,
                'bias': final_bias
            }

        # 2. Agregación para Imágenes (Unir pedazos)
        elif task_type == 'IMAGE_PROC':
            # Ordenar resultados para que la imagen no quede desordenada
            # (Asumimos que el envío fue ordenado, concatenamos en orden de llegada)
            # Una mejora sería enviar el índice del chunk.
            final_matrix = []
            nodes = []
            for res in results:
                if res and res.get('status') == 'success':
                    final_matrix.extend(res['processed_matrix'])
                    nodes.append(res['executed_by'])
            
            return {
                'status': 'success',
                'distribution_mode': 'PARALLEL_SPLIT',
                'nodes_involved': nodes,
                'processed_matrix': final_matrix,
                'original_size': f"Reconstructed from {len(nodes)} parts"
            }
            
        return {'status': 'unknown task'}

    def process_parallel(self, msg):
        """El director de orquesta: Divide, Envía y Une"""
        peers = self.discovery.get_peers()
        
        # Lista de trabajadores: Mis amigos + Yo mismo
        workers = list(peers.values()) 
        # Añadimos 'local' para que yo también trabaje
        workers.append({'ip': 'local'})
        
        num_workers = len(workers)
        print(f" [PARALLEL] 🚀 Distribuyendo tarea entre {num_workers} nodos...")
        
        # 1. MAP: Dividir datos
        raw_content = msg['data'].get('file_content', '')
        chunks = self._split_data(raw_content, num_workers)
        
        threads = []
        results = [None] * len(chunks) # Array para guardar resultados en orden

        # Función para el hilo
        def worker_task(index, worker_ip, chunk_data):
            # Crear sub-mensaje
            sub_msg = msg.copy()
            sub_msg['data'] = msg['data'].copy()
            sub_msg['data']['file_content'] = chunk_data
            
            if worker_ip == 'local':
                print(f"   -> Chunk {index} procesado localmente")
                results[index] = self.process_local(sub_msg)
            else:
                print(f"   -> Chunk {index} enviado a {worker_ip}")
                results[index] = self.forward_request(worker_ip, sub_msg)

        # 2. DISTRIBUTE: Lanzar hilos
        for i, worker in enumerate(workers):
            if i < len(chunks): # Evitar error si hay más workers que líneas
                ip = worker.get('ip', 'local')
                t = threading.Thread(target=worker_task, args=(i, ip, chunks[i]))
                threads.append(t)
                t.start()
        
        # 3. WAIT: Esperar a todos
        for t in threads:
            t.join()
            
        # 4. REDUCE: Unir resultados
        print(f" [PARALLEL] 🏁 Todos terminaron. Unificando resultados...")
        return self._aggregate_results(results, msg['type'])

    # --- MÉTODOS ESTÁNDAR ---

    def process_local(self, msg):
        if msg['type'] == 'ML_TRAIN':
            return self.ml_app.run_task(msg['data'])
        elif msg['type'] == 'IMAGE_PROC':
            return self.image_app.process(msg['data'])
        elif msg['type'] == 'MONITOR':
            return self.monitor_app.get_stats()
        return {'status': 'error', 'msg': 'Unknown'}

    def _handle_client(self, client):
        try:
            msg = self._recv_msg(client)
            if not msg: return
            
            response = {}
            
            # ¿El usuario pidió modo paralelo explícito?
            if msg.get('mode') == 'parallel':
                response = self.process_parallel(msg)
            else:
                # Modo normal (Single Node / Delegation)
                is_forwarded = msg.get('is_forwarded', False)
                target_ip = "local" if is_forwarded else self.scheduler.decide_node()
                
                if target_ip == "local":
                    print(f" [API] ⚙️ Executing LOCALLY")
                    response = self.process_local(msg)
                else:
                    print(f" [API] 📡 Delegating to {target_ip}")
                    response = self.forward_request(target_ip, msg)
            
            self._send_msg(client, response)
            
        except Exception as e:
            print(f" [API] Error: {e}")
            try: self._send_msg(client, {'status': 'error', 'msg': str(e)})
            except: pass
        finally:
            client.close()

    def start(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(20)
        print(f" [API] Listening on {self.port}")
        def run():
            while self.running:
                try:
                    client, addr = server.accept()
                    threading.Thread(target=self._handle_client, args=(client,)).start()
                except: pass
        threading.Thread(target=run, daemon=True).start()

    def stop(self): self.running = False
