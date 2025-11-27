import socket
import json
import threading
import struct
import time
from apps.ml_app import MLApp
from apps.image_app import ImageApp
from apps.monitor_app import MonitorApp
from apps.classification_app import ClassificationApp
from apps.mlp_app import MLPApp

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
        self.classification_app = ClassificationApp(node_id)
        self.mlp_app = MLPApp(node_id)

    # --- COMUNICACIÓN SEGURA (prefijo de longitud) ---
    def _send_msg(self, sock, msg):
        msg_bytes = json.dumps(msg).encode()
        sock.sendall(struct.pack('>I', len(msg_bytes)) + msg_bytes)

    def _recv_msg(self, sock):
        try:
            raw_len = sock.recv(4)
            if not raw_len:
                return None
            msg_len = struct.unpack('>I', raw_len)[0]
            data = b''
            while len(data) < msg_len:
                packet = sock.recv(min(4096, msg_len - len(data)))
                if not packet:
                    return None
                data += packet
            return json.loads(data.decode())
        except:
            return None

    def forward_request(self, target_ip, msg):
        """Envía tarea a otro nodo y espera respuesta"""
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

    # --- MAP/REDUCE helpers ---
    def _split_data(self, content, num_parts):
        lines = content.strip().split('\n')
        total_lines = len(lines)
        if total_lines == 0:
            return []
        chunk_size = -(-total_lines // num_parts)
        chunks = []
        for i in range(0, total_lines, chunk_size):
            chunks.append('\n'.join(lines[i:i + chunk_size]))
        return chunks

    def _aggregate_results(self, results, task_type):
        # Filtrar solo respuestas exitosas
        valid_results = [r for r in results if r and r.get('status') == 'success']
        failed_count = len(results) - len(valid_results)
        if failed_count > 0:
            print(f" [WARN] ⚠️ {failed_count} chunks fallaron o se perdieron.")

        if not valid_results:
            return {'status': 'error', 'msg': 'All nodes failed'}

        # ML federated averaging
        if task_type == 'ML_TRAIN':
            count = len(valid_results)
            num_weights = len(valid_results[0].get('weights', []))
            if num_weights == 0:
                return {'status': 'error', 'msg': 'No valid weights returned'}
            avg_weights = [0.0] * num_weights
            avg_bias = 0.0
            nodes = []
            for res in valid_results:
                nodes.append(res.get('executed_by', 'unknown'))
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
                'nodes_involved': nodes,
                'nodes_failed': failed_count,
                'weights': final_weights,
                'bias': final_bias
            }

        # Image processing: concatenate reconstructed parts (assumes vertical split)
        elif task_type == 'IMAGE_PROC':
            final_matrix = []
            nodes = []
            for res in results:
                if res and res.get('status') == 'success':
                    final_matrix.extend(res.get('processed_matrix', []))
                    nodes.append(res.get('executed_by', 'unknown'))
            return {
                'status': 'success',
                'distribution_mode': 'PARALLEL_SPLIT',
                'nodes_involved': nodes,
                'nodes_failed': failed_count,
                'processed_matrix': final_matrix
            }

        # Classification / MLP results: return all successful node outputs for downstream fusion
        elif task_type in ('CLASSIFY', 'MLP_TRAIN'):
            nodes = []
            outputs = []
            for res in results:
                if res and res.get('status') == 'success':
                    nodes.append(res.get('executed_by', 'unknown'))
                    # store full payload (result/predictions/etc.)
                    outputs.append(res.get('result', res))
            return {
                'status': 'success',
                'distribution_mode': 'PARALLEL_COLLECT',
                'nodes_involved': nodes,
                'nodes_failed': failed_count,
                'results': outputs
            }

        return {'status': 'unknown task', 'nodes_failed': failed_count}

    # --- PARALLEL PROCESSING ---
    def process_parallel(self, msg):
        # Obtener peers y normalizar candidatos
        peers = self.discovery.get_peers()
        candidates = []
        for p in peers.values():
            candidates.append({'ip': p['ip']})
        candidates.append({'ip': 'local'})

        active_workers = []
        print(f" [PARALLEL] 🔍 Verificando disponibilidad de {len(candidates)} candidatos...")

        # Verificar conectividad TCP (rápida)
        for w in candidates:
            target_ip = w['ip']
            if target_ip == 'local':
                active_workers.append(w)
            else:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1.0)
                    s.connect((target_ip, self.port))
                    s.close()
                    active_workers.append(w)
                except Exception as e:
                    print(f"   ⚠️ Nodo {target_ip} no responde: {e}")

        num_workers = len(active_workers)
        if num_workers == 0:
            return {'status': 'error', 'msg': 'No active workers'}

        print(f" [PARALLEL] 🚀 Distribuyendo tarea entre {num_workers} nodos activos...")

        raw_content = msg['data'].get('file_content', '')
        chunks = self._split_data(raw_content, num_workers)
        threads = []
        results = [None] * len(chunks)

        def worker_task(index, worker_ip, chunk_data):
            sub_msg = msg.copy()
            sub_msg['data'] = msg['data'].copy()
            sub_msg['data']['file_content'] = chunk_data

            if worker_ip == 'local':
                print(f"   -> Chunk {index} procesando localmente")
                results[index] = self.process_local(sub_msg)
            else:
                print(f"   -> Chunk {index} enviando a {worker_ip}")
                res = self.forward_request(worker_ip, sub_msg)
                if res:
                    print(f"   ✅ {worker_ip} terminó Chunk {index}")
                    results[index] = res
                else:
                    print(f"   ❌ {worker_ip} falló Chunk {index}")
                    results[index] = None

        for i, worker in enumerate(active_workers):
            if i < len(chunks):
                ip = worker.get('ip')
                t = threading.Thread(target=worker_task, args=(i, ip, chunks[i]))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        print(f" [PARALLEL] 🏁 Todos terminaron. Unificando resultados...")
        return self._aggregate_results(results, msg['type'])

    # --- PROCESAMIENTO LOCAL ---
    def process_local(self, msg):
        t = msg.get('type')
        if t == 'ML_TRAIN':
            return self.ml_app.run_task(msg['data'])
        elif t == 'IMAGE_PROC':
            return self.image_app.process(msg['data'])
        elif t == 'MONITOR':
            return self.monitor_app.get_stats()
        elif t == 'CLASSIFY':
            return self.classification_app.run_task(msg['data'])
        elif t == 'MLP_TRAIN':
            return self.mlp_app.run_task(msg['data'])
        return {'status': 'error', 'msg': 'Unknown'}

    # --- MANEJO DE PETICIONES ENTRANTES ---
    def _handle_client(self, client):
        try:
            msg = self._recv_msg(client)
            if not msg:
                return

            if msg.get('mode') == 'parallel':
                response = self.process_parallel(msg)
            else:
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
            try:
                self._send_msg(client, {'status': 'error', 'msg': str(e)})
            except:
                pass
        finally:
            client.close()

    def start(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(20)
        print(f" [API] Distributed API listening on port {self.port}")

        def run():
            while self.running:
                try:
                    c, a = server.accept()
                    threading.Thread(target=self._handle_client, args=(c,)).start()
                except:
                    pass
        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        self.running = False
