import os
import time
import sys
import threading

# Añadir rutas al path
sys.path.append('/opt/os-decentralized')

from network.discovery import NodeDiscovery
from api.distributed_api import DistributedAPI
from scheduler.distributed_scheduler import DistributedScheduler

def start_kernel():
    node_id = os.getenv('NODE_ID', 'unknown')
    node_ip = os.getenv('NODE_IP', '127.0.0.1')
    
    print(f" [KERNEL] ⚡ Booting Decentralized OS on {node_id} ({node_ip})...")
    
    # 1. Capa de Red (Discovery)
    discovery = NodeDiscovery(node_id, node_ip)
    discovery.start()
    
    # 2. Scheduler Distribuido (Gestión de recursos)
    scheduler = DistributedScheduler(node_id, discovery)
    
    # 3. API de Comunicación (Para Apps)
    api = DistributedAPI(node_id, discovery, scheduler)
    api.start()
    
    print(" [KERNEL] ✅ System Operational.")
    
    # Loop principal
    try:
        while True:
            time.sleep(5)
            # Monitor de estado (opcional)
            # peers = discovery.get_peers()
            # print(f" [STATUS] Peers: {len(peers)} | Tasks: {scheduler.task_count}")
    except KeyboardInterrupt:
        print(" [KERNEL] Shutting down...")
        api.stop()
        discovery.stop()

if __name__ == "__main__":
    start_kernel()
