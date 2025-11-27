import numpy as np
from libs.linear_regression import LinearRegression

class DistributedMLTraining:
    def __init__(self, node_id, discovery, api):
        self.node_id = node_id
        self.api = api
        self.api.register_handler('TRAIN', self.handle_train)
        
    def handle_train(self, data):
        print(f"[APP] Training request received")
        X = np.array(data['X'])
        y = np.array(data['y'])
        
        model = LinearRegression()
        model.fit(X, y)
        
        return {
            'weights': model.weights.tolist(),
            'bias': model.bias,
            'trained_by': self.node_id
        }
