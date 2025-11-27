import math
import random

class MLP:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Inicializar pesos con Xavier initialization
        limit_ih = math.sqrt(6.0 / (input_size + hidden_size))
        limit_ho = math.sqrt(6.0 / (hidden_size + output_size))
        
        self.W1 = [[random.uniform(-limit_ih, limit_ih) for _ in range(hidden_size)] 
                   for _ in range(input_size)]
        self.b1 = [0.0] * hidden_size
        
        self.W2 = [[random.uniform(-limit_ho, limit_ho) for _ in range(output_size)] 
                   for _ in range(hidden_size)]
        self.b2 = [0.0] * output_size

    def sigmoid(self, x):
        if x > 20: return 1.0
        if x < -20: return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1.0 - x)

    def forward(self, X):
        """Forward pass"""
        # Input -> Hidden
        hidden = []
        for j in range(self.hidden_size):
            z = self.b1[j]
            for i in range(self.input_size):
                z += X[i] * self.W1[i][j]
            hidden.append(self.sigmoid(z))
        
        # Hidden -> Output
        output = []
        for k in range(self.output_size):
            z = self.b2[k]
            for j in range(self.hidden_size):
                z += hidden[j] * self.W2[j][k]
            output.append(self.sigmoid(z))
        
        return hidden, output

    def train(self, X_train, y_train, epochs=100, learning_rate=0.1):
        """Entrenamiento con backpropagation"""
        n_samples = len(X_train)
        
        for epoch in range(epochs):
            total_loss = 0.0
            
            for sample_idx in range(n_samples):
                X = X_train[sample_idx]
                y_true = y_train[sample_idx]
                
                # Forward
                hidden, output = self.forward(X)
                
                # Calcular loss (MSE)
                loss = 0.0
                for k in range(self.output_size):
                    target = 1.0 if y_true == k else 0.0
                    loss += (output[k] - target) ** 2
                total_loss += loss
                
                # Backward
                # Output layer gradients
                output_deltas = []
                for k in range(self.output_size):
                    target = 1.0 if y_true == k else 0.0
                    error = output[k] - target
                    delta = error * self.sigmoid_derivative(output[k])
                    output_deltas.append(delta)
                
                # Hidden layer gradients
                hidden_deltas = []
                for j in range(self.hidden_size):
                    error = sum(output_deltas[k] * self.W2[j][k] 
                               for k in range(self.output_size))
                    delta = error * self.sigmoid_derivative(hidden[j])
                    hidden_deltas.append(delta)
                
                # Update W2 and b2
                for j in range(self.hidden_size):
                    for k in range(self.output_size):
                        self.W2[j][k] -= learning_rate * output_deltas[k] * hidden[j]
                
                for k in range(self.output_size):
                    self.b2[k] -= learning_rate * output_deltas[k]
                
                # Update W1 and b1
                for i in range(self.input_size):
                    for j in range(self.hidden_size):
                        self.W1[i][j] -= learning_rate * hidden_deltas[j] * X[i]
                
                for j in range(self.hidden_size):
                    self.b1[j] -= learning_rate * hidden_deltas[j]
            
            avg_loss = total_loss / n_samples
            
            if (epoch + 1) % 20 == 0:
                print(f" [MLP] Época {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
        
        return avg_loss

    def fit_from_content(self, content):
        """Entrenar desde CSV"""
        lines = [l.strip() for l in content.strip().split('\n') 
                if l.strip() and not l.startswith('#')]
        
        if not lines:
            return {'status': 'error', 'msg': 'No data provided'}
        
        X_train = []
        y_train = []
        
        for line in lines:
            try:
                values = [float(v.strip()) for v in line.split(',')]
                if len(values) < 2:
                    continue
                X_train.append(values[:-1])
                y_train.append(int(values[-1]))
            except (ValueError, IndexError):
                continue
        
        if not X_train:
            return {'status': 'error', 'msg': 'No valid data'}
        
        n_samples = len(X_train)
        n_features = len(X_train[0])
        n_classes = max(y_train) + 1
        
        print(f" [MLP] 🧠 Datos: {n_samples} muestras, {n_features} features, {n_classes} clases")
        
        # Normalizar
        means = [sum(X_train[i][j] for i in range(n_samples)) / n_samples 
                for j in range(n_features)]
        stds = []
        for j in range(n_features):
            var = sum((X_train[i][j] - means[j])**2 for i in range(n_samples)) / n_samples
            stds.append(math.sqrt(var) if var > 0 else 1.0)
        
        X_normalized = []
        for i in range(n_samples):
            row = [(X_train[i][j] - means[j]) / stds[j] if stds[j] > 0 else 0.0
                   for j in range(n_features)]
            X_normalized.append(row)
        
        # Reinitializar red con tamaños correctos
        self.__init__(n_features, 5, n_classes)
        
        # Entrenar
        final_loss = self.train(X_normalized, y_train, epochs=100, learning_rate=0.1)
        
        print(f" [MLP] ✅ Entrenamiento completado")
        
        return {
            'status': 'success',
            'input_to_hidden_w': self.W1,
            'hidden_bias': self.b1,
            'hidden_to_output_w': self.W2,
            'output_bias': self.b2,
            'final_loss': final_loss,
            'n_samples': n_samples,
            'n_classes': n_classes
        }
