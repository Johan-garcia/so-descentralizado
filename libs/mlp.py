import numpy as np

class CustomMLP:
    def __init__(self, input_size, hidden_size, output_size, lr=0.1):
        # Inicialización aleatoria de pesos
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        self.lr = lr

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    def fit(self, X, y, epochs=1000):
        m = X.shape[0]
        y = y.reshape(-1, 1)
        
        for _ in range(epochs):
            # Forward
            Z1 = np.dot(X, self.W1) + self.b1
            A1 = self.sigmoid(Z1)
            Z2 = np.dot(A1, self.W2) + self.b2
            A2 = self.sigmoid(Z2)
            
            # Backprop
            dZ2 = A2 - y
            dW2 = (1/m) * np.dot(A1.T, dZ2)
            db2 = (1/m) * np.sum(dZ2, axis=0, keepdims=True)
            
            dZ1 = np.dot(dZ2, self.W2.T) * (A1 * (1 - A1))
            dW1 = (1/m) * np.dot(X.T, dZ1)
            db1 = (1/m) * np.sum(dZ1, axis=0, keepdims=True)
            
            # Update
            self.W1 -= self.lr * dW1
            self.b1 -= self.lr * db1
            self.W2 -= self.lr * dW2
            self.b2 -= self.lr * db2

    def predict(self, X):
        Z1 = np.dot(X, self.W1) + self.b1
        A1 = self.sigmoid(Z1)
        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = self.sigmoid(Z2)
        return (A2 > 0.5).astype(int)
