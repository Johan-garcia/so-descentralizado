import math
import time

class LogisticRegression:
    def __init__(self, learning_rate=0.1, iterations=1000):
        self.lr = learning_rate
        self.iters = iterations
        self.weights = []
        self.bias = 0.0

    def _sigmoid(self, z):
        # Evitar overflow
        if z < -709: return 0.0
        if z > 709: return 1.0
        return 1.0 / (1.0 + math.exp(-z))

    def _parse_content(self, file_content):
        X, y = [], []
        lines = file_content.strip().split('\n')
        for line in lines:
            parts = line.split(',')
            try:
                vals = [float(p) for p in parts]
                X.append(vals[:-1])
                y.append(vals[-1])
            except: continue
        return X, y

    def fit_from_content(self, file_content):
        X, y = self._parse_content(file_content)
        if not X: return {'status': 'error', 'msg': 'No data'}

        print(f" [MATH] 📉 Entrenando Regresión Logística ({len(X)} muestras)...")
        time.sleep(5) # Simular carga pesada para ver paralelismo

        n_samples = len(X)
        n_features = len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0

        # Descenso de Gradiente
        for _ in range(self.iters):
            dw = [0.0] * n_features
            db = 0.0
            
            for i in range(n_samples):
                # 1. Predicción Lineal: z = w*x + b
                linear_model = sum(X[i][j] * self.weights[j] for j in range(n_features)) + self.bias
                # 2. Activación: y_pred = sigmoid(z)
                y_predicted = self._sigmoid(linear_model)
                
                # 3. Calculo de Gradientes
                diff = y_predicted - y[i]
                for j in range(n_features):
                    dw[j] += (1 / n_samples) * X[i][j] * diff
                db += (1 / n_samples) * diff

            # 4. Actualizar Pesos
            for j in range(n_features):
                self.weights[j] -= self.lr * dw[j]
            self.bias -= self.lr * db

        return {
            "status": "success",
            "weights": self.weights,
            "bias": self.bias,
            "algorithm": "LogisticRegression"
        }
