import numpy as np

class ImageApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def process(self, data):
        # data: {'image': [[...]], 'op': 'invert'}
        img = np.array(data['image'])
        
        if data['op'] == 'invert':
            processed = 255 - img
            return {'image': processed.tolist()}
        
        return {'error': 'unknown op'}
