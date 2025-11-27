import socket
import json
import threading
import struct
import time
from apps.ml_app import MLApp
from apps.image_app import ImageApp
from apps.monitor_app import MonitorApp
from apps.mlp_app import MLPApp
from apps.logistic_app import LogisticApp
from apps.decision_tree_app import DecisionTreeApp

class DistributedAPI:
    def __init__(self, node_id, discovery, scheduler, port=5001):
        self. node_id = node_id
        self.discovery = discovery
        self.scheduler = scheduler
        self.port = port
        self. running = False

        # Apps Locales
        self.ml_app = MLApp(node_id)
        self.image_app = ImageApp(node_id)
        self.monitor_app = MonitorApp(node_id)
        self.mlp_app = MLPApp(node_id)
        self.logistic_app = LogisticApp(node_id)
        self.tree_app = DecisionTreeApp(node_id)

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
            return json.loads(data. decode())
        except: return None

    def forward_request(self, target_ip, msg):
        try:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(15)
            remote.connect((target_ip, self.port))
            msg['mode'] = 'single'
            msg['is_forwarded'] = True
            self._send_msg(remote, msg)
            response = self._recv_msg(remote)
            remote.close()
            return response
        except Exception as e:
            print(f" [API] ❌ Falló conexión con {target_ip}: {e}")
            return None

    def _split_data(self, content, num_parts):
        lines = content.strip().split('\n')
        total_lines = len(lines)
        if total_lines == 0: return []
        chunk_size = -(-total_lines // num_parts)
        chunks = []
        for i in range(0, total_lines, chunk_size):
            chunks.append('\n'.join(lines[i:i + chunk_size]))
        return chunks

    def _aggregate_results(self, results, task_type):
        valid_results = [r for r in results if r and r. get('status') == 'success']
        failed_count = len(results) - len(valid_results)
        
        if not valid_results: return {'status': 'error', 'msg': 'All nodes failed'}

        # --- LOGICA DE AGREGACION (FEDERATED LEARNING) ---
        
        # 1. Regresión Lineal (Vector simple de pesos)
        if task_type == 'ML_TRAIN':
            count = len(valid_results)
            num_weights = len(valid_results[0]['weights'])
            avg_weights = [0. 0] * num_weights
            avg_bias = 0.0
            
            for res in valid_results:
                w = res['weights']
                b = res['bias']
                avg_bias += b
                for i in range(num_weights): avg_weights[i] += w[i]
            
            return {
                'status': 'success',
                'distribution_mode': 'FEDERATED_AVG',
                'algorithm': 'Linear Regression',
                'final_weights': [x/count for x in avg_weights],
                'final_bias': avg_bias/count,
                'nodes_involved': [r['executed_by'] for r in valid_results],
                'nodes_count': len(valid_results)
            }

        # 2. Regresión Logística
        elif task_type == 'LOGISTIC':
            count = len(valid_results)
            num_weights = len(valid_results[0]['weights'])
            avg_weights = [0.0] * num_weights
            avg_bias = 0.0
            total_accuracy = 0. 0
            
            for res in valid_results:
                w = res['weights']
                b = res['bias']
                avg_bias += b
                total_accuracy += res. get('accuracy', 0)
                for i in range(num_weights): avg_weights[i] += w[i]
            
            return {
                'status': 'success',
                'distribution_mode': 'FEDERATED_AVG',
                'algorithm': 'Logistic Regression',
                'final_weights': [x/count for x in avg_weights],
                'final_bias': avg_bias/count,
                'avg_accuracy': total_accuracy/count,
                'nodes_involved': [r['executed_by'] for r in valid_results],
                'nodes_count': len(valid_results)
            }

        # 3. MLP (Promedio de Matrices complejas)
        elif task_type == 'MLP_TRAIN':
            count = len(valid_results)
            base = valid_results[0]
            
            # Inicializar matrices suma
            W1_sum = [[cell for cell in row] for row in base['input_to_hidden_w']]
            b1_sum = base['hidden_bias'][:]
            W2_sum = [[cell for cell in row] for row in base['hidden_to_output_w']]
            b2_sum = base['output_bias'][:]
            total_loss = base. get('final_loss', 0)

            # Sumar resto de nodos
            for i in range(1, count):
                res = valid_results[i]
                total_loss += res.get('final_loss', 0)
                
                # Sumar W1
                for r in range(len(W1_sum)):
                    for c in range(len(W1_sum[0])):
                        W1_sum[r][c] += res['input_to_hidden_w'][r][c]
                
                # Sumar b1
                for j in range(len(b1_sum)):
                    b1_sum[j] += res['hidden_bias'][j]
                
                # Sumar W2
                for r in range(len(W2_sum)):
                    for c in range(len(W2_sum[0])):
                        W2_sum[r][c] += res['hidden_to_output_w'][r][c]
                
                # Sumar b2
                for j in range(len(b2_sum)):
                    b2_sum[j] += res['output_bias'][j]

            # Promediar todo
            W1_avg = [[x / count for x in row] for row in W1_sum]
            b1_avg = [x / count for x in b1_sum]
            W2_avg = [[x / count for x in row] for row in W2_sum]
            b2_avg = [x / count for x in b2_sum]
            
            return {
                'status': 'success',
                'distribution_mode': 'FEDERATED_MLP_AVG',
                'algorithm': 'Multi-Layer Perceptron',
                'global_model': {
                    'input_to_hidden_weights': W1_avg,
                    'hidden_bias': b1_avg,
                    'hidden_to_output_weights': W2_avg,
                    'output_bias': b2_avg
                },
                'avg_loss': total_loss / count,
                'nodes_involved': [r['executed_by'] for r in valid_results],
                'nodes_count': len(valid_results)
            }

        # 4. Árboles de Decisión (Ensemble voting)
        elif task_type == 'TREE_TRAIN':
            count = len(valid_results)
            avg_accuracy = sum(r.get('accuracy', 0) for r in valid_results) / count
            
            # En federated learning de árboles, usamos ensemble (voting)
            trees = [r. get('tree') for r in valid_results]
            
            return {
                'status': 'success',
                'distribution_mode': 'FEDERATED_ENSEMBLE',
                'algorithm': 'Decision Tree',
                'trees': trees,
                'avg_accuracy': avg_accuracy,
                'nodes_involved': [r['executed_by'] for r in valid_results],
                'nodes_count': len(valid_results)
            }

        # 5. Procesamiento de Imágenes
        elif task_type == 'IMAGE_PROC':
            final_matrix = []
            operations = []
            for res in valid_results:
                final_matrix.extend(res['processed_matrix'])
                operations.append(res. get('operation', 'unknown'))
            
            return {
                'status': 'success',
                'distribution_mode': 'CHUNK_PROCESSING',
                'algorithm': 'Image Processing',
                'processed_matrix': final_matrix,
                'total_rows': len(final_matrix),
                'operations': list(set(operations)),
                'nodes_involved': [r['executed_by'] for r in valid_results],
                'nodes_count': len(valid_results)
            }

        return {'status': 'success', 'results': valid_results}

    def process_parallel(self, msg):
        peers = self.discovery.get_peers()
        candidates = [{'ip': p['ip']} for p in peers. values()]
        candidates.append({'ip': 'local'})
        
        active_workers = []
        print(f" [PARALLEL] 🔍 Buscando nodos para {msg['type']}...")
        for w in candidates:
            target = w['ip']
            if target == 'local': 
                active_workers.append(w)
            else:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1. 0)
                    s.connect((target, self.port))
                    s.close()
                    active_workers.append(w)
                    print(f" [PARALLEL] ✅ Nodo {target} disponible")
                except: 
                    print(f" [PARALLEL] ⚠️ Nodo {target} no responde")
        
        num_workers = len(active_workers)
        print(f" [PARALLEL] 🚀 Distribuyendo a {num_workers} nodos...")
        chunks = self._split_data(msg['data']. get('file_content',''), num_workers)
        
        threads = []
        results = [None] * len(chunks)
        
        def worker(idx, ip, data):
            sub = msg. copy()
            sub['data'] = msg['data']. copy()
            sub['data']['file_content'] = data
            if ip == 'local': 
                results[idx] = self.process_local(sub)
            else: 
                results[idx] = self.forward_request(ip, sub)

        for i, w in enumerate(active_workers):
            if i < len(chunks):
                t = threading.Thread(target=worker, args=(i, w['ip'], chunks[i]))
                t.start()
                threads.append(t)
        
        for t in threads: 
            t.join()
        
        return self._aggregate_results(results, msg['type'])

    def process_local(self, msg):
        t = msg.get('type')
        d = msg['data']
        
        print(f" [LOCAL] 🔧 Procesando {t} en nodo {self.node_id}")
        
        if t == 'ML_TRAIN': 
            return self.ml_app.run_task(d)
        elif t == 'LOGISTIC': 
            return self.logistic_app.run_task(d)
        elif t == 'MLP_TRAIN': 
            return self.mlp_app. run_task(d)
        elif t == 'TREE_TRAIN':
            return self.tree_app.run_task(d)
        elif t == 'IMAGE_PROC': 
            return self.image_app.process(d)
        elif t == 'MONITOR': 
            return self.monitor_app.get_stats()
        
        return {'status': 'error', 'msg': 'Unknown Task'}

    def _handle_client(self, client):
        try:
            msg = self._recv_msg(client)
            if not msg: return
            
            print(f" [API] 📨 Solicitud recibida: {msg. get('type')} en modo {msg.get('mode', 'single')}")
            
            if msg.get('mode') == 'parallel':
                response = self.process_parallel(msg)
            else:
                is_fwd = msg.get('is_forwarded', False)
                target = 'local' if is_fwd else self.scheduler.decide_node()
                if target == 'local': 
                    response = self. process_local(msg)
                else: 
                    response = self.forward_request(target, msg)
            
            self._send_msg(client, response)
        except Exception as e: 
            print(f" [API] ❌ Error procesando cliente: {e}")
        finally: 
            client.close()

    def start(self):
        self.running = True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s. setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.port))
        s.listen(20)
        print(f" [API] 🎧 Listening on port {self.port}")
        
        def run():
            while self.running:
                try: 
                    c, a = s.accept()
                    threading.Thread(target=self._handle_client, args=(c,)). start()
                except: 
                    pass
        
        threading.Thread(target=run, daemon=True).start()

    def stop(self): 
        self.running = False
