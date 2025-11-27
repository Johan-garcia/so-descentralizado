#!/usr/bin/env python3
import socket
import json
import time
import subprocess

def test_api_endpoint(ip, port=5001, msg_type='MONITOR', data={}):
    """Prueba genérica de API"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))
        
        request = {'type': msg_type, 'data': data}
        sock.send(json.dumps(request).encode())
        
        response = sock.recv(4096)
        result = json.loads(response.decode())
        sock.close()
        return result
    except Exception as e:
        return {'error': str(e)}

def test_monitor():
    """Prueba la app de monitoreo"""
    print("[TEST] Testing Monitor App...")
    result = test_api_endpoint('127.0.0.1', msg_type='MONITOR')
    
    if 'error' not in result:
        print(f"   [OK] Node: {result.get('node')}")
        print(f"   [OK] CPU: {result.get('cpu')}%")
        print(f"   [OK] RAM: {result.get('ram')}%")
        return True
    else:
        print(f"   [ERROR] Error: {result['error']}")
        return False

def test_ml():
    """Prueba ML training"""
    print("\n[TEST] Testing ML Training...")
    result = test_api_endpoint('127.0.0.1', msg_type='ML_TRAIN', data={
        'model': 'linear',
        'X': [[1], [2], [3], [4], [5]],
        'y': [2, 4, 6, 8, 10]
    })
    
    if 'error' not in result:
        print(f"   [OK] Weights: {result.get('weights')}")
        print(f"   [OK] Bias: {result.get('bias')}")
        return True
    else:
        print(f"   [ERROR] Error: {result['error']}")
        return False

def test_image_processing():
    """Prueba procesamiento de imágenes"""
    print("\n[TEST] Testing Image Processing...")
    
    # Imagen 3x3 simple
    test_image = [[100, 150, 200], [50, 100, 150], [25, 75, 125]]
    
    result = test_api_endpoint('127.0.0.1', msg_type='IMAGE_PROC', data={
        'image': test_image,
        'op': 'invert'
    })
    
    if 'error' not in result:
        print(f"   [OK] Image processed successfully")
        print(f"   Original: {test_image[0]}")
        print(f"   Inverted: {result.get('image', [[]])[0]}")
        return True
    else:
        print(f"   [ERROR] Error: {result['error']}")
        return False

def scan_network_for_nodes():
    """Escanea la red para encontrar nodos activos"""
    print("\n[BUSCANDO] Scanning network for active nodes...")
    print("   (This may take 20-30 seconds)")
    
    active_nodes = []
    
    # Escanear subnet 10.0.1.x
    for i in range(1, 255):
        ip = f"10.0.1.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 5001))
            if result == 0:
                # Puerto abierto, probar si es nuestro nodo
                try:
                    response = test_api_endpoint(ip, msg_type='MONITOR')
                    if 'node' in response:
                        node_id = response['node']
                        active_nodes.append({'id': node_id, 'ip': ip})
                        print(f"   [OK] Found: {node_id} at {ip}")
                except:
                    pass
            sock.close()
        except:
            pass
    
    print(f"\n   Total active nodes: {len(active_nodes)}")
    return active_nodes

def check_docker_logs():
    """Revisa los logs del Docker para ver peers descubiertos"""
    print("\n[INFO] Checking Docker logs for peer discovery...")
    try:
        result = subprocess.run(['docker', 'logs', '--tail', '50', 'so-node'], 
                              capture_output=True, text=True, timeout=5)
        
        logs = result.stdout + result.stderr
        
        # Buscar menciones de peers
        if 'peer' in logs.lower() or 'found' in logs.lower():
            print("   [OK] Peer discovery activity detected")
            # Mostrar líneas relevantes
            for line in logs.split('\n'):
                if 'peer' in line.lower() or 'found' in line.lower():
                    print(f"      {line.strip()}")
        else:
            print("   [ADVERTENCIA] No peer discovery activity in recent logs")
            
    except Exception as e:
        print(f"   [ERROR] Could not read logs: {e}")

if __name__ == "__main__":
    print("="*70)
    print(" DECENTRALIZED OS - COMPREHENSIVE SYSTEM TEST")
    print("="*70)
    
    results = {
        'monitor': False,
        'ml': False,
        'image': False,
        'nodes': []
    }
    
    # Test 1: Monitor
    results['monitor'] = test_monitor()
    
    # Test 2: ML
    results['ml'] = test_ml()
    
    # Test 3: Image Processing
    results['image'] = test_image_processing()
    
    # Test 4: Network Discovery
    results['nodes'] = scan_network_for_nodes()
    
    # Test 5: Docker Logs
    check_docker_logs()
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f"  Monitor App:        {'[OK] PASS' if results['monitor'] else '[ERROR] FAIL'}")
    print(f"  ML Training:        {'[OK] PASS' if results['ml'] else '[ERROR] FAIL'}")
    print(f"  Image Processing:   {'[OK] PASS' if results['image'] else '[ERROR] FAIL'}")
    print(f"  Active Nodes:       {len(results['nodes'])}")
    
    for node in results['nodes']:
        print(f"    - {node['id']} ({node['ip']})")
    
    all_tests_pass = results['monitor'] and results['ml'] and results['image']
    
    print("\n" + "="*70)
    if all_tests_pass and len(results['nodes']) >= 3:
        print(" ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL")
    elif all_tests_pass:
        print(" [ADVERTENCIA] APPS WORKING - Waiting for all 3 nodes to connect")
    else:
        print(" [ERROR] SOME TESTS FAILED - Check logs above")
    print("="*70)
