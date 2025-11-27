from libs.decision_tree import DecisionTree

class DecisionTreeApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def run_task(self, task_data):
        """
        Entrena un árbol de decisión. 
        Recibe: { 'file_content': '... ', 'max_depth': 5 }
        """
        content = task_data.get('file_content')
        max_depth = task_data.get('max_depth', 5)
        
        if not content:
            return {'status': 'error', 'msg': 'No file content provided'}

        print(f" [TREE APP] 🌳 Ejecutando Árbol de Decisión (max_depth={max_depth})...")

        model = DecisionTree(max_depth=max_depth, min_samples_split=2)
        result = model.fit_from_content(content)
        
        # Añadir quién lo ejecutó
        result['executed_by'] = self.node_id
        return result
