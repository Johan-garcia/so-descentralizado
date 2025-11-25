from libs.linear_models import LinearRegression
from libs.decision_tree import DecisionTree

class MLApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def run_task(self, task_data):
        """
        Manejador principal.
        Recibe: { 'algorithm': 'linear', 'file_content': '...' }
        """
        algo = task_data.get('algorithm')
        content = task_data.get('file_content')
        
        if not content:
            return {'status': 'error', 'msg': 'No file content provided'}

        print(f" [ML APP] 🚀 Ejecutando algoritmo: {algo}")

        if algo == 'linear':
            model = LinearRegression()
            # Llamamos al método inteligente que creamos antes
            result = model.fit_from_content(content)
            
            # Añadimos quién lo ejecutó
            result['executed_by'] = self.node_id
            return result

        elif algo == 'tree':
            model = DecisionTree()
            result = model.fit_from_content(content)
            result['executed_by'] = self.node_id
            return result
            
        else:
            return {'status': 'error', 'msg': f'Unknown algorithm: {algo}'}
