import sys
import json
import socket
import os
import struct

API_IP = '127.0.0.1'
API_PORT = 5001

def enviar_al_kernel(payload):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(30)  # Timeout más largo para procesos distribuidos
        client.connect((API_IP, API_PORT))
        
        # Protocolo con longitud (Seguro)
        msg_bytes = json.dumps(payload).encode()
        client.sendall(struct.pack('>I', len(msg_bytes)) + msg_bytes)
        
        # Recibir
        raw_len = client.recv(4)
        if not raw_len: return None
        msg_len = struct.unpack('>I', raw_len)[0]
        
        data = b''
        while len(data) < msg_len:
            packet = client.recv(min(4096, msg_len - len(data)))
            if not packet: break
            data += packet
            
        client.close()
        return json.loads(data.decode())
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[ERROR] Uso: python3 ejecutar.py <archivo> <app> [modo]")
        print("\nApps disponibles:")
        print("   • linear    - Regresión Lineal")
        print("   • logistic  - Regresión Logística")
        print("   • mlp       - Red Neuronal (MLP)")
        print("   • tree      - Árbol de Decisión")
        print("   • image     - Procesamiento de Imágenes")
        print("\nModos:")
        print("   • single   - Ejecuta en un solo nodo (defecto)")
        print("   • parallel - Distribuye entre todos los nodos")
        print("\nEjemplos:")
        print("   python3 ejecutar.py mis_datos/regresion.txt linear parallel")
        print("   python3 ejecutar.py mis_datos/clasificacion.txt logistic parallel")
        print("   python3 ejecutar.py mis_datos/red_neuronal.txt mlp parallel")
        print("   python3 ejecutar.py mis_datos/arbol.txt tree parallel")
        print("   python3 ejecutar.py mis_datos/imagen. txt image parallel")
        sys.exit(1)

    archivo_path = sys.argv[1]
    app_type = sys.argv[2]
    modo = sys.argv[3] if len(sys.argv) > 3 else 'single'

    if not os.path.exists(archivo_path):
        print(f"[ERROR] Archivo no encontrado: {archivo_path}")
        sys.exit(1)

    with open(archivo_path, 'r') as f:
        contenido = f.read()

    payload = {
        'mode': modo,
        'data': {'file_content': contenido}
    }

    if app_type == 'linear':
        payload['type'] = 'ML_TRAIN'
        payload['data']['algorithm'] = 'linear'
        print("Algoritmo: Regresion Lineal")
        
    elif app_type == 'logistic':
        payload['type'] = 'LOGISTIC'
        print("Algoritmo: Regresion Logistica")
        
    elif app_type == 'mlp':
        payload['type'] = 'MLP_TRAIN'
        print("Algoritmo: Red Neuronal (MLP)")
        
    elif app_type == 'tree':
        payload['type'] = 'TREE_TRAIN'
        payload['data']['max_depth'] = 5  # Profundidad máxima del árbol
        print("Algoritmo: Arbol de Decision")
        
    elif app_type == 'image':
        payload['type'] = 'IMAGE_PROC'
        payload['data']['operation'] = 'invert'
        print("Algoritmo: Procesamiento de Imagenes")
        
    else:
        print(f"[ERROR] App desconocida: {app_type}")
        print("Apps válidas: linear, logistic, mlp, tree, image")
        sys.exit(1)

    print(f"[INICIANDO] Enviando tarea en modo: {modo. upper()}")
    print(f"Archivo: {archivo_path}\n")
    
    res = enviar_al_kernel(payload)
    
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("="*60)
