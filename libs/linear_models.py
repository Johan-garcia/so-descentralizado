import math

class LinearRegression:
    def __init__(self):
        self.weights = []
        self.bias = 0.0

    def fit_from_content(self, content):
        """
        Entrena regresión lineal desde contenido CSV.
        Formato esperado: x1,x2,... ,xn,y
        """
        lines = [l.strip() for l in content.strip().split('\n') if l.strip() and not l.startswith('#')]
        
        if not lines:
            return {'status': 'error', 'msg': 'No data provided'}
        
        # Parsear datos
        X = []
        y = []
        
        for line in lines:
            try:
                values = [float(v.strip()) for v in line.split(',')]
                if len(values) < 2:
                    continue
                X.append(values[:-1])  # Todas menos la última columna
                y.append(values[-1])    # Última columna es el target
            except ValueError:
                continue
        
        if not X or not y:
            return {'status': 'error', 'msg': 'No valid data parsed'}
        
        n_samples = len(X)
        n_features = len(X[0])
        
        print(f" [LINEAR] 📊 Datos: {n_samples} muestras, {n_features} características")
        
        # ===== NORMALIZACIÓN (CRÍTICO PARA ESTABILIDAD) =====
        X_normalized = []
        means = [0.0] * n_features
        stds = [0.0] * n_features
        
        # Calcular medias
        for j in range(n_features):
            means[j] = sum(X[i][j] for i in range(n_samples)) / n_samples
        
        # Calcular desviaciones estándar
        for j in range(n_features):
            variance = sum((X[i][j] - means[j])**2 for i in range(n_samples)) / n_samples
            stds[j] = math.sqrt(variance) if variance > 0 else 1.0
        
        # Normalizar X
        for i in range(n_samples):
            normalized_row = []
            for j in range(n_features):
                normalized_val = (X[i][j] - means[j]) / stds[j] if stds[j] > 0 else 0.0
                normalized_row.append(normalized_val)
            X_normalized.append(normalized_row)
        
        X = X_normalized
        
        # Normalizar y
        y_mean = sum(y) / n_samples
        y_std = math.sqrt(sum((yi - y_mean)**2 for yi in y) / n_samples)
        y_std = y_std if y_std > 0 else 1.0
        y_normalized = [(yi - y_mean) / y_std for yi in y]
        
        # Inicializar pesos
        self.weights = [0.0] * n_features
        self.bias = 0.0
        
        # Hiperparámetros (CORREGIDOS)
        learning_rate = 0.01  # Reducido de 0.001 para estabilidad
        epochs = 1000
        
        # Gradient Descent
        for epoch in range(epochs):
            # Calcular predicciones
            predictions = []
            for i in range(n_samples):
                pred = self.bias
                for j in range(n_features):
                    pred += self.weights[j] * X[i][j]
                predictions.append(pred)
            
            # Calcular gradientes
            dw = [0.0] * n_features
            db = 0.0
            
            for i in range(n_samples):
                error = predictions[i] - y_normalized[i]
                db += error
                for j in range(n_features):
                    dw[j] += error * X[i][j]
            
            # Actualizar pesos
            for j in range(n_features):
                self.weights[j] -= learning_rate * (dw[j] / n_samples)
            self.bias -= learning_rate * (db / n_samples)
            
            # Calcular MSE cada 200 épocas
            if (epoch + 1) % 200 == 0:
                mse = sum((predictions[i] - y_normalized[i])**2 for i in range(n_samples)) / n_samples
                print(f" [LINEAR] Época {epoch+1}/{epochs} - MSE: {mse:.4f}")
        
        # Calcular MSE final en escala normalizada
        final_predictions = []
        for i in range(n_samples):
            pred = self.bias
            for j in range(n_features):
                pred += self.weights[j] * X[i][j]
            final_predictions.append(pred)
        
        mse_normalized = sum((final_predictions[i] - y_normalized[i])**2 for i in range(n_samples)) / n_samples
        rmse_normalized = math.sqrt(mse_normalized)
        
        # Desnormalizar para métricas reales
        final_predictions_real = [pred * y_std + y_mean for pred in final_predictions]
        mse_real = sum((final_predictions_real[i] - y[i])**2 for i in range(n_samples)) / n_samples
        rmse_real = math.sqrt(mse_real)
        
        print(f" [LINEAR] ✅ Entrenamiento completado - RMSE: {rmse_real:.4f}")
        
        return {
            'status': 'success',
            'weights': self.weights,
            'bias': self.bias,
            'mse': mse_real,
            'rmse': rmse_real,
            'n_samples': n_samples,
            'n_features': n_features
        }


class DecisionTree:
    def __init__(self):
        self.tree = None

    def fit_from_content(self, content):
        """Árbol de decisión básico"""
        lines = [l.strip() for l in content.strip().split('\n') if l.strip() and not l.startswith('#')]
        
        if not lines:
            return {'status': 'error', 'msg': 'No data provided'}
        
        # Parse simple
        X = []
        y = []
        
        for line in lines:
            try:
                values = [float(v.strip()) for v in line.split(',')]
                if len(values) < 2:
                    continue
                X.append(values[:-1])
                y.append(values[-1])
            except ValueError:
                continue
        
        if not X:
            return {'status': 'error', 'msg': 'No valid data'}
        
        print(f" [TREE] 🌳 Datos: {len(X)} muestras")
        
        # Árbol simple: usar promedio como predicción
        avg = sum(y) / len(y)
        
        return {
            'status': 'success',
            'tree_prediction': avg,
            'n_samples': len(X)
        }
