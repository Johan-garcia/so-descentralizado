import random

class DistributedScheduler:
    def __init__(self, node_id, discovery):
        self.node_id = node_id
        self.discovery = discovery

    def decide_node(self):
        """
        Decide qué nodo ejecutará la tarea.
        Retorna: 'local' o la IP del nodo remoto.
        """
        peers = self.discovery.get_peers() # Obtiene diccionario {id: {ip: ..., last_seen: ...}}
        
        # Si no hay nadie más en la red, trabajamos local
        if not peers:
            return "local"
        
        # Lógica de Balanceo de Carga (Load Balancing)
        # Aquí implementamos una decisión aleatoria simple para distribuir
        # 50% probabilidad de hacerlo local, 50% de delegar (ajustable)
        
        candidates = list(peers.values()) # Lista de dicts con IPs
        
        # Lanzamos una moneda: ¿Lo hago yo o lo delego?
        if random.random() < 0.3: # 30% probabilidad de hacerlo local siempre
            return "local"
            
        # Si delegamos, elegimos un nodo al azar de los disponibles
        chosen_peer = random.choice(candidates)
        print(f" [SCHEDULER] 🔀 Delegating task to {chosen_peer['ip']}")
        return chosen_peer['ip']
