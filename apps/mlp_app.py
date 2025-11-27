from libs.mlp import MLP

class MLPApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def run_task(self, task_data):
        content = task_data.get('file_content')
        if not content: return {'status': 'error', 'msg': 'No content'}

        print(f" [MLP APP] 🧠 Ejecutando Red Neuronal...")
        # Instanciamos el MLP hecho a mano
        model = MLP(hidden_size=5) 
        result = model.fit_from_content(content)
        result['executed_by'] = self.node_id
        return result
