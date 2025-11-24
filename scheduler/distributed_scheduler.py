class DistributedScheduler:
    def __init__(self, node_id, discovery):
        self.node_id = node_id
        self.discovery = discovery
        self.task_count = 0
        self.reputation = 1.0

    def schedule_task(self, task_type, data):
        """
        Algoritmo de decisión simple basado en la lista de peers
        Si hay peers, delega (Round Robin simple o Random)
        Si no, ejecuta local
        """
        peers = self.discovery.get_peers()
        if peers:
            # Aquí iría la lógica matemática de reputación
            # Por simplicidad, retornamos un peer random
            import random
            target_id = random.choice(list(peers.keys()))
            return target_id
        else:
            return "local"
