#!/bin/bash

echo "╔════════════════════════════════════════════════════╗"
echo "║  🧪 Suite de Pruebas - SO Descentralizado         ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Verificar que el sistema esté corriendo
echo "🔍 Verificando que el sistema esté activo..."
if !  docker ps | grep -q "so-node"; then
    echo "❌ El contenedor no está corriendo.  Ejecuta: docker-compose up -d"
    exit 1
fi
echo "✅ Sistema activo"
echo ""

# Test 1: Regresión Lineal
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 1: Regresión Lineal (Single Node)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/regresion.txt linear single
echo ""
sleep 2

# Test 2: Regresión Lineal Paralela
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 2: Regresión Lineal (Parallel/Federated)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/regresion.txt linear parallel
echo ""
sleep 2

# Test 3: Regresión Logística
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 3: Regresión Logística (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/clasificacion.txt logistic parallel
echo ""
sleep 2

# Test 4: Red Neuronal MLP
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 4: Red Neuronal MLP (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/red_neuronal.txt mlp parallel
echo ""
sleep 2

# Test 5: Procesamiento de Imágenes
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TEST 5: Procesamiento de Imágenes (Parallel)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 ejecutar.py mis_datos/imagen.txt image parallel
echo ""

echo "╔════════════════════════════════════════════════════╗"
echo "║  ✅ TODAS LAS PRUEBAS COMPLETADAS                 ║"
echo "╚════════════════════════════════════════════════════╝"
