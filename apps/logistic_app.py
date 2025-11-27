from libs.logistic_regression import LogisticRegression

class LogisticApp:
    def __init__(self, node_id):
        self.node_id = node_id

    def run_task(self, task_data):
        content = task_data.get('file_content')
        if not content: return {'status': 'error', 'msg': 'No content'}
        
        print(f" [LOGISTIC APP] 🚀 Ejecutando Regresión Logística...")
        model = LogisticRegression()
        result = model.fit_from_content(content)
        result['executed_by'] = self.node_id
        return result
