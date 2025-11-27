import math
import random
import time

class MLP:
    def __init__(self, input_size=2, hidden_size=4, output_size=1, learning_rate=0.1, epochs=500):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lr = learning_rate
        self.epochs = epochs
        
        # Inicialización aleatoria de pesos (Matriz W1 y W2)
        # W1: input x hidden
        self.W1 = [[random.uniform(-0.5, 0.5) for _ in range(hidden_size)] for _ in range(input_size)]
        self.b1 = [0.0] * hidden_size
        
        # W2: hidden x output
        self.W2 = [[random.uniform(-0.5, 0.5) for _ in range(output_size)] for _ in range(hidden_size)]
        self.b2 = [0.0] * output_size

    def _sigmoid(self, x):
        return 1.0 / (1.0 + math.exp(-x))

    def _sigmoid_derivative(self, x):
        return x * (1.0 - x)

    def fit_from_content(self, file_content):
        # Parsear CSV
        X = []
        y = []
        lines = file_content.strip().split('\n')
        for line in lines:
            try:
                parts = [float(p) for p in line.split(',')]
                X.append(parts[:-1])
                y.append([parts[-1]]) # Output debe ser lista
            except: continue

        if not X: return {'status': 'error', 'msg': 'No data'}
        
        # Ajustar tamaño de entrada dinámicamente
        self.input_size = len(X[0])
        # Reinicializar W1 si cambió el tamaño de entrada
        if len(self.W1) != self.input_size:
             self.W1 = [[random.uniform(-0.5, 0.5) for _ in range(self.hidden_size)] for _ in range(self.input_size)]

        print(f" [MATH] 🧠 Entrenando MLP (Backpropagation manual)...")
        time.sleep(5) # Para prueba de paralelismo

        for epoch in range(self.epochs):
            for i in range(len(X)):
                # --- FORWARD PASS ---
                # 1. Hidden Layer
                hidden_inputs = [0.0] * self.hidden_size
                for h in range(self.hidden_size):
                    val = sum(X[i][In] * self.W1[In][h] for In in range(self.input_size)) + self.b1[h]
                    hidden_inputs[h] = self._sigmoid(val)
                
                # 2. Output Layer
                final_outputs = [0.0] * self.output_size
                for o in range(self.output_size):
                    val = sum(hidden_inputs[h] * self.W2[h][o] for h in range(self.hidden_size)) + self.b2[o]
                    final_outputs[o] = self._sigmoid(val)

                # --- BACKPROPAGATION ---
                # Error Output
                expected = y[i]
                output_errors = [expected[o] - final_outputs[o] for o in range(self.output_size)]
                output_deltas = [output_errors[o] * self._sigmoid_derivative(final_outputs[o]) for o in range(self.output_size)]

                # Error Hidden
                hidden_errors = [0.0] * self.hidden_size
                for h in range(self.hidden_size):
                    error = sum(output_deltas[o] * self.W2[h][o] for o in range(self.output_size))
                    hidden_errors[h] = error * self._sigmoid_derivative(hidden_inputs[h])

                # Actualizar W2 y b2
                for o in range(self.output_size):
                    self.b2[o] += output_deltas[o] * self.lr
                    for h in range(self.hidden_size):
                        self.W2[h][o] += hidden_inputs[h] * output_deltas[o] * self.lr
                
                # Actualizar W1 y b1
                for h in range(self.hidden_size):
                    self.b1[h] += hidden_errors[h] * self.lr
                    for In in range(self.input_size):
                        self.W1[In][h] += X[i][In] * hidden_errors[h] * self.lr

        return {
            "status": "success",
            "input_to_hidden_w": self.W1,
            "hidden_bias": self.b1,
            "hidden_to_output_w": self.W2,
            "output_bias": self.b2
        }
