import random
import time

class DistributedScheduler:
    def __init__(self, node_id, discovery):
        self.node_id = node_id
        self.discovery = discovery

    def decide_node(self):
        # Obtener pares
        peers = self.discovery.get_peers()
        
        # --- DEBUG PRINT ---
        # Esto saldrá en los logs de docker y nos dirá la verdad
        print(f" [DEBUG SCHEDULER] Veo {len(peers)} amigos: {list(peers.keys())}")
        # -------------------

        # Si no hay nadie, local
        if not peers:
            print(" [DEBUG] [ERROR] Nadie disponible, me toca a mi (Local)")
            return "local"
        
        candidates = list(peers.values())
        
        # Forzamos un poco más la distribución (80% probabilidad de enviar fuera para probar)
        if random.random() < 0.2: 
            print(" [DEBUG] Decision aleatoria: Lo hago yo (Local)")
            return "local"
            
        chosen_peer = random.choice(candidates)
        target_ip = chosen_peer['ip']
        print(f" [DEBUG] [INICIANDO] ENVIANDO TAREA A: {target_ip}")
        return target_ip
