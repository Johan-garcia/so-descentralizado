import sys
import os
import uuid
import time
from network.discovery import NodeDiscovery
from scheduler.distributed_scheduler import DistributedScheduler
from api.distributed_api import DistributedAPI

sys.path.append(os.getcwd())

def main():
    # Generar ID único
    node_id = f"node-{uuid.uuid4().hex[:6]}"
    print(f" [KERNEL] ⚡ Iniciando nodo {node_id}...")

    # Iniciar componentes
    discovery = NodeDiscovery(node_id)
    discovery.start()

    scheduler = DistributedScheduler(node_id, discovery)
    
    api = DistributedAPI(node_id, discovery, scheduler)
    api.start()

    print(f" [KERNEL] ✅ Sistema Operativo en línea ({node_id}).")
    
    try:
        while True: time.sleep(1)
    except:
        discovery.stop()
        api.stop()

if __name__ == "__main__":
    main()
