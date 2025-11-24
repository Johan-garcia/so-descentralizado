import numpy as np
from libs.linear_models import CustomLinearRegression
from libs.mlp import CustomMLP

class MLApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def train(self, data):
        # data: {'model': 'linear', 'X': [...], 'y': [...]}
        X = np.array(data['X'])
        y = np.array(data['y'])
        
        if data['model'] == 'linear':
            model = CustomLinearRegression()
            model.fit(X, y)
            return {'weights': model.weights.tolist(), 'bias': model.bias}
        
        elif data['model'] == 'mlp':
            # Ejemplo simple MLP
            model = CustomMLP(input_size=len(X[0]), hidden_size=4, output_size=1)
            model.fit(X, y, epochs=100)
            # Retornamos éxito (pesos muy grandes para JSON simple)
            return {'status': 'trained', 'model': 'mlp'}
            
        return {'error': 'unknown model'}
