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
        print("❌ Uso: python3 ejecutar.py <archivo> <app> [modo]")
        print("   Apps: linear, image")
        print("   Modo: single (defecto) o parallel")
        print("   Ejemplo: python3 ejecutar.py mis_datos/regresion.txt linear parallel")
        sys.exit(1)

    archivo_path = sys.argv[1]
    app_type = sys.argv[2]
    modo = sys.argv[3] if len(sys.argv) > 3 else 'single'

    if not os.path.exists(archivo_path):
        print(f"❌ Archivo no encontrado: {archivo_path}")
        sys.exit(1)

    with open(archivo_path, 'r') as f:
        contenido = f.read()

    payload = {
        'mode': modo, # 'single' o 'parallel'
        'data': {'file_content': contenido}
    }

    if app_type == 'linear':
        payload['type'] = 'ML_TRAIN'
        payload['data']['algorithm'] = 'linear'
    elif app_type == 'image':
        payload['type'] = 'IMAGE_PROC'
        payload['data']['operation'] = 'invert'
    else:
        print("App desconocida.")
        sys.exit(1)

    print(f"🚀 Enviando tarea (Modo: {modo.upper()}) al cluster...")
    
    res = enviar_al_kernel(payload)
    
    print("\n📥 RESULTADO FINAL:")
    print(json.dumps(res, indent=2))
