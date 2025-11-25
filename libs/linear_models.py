import math
import time

class LinearRegression:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.lr = learning_rate
        self.iters = iterations
        self.weights = []
        self.bias = 0.0

    def _parse_content(self, file_content):
        """Convierte texto CSV crudo en matrices X e y"""
        X = []
        y = []
        lines = file_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line[0].isalpha(): continue
            
            parts = line.split(',')
            try:
                values = [float(p) for p in parts]
                X.append(values[:-1]) 
                y.append(values[-1])
            except ValueError: continue
            
        return X, y

    def fit(self, X, y):
        """Entrenamiento con simulación de carga pesada"""
        
        # --- PRUEBA DE PARALELISMO ---
        print(f" [MATH] ⏳ Iniciando 'Cálculo Pesado'. Durmiendo 5s...", flush=True)
        time.sleep(5) # Si es paralelo, el tiempo total será ~5s. Si es secuencial, será ~15s.
        # -----------------------------

        n_samples = len(X)
        if n_samples == 0: return {"status": "error", "msg": "No data"}
        n_features = len(X[0])
        
        self.weights = [0.0] * n_features
        self.bias = 0.0

        for _ in range(self.iters):
            dw = [0.0] * n_features
            db = 0.0
            
            for i in range(n_samples):
                prediction = sum(x_i * w_i for x_i, w_i in zip(X[i], self.weights)) + self.bias
                error = prediction - y[i]
                
                for j in range(n_features):
                    dw[j] += (1 / n_samples) * X[i][j] * error
                db += (1 / n_samples) * error

            for j in range(n_features):
                self.weights[j] -= self.lr * dw[j]
            self.bias -= self.lr * db
            
        # RETORNO CON STATUS "success" (Arregla el error "All nodes failed")
        return {
            "status": "success", 
            "weights": self.weights,
            "bias": self.bias
        }

    def fit_from_content(self, file_content):
        try:
            X, y = self._parse_content(file_content)
            if not X: return {"status": "error", "msg": "No valid data"}
            if len(X) < 2: return {"status": "error", "msg": "Need at least 2 rows of data"}
            
            return self.fit(X, y)
        except Exception as e:
            return {"status": "error", "msg": str(e)}
