import math

class LogisticRegression:
    def __init__(self):
        self.weights = []
        self.bias = 0. 0

    def sigmoid(self, z):
        """Función sigmoide con protección contra overflow"""
        if z > 20:
            return 1.0
        elif z < -20:
            return 0.0
        return 1.0 / (1.0 + math.exp(-z))

    def fit_from_content(self, content):
        """
        Entrena regresión logística desde contenido CSV.
        Formato: x1,x2,...,xn,y (y debe ser 0 o 1)
        """
        lines = [l.strip() for l in content.strip().split('\n') if l.strip() and not l. startswith('#')]
        
        if not lines:
            return {'status': 'error', 'msg': 'No data provided'}
        
        X = []
        y = []
        
        for line in lines:
            try:
                values = [float(v.strip()) for v in line.split(',')]
                if len(values) < 2:
                    continue
                X.append(values[:-1])
                y.append(int(values[-1]))
            except (ValueError, IndexError):
                continue
        
        if not X or not y:
            return {'status': 'error', 'msg': 'No valid data parsed'}
        
        n_samples = len(X)
        n_features = len(X[0])
        
        print(f" [LOGISTIC] 📊 Datos: {n_samples} muestras, {n_features} características")
        
        # Normalizar características (importante para logística)
        X_normalized = []
        means = [0.0] * n_features
        stds = [0.0] * n_features
        
        # Calcular medias
        for j in range(n_features):
            means[j] = sum(X[i][j] for i in range(n_samples)) / n_samples
        
        # Calcular desviaciones estándar
        for j in range(n_features):
            variance = sum((X[i][j] - means[j])**2 for i in range(n_samples)) / n_samples
            stds[j] = math. sqrt(variance) if variance > 0 else 1.0
        
        # Normalizar
        for i in range(n_samples):
            normalized_row = []
            for j in range(n_features):
                normalized_val = (X[i][j] - means[j]) / stds[j] if stds[j] > 0 else 0.0
                normalized_row.append(normalized_val)
            X_normalized.append(normalized_row)
        
        X = X_normalized
        
        # Inicializar pesos
        self.weights = [0.0] * n_features
        self.bias = 0. 0
        
        # Hiperparámetros
        learning_rate = 0.1
        epochs = 200
        
        # Gradient Descent
        for epoch in range(epochs):
            # Predicciones
            predictions = []
            for i in range(n_samples):
                z = self.bias
                for j in range(n_features):
                    z += self.weights[j] * X[i][j]
                predictions.append(self.sigmoid(z))
            
            # Calcular gradientes
            dw = [0.0] * n_features
            db = 0.0
            
            for i in range(n_samples):
                error = predictions[i] - y[i]
                db += error
                for j in range(n_features):
                    dw[j] += error * X[i][j]
            
            # Actualizar pesos
            for j in range(n_features):
                self.weights[j] -= learning_rate * (dw[j] / n_samples)
            self.bias -= learning_rate * (db / n_samples)
            
            # Log cada 50 épocas
            if (epoch + 1) % 50 == 0:
                loss = -sum(
                    y[i] * math.log(predictions[i] + 1e-10) + 
                    (1 - y[i]) * math.log(1 - predictions[i] + 1e-10)
                    for i in range(n_samples)
                ) / n_samples
                print(f" [LOGISTIC] Época {epoch+1}/{epochs} - Loss: {loss:.4f}")
        
        # Calcular accuracy final
        correct = 0
        for i in range(n_samples):
            z = self.bias
            for j in range(n_features):
                z += self.weights[j] * X[i][j]
            pred_class = 1 if self.sigmoid(z) >= 0.5 else 0
            if pred_class == y[i]:
                correct += 1
        
        accuracy = correct / n_samples
        
        print(f" [LOGISTIC] ✅ Entrenamiento completado - Accuracy: {accuracy*100:.2f}%")
        
        return {
            'status': 'success',
            'weights': self.weights,
            'bias': self.bias,
            'accuracy': accuracy,
            'n_samples': n_samples,
            'n_features': n_features
        }
