import socket
import json
import time

# Configuración
HOST = '127.0.0.1'  # Atacamos al nodo local
PORT = 5001         # Puerto de la API

def enviar_tarea(i):
    # Datos: Un entrenamiento simple de ML
    payload = {
        'type': 'ML_TRAIN',
        'data': {
            'model': 'linear',
            'X': [[1], [2], [3], [4]],
            'y': [2, 4, 6, 8]
        }
    }

    try:
        # Conectar al socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.send(json.dumps(payload).encode())
        
        # Recibir respuesta
        data = client.recv(4096)
        response = json.loads(data.decode())
        
        # Ver quién lo ejecutó
        ejecutor = response.get('executed_by', 'local')
        print(f"Petición {i+1}: ✅ Procesada por -> {ejecutor}")
        
        client.close()
    except Exception as e:
        print(f"Petición {i+1}: ❌ Error: {e}")

print(f"--- 🚀 INICIANDO TEST DE CARGA (Load Balancing) ---")
print(f"Enviando tareas al Nodo 1 para ver si las distribuye...\n")

# Enviamos 10 tareas seguidas
for x in range(10):
    enviar_tarea(x)
    time.sleep(1) # Esperar 1 seg entre peticiones para dar tiempo a ver los logs

print("\n--- 🏁 TEST FINALIZADO ---")
