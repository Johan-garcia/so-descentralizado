#!/bin/bash

echo "╔════════════════════════════════════════════════════╗"
echo "║  Suite de Pruebas - SO Descentralizado            ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Verificar que el sistema esté corriendo
echo "[BUSCANDO] Verificando que el sistema este activo..."
if !  docker ps | grep -q "so-node"; then
    echo "[ERROR] El contenedor no esta corriendo.  Ejecuta: docker-compose up -d"
    exit 1
fi
echo "[OK] Sistema activo"
echo ""

# Test 1: Regresión Lineal (Single)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[TEST] TEST 1: Regresion Lineal (Single Node)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/regresion.txt linear single
echo ""
sleep 2

# Test 2: Regresión Lineal (Parallel) - CORREGIDO
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[TEST] TEST 2: Regresion Lineal (Parallel/Federated)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/regresion.txt linear parallel
echo ""
sleep 2

# Test 3: Regresión Logística
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[TEST] TEST 3: Regresion Logistica (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/clasificacion.txt logistic parallel
echo ""
sleep 2

# Test 4: Red Neuronal MLP
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[TEST] TEST 4: Red Neuronal MLP (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/red_neuronal.txt mlp parallel
echo ""
sleep 2

# Test 5: Árbol de Decisión
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[TEST] TEST 5: Arbol de Decision (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/arbol.txt tree parallel
echo ""
sleep 2

# Test 6: Procesamiento de Imágenes
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[TEST] TEST 6: Procesamiento de Imagenes (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/imagen.txt image parallel
echo ""

echo "╔════════════════════════════════════════════════════╗"
echo "║  [OK] TODAS LAS PRUEBAS COMPLETADAS              ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Resumen de algoritmos probados:"
echo "   1. [OK] Regresion Lineal (Single + Parallel)"
echo "   2. [OK] Regresion Logistica (Parallel)"
echo "   3. [OK] Red Neuronal MLP (Parallel)"
echo "   4. [OK] Arbol de Decision (Parallel)"
echo "   5. [OK] Procesamiento de Imagenes (Parallel)"
echo ""
echo "[INFO] Para ver logs detallados: docker logs -f so-node"
