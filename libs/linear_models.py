import math

class LinearRegression:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.lr = learning_rate
        self.iters = iterations
        self.weights = []
        self.bias = 0.0

    def _parse_content(self, file_content):
        """
        Convierte el contenido de texto crudo en matrices numéricas X e y.
        Soporta formato CSV: 1.0, 2.5, 3.0 (Donde 3.0 es la etiqueta Y)
        """
        X = []
        y = []
        
        # Dividir por líneas y limpiar espacios
        lines = file_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Ignorar líneas vacías o encabezados con texto
            if not line or line[0].isalpha():
                continue
                
            parts = line.split(',')
            # Convertir a flotantes
            try:
                values = [float(p) for p in parts]
                # Asumimos que el último valor es la etiqueta (y)
                X.append(values[:-1]) 
                y.append(values[-1])
            except ValueError:
                continue # Saltar líneas con errores de formato

        return X, y

    def fit(self, X, y):
        """Entrenamiento matemático puro (Listas nativas de Python para no depender de numpy)"""
        n_samples = len(X)
        if n_samples == 0: return {"error": "No data"}
        n_features = len(X[0])
        
        # Inicializar pesos
        self.weights = [0.0] * n_features
        self.bias = 0.0

        for _ in range(self.iters):
            # Predicción y cálculo de gradientes
            dw = [0.0] * n_features
            db = 0.0
            
            for i in range(n_samples):
                # Predicción lineal: y = wx + b
                prediction = sum(x_i * w_i for x_i, w_i in zip(X[i], self.weights)) + self.bias
                error = prediction - y[i]
                
                # Acumular gradientes
                for j in range(n_features):
                    dw[j] += (1 / n_samples) * X[i][j] * error
                db += (1 / n_samples) * error

            # Actualizar pesos
            for j in range(n_features):
                self.weights[j] -= self.lr * dw[j]
            self.bias -= self.lr * db
            
        return {
            "status": "trained",
            "weights": self.weights,
            "bias": self.bias
        }

    def fit_from_content(self, file_content):
        """Método principal para llamar desde la App con el TXT"""
        try:
            X, y = self._parse_content(file_content)
            if not X:
                return {"status": "error", "msg": "No valid numeric data found in file"}
            
            return self.fit(X, y)
        except Exception as e:
            return {"status": "error", "msg": str(e)}
