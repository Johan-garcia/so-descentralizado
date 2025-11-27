from libs.image_processor import ImageProcessor

class ImageApp:
    def __init__(self, node_id):
        self.node_id = node_id
        self.processor = ImageProcessor()

    def process(self, task_data):
        content = task_data.get('file_content')
        op = task_data.get('operation', 'invert')
        
        print(f" [IMG APP] Procesando imagen: {op}")
        
        if not content:
            return {'status': 'error', 'msg': 'No image content'}

        result = self.processor.process_from_content(content, op)
        result['executed_by'] = self.node_id
        return result
