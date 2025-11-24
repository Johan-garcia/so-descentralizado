#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Usage: ./start_node.sh <node_id> <node_ip>"
    exit 1
fi

NODE_ID=$1
NODE_IP=$2

echo "Starting node $NODE_ID ($NODE_IP)..."

cd /home/ubuntu/so-descentralizado
mkdir -p logs

# Iniciar discovery
python3 network/discovery.py $NODE_ID $NODE_IP > logs/discovery.log 2>&1 &
echo "Discovery service started (PID: $!)"

echo "Node $NODE_ID started!"
echo "Check logs: tail -f logs/discovery.log"
