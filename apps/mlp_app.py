from libs.mlp import MLP

class MLPApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def run_task(self, task_data):
        """
        Entrena una red neuronal MLP. 
        Recibe: { 'file_content': '...' }
        """
        content = task_data.get('file_content')
        
        if not content:
            return {'status': 'error', 'msg': 'No file content provided'}

        print(f" [MLP APP] Ejecutando Red Neuronal...")

        # El MLP se instanciará dentro del método fit_from_content
        # que detectará automáticamente el tamaño de entrada y salida
        model = MLP(input_size=4, hidden_size=5, output_size=3)  # Valores por defecto
        result = model.fit_from_content(content)
        
        # Añadir quién lo ejecutó
        result['executed_by'] = self.node_id
        return result
