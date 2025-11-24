import psutil
import time

class MonitorApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def get_stats(self):
        return {
            'node': self.node_id,
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'ts': time.time()
        }
