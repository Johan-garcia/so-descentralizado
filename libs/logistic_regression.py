#!/usr/bin/env python3
"""
Implementación propia de Regresión Logística
"""
import numpy as np

class LogisticRegression:
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
        self.losses = []
        
    def sigmoid(self, z):
        """Función sigmoide"""
        return 1 / (1 + np.exp(-z))
        
    def fit(self, X, y):
        """
        Entrena el modelo
        X: matriz de features (n_samples, n_features)
        y: vector de targets binarios (n_samples,)
        """
        n_samples, n_features = X.shape
        
        # Inicializar parámetros
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        # Gradient Descent
        for i in range(self.n_iterations):
            # Predicción
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)
            
            # Calcular gradientes
            dw = (1/n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1/n_samples) * np.sum(y_predicted - y)
            
            # Actualizar parámetros
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            # Calcular loss (Binary Cross-Entropy)
            if i % 100 == 0:
                loss = -np.mean(y * np.log(y_predicted + 1e-15) + 
                               (1 - y) * np.log(1 - y_predicted + 1e-15))
                self.losses.append(loss)
                
        return self
        
    def predict(self, X, threshold=0.5):
        """Realiza predicciones binarias"""
        linear_model = np.dot(X, self.weights) + self.bias
        y_predicted = self.sigmoid(linear_model)
        return (y_predicted >= threshold).astype(int)
        
    def predict_proba(self, X):
        """Retorna probabilidades"""
        linear_model = np.dot(X, self.weights) + self.bias
        return self.sigmoid(linear_model)
        
    def accuracy(self, X, y):
        """Calcula accuracy"""
        predictions = self.predict(X)
        return np.mean(predictions == y)

# Test
if __name__ == "__main__":
    # Datos de ejemplo (clasificación binaria)
    X = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])
    y = np.array([0, 0, 0, 1, 1, 1])
    
    model = LogisticRegression(learning_rate=0.1, n_iterations=1000)
    model.fit(X, y)
    
    predictions = model.predict(X)
    accuracy = model.accuracy(X, y)
    
    print(f"Predictions: {predictions}")
    print(f"Accuracy: {accuracy:.4f}")
