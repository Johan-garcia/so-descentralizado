import sys
import json
import socket
import os

# Configuración del Nodo Local
API_IP = '127.0.0.1'
API_PORT = 5001

def enviar_al_kernel(payload):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((API_IP, API_PORT))
        client.send(json.dumps(payload).encode())
        
        # Recibir respuesta
        response = client.recv(16384).decode()
        client.close()
        return json.loads(response)
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Uso correcto: python3 ejecutar.py <archivo> <aplicacion>")
        print("   Aplicaciones disponibles: linear, tree, image")
        print("   Ejemplo: python3 ejecutar.py mis_datos/regresion.txt linear")
        sys.exit(1)

    archivo_path = sys.argv[1]
    app_type = sys.argv[2]

    # 1. Leer el archivo TXT
    if not os.path.exists(archivo_path):
        print(f"❌ El archivo '{archivo_path}' no existe.")
        sys.exit(1)

    with open(archivo_path, 'r') as f:
        contenido = f.read()

    # 2. Preparar el paquete para el SO
    payload = {}

    if app_type in ['linear', 'tree']:
        payload = {
            'type': 'ML_TRAIN',
            'data': {
                'algorithm': app_type,
                'file_content': contenido
            }
        }
    elif app_type == 'image':
        payload = {
            'type': 'IMAGE_PROC',
            'data': {
                'operation': 'invert', # Operación por defecto
                'file_content': contenido
            }
        }
    else:
        print(f"❌ Aplicación '{app_type}' no reconocida.")
        sys.exit(1)

    # 3. Enviar y Mostrar Resultados
    print(f"🚀 Enviando '{archivo_path}' a la aplicación '{app_type}'...")
    
    resultado = enviar_al_kernel(payload)
    
    print("\n📥 RESPUESTA DEL SISTEMA:")
    print(json.dumps(resultado, indent=2))
