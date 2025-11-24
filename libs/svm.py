import numpy as np

class CustomSVM:
    def __init__(self, lr=0.001, lambda_param=0.01, iters=1000):
        self.lr = lr
        self.lambda_param = lambda_param
        self.iters = iters
        self.w = None
        self.b = None

    def fit(self, X, y):
        # Asegurar que y sea -1 o 1
        y_ = np.where(y <= 0, -1, 1)
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features)
        self.b = 0

        for _ in range(self.iters):
            for idx, x_i in enumerate(X):
                condition = y_[idx] * (np.dot(x_i, self.w) - self.b) >= 1
                if condition:
                    self.w -= self.lr * (2 * self.lambda_param * self.w)
                else:
                    self.w -= self.lr * (2 * self.lambda_param * self.w - np.dot(x_i, y_[idx]))
                    self.b -= self.lr * y_[idx]

    def predict(self, X):
        approx = np.dot(X, self.w) - self.b
        return np.sign(approx)
