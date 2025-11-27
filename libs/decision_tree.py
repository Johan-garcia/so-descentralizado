import math

class DecisionTree:
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
        self.n_features = 0
        self.n_classes = 0

    def fit_from_content(self, content):
        """
        Entrena árbol de decisión desde CSV. 
        Formato: x1,x2,... ,xn,y
        """
        lines = [l.strip() for l in content. strip().split('\n') 
                if l.strip() and not l.startswith('#')]
        
        if not lines:
            return {'status': 'error', 'msg': 'No data provided'}
        
        # Parsear datos
        X = []
        y = []
        
        for line in lines:
            try:
                values = [float(v. strip()) for v in line.split(',')]
                if len(values) < 2:
                    continue
                X.append(values[:-1])
                y.append(int(values[-1]))
            except (ValueError, IndexError):
                continue
        
        if not X or not y:
            return {'status': 'error', 'msg': 'No valid data'}
        
        n_samples = len(X)
        self.n_features = len(X[0])
        self.n_classes = max(y) + 1
        
        print(f" [TREE] 🌳 Datos: {n_samples} muestras, {self.n_features} features, {self.n_classes} clases")
        
        # Construir árbol
        self.tree = self._build_tree(X, y, depth=0)
        
        # Calcular accuracy en training set
        correct = 0
        for i in range(n_samples):
            pred = self.predict_single(X[i])
            if pred == y[i]:
                correct += 1
        
        accuracy = correct / n_samples
        
        print(f" [TREE] ✅ Árbol construido - Profundidad: {self._get_depth(self.tree)} - Accuracy: {accuracy*100:.2f}%")
        
        return {
            'status': 'success',
            'tree': self._serialize_tree(self.tree),
            'accuracy': accuracy,
            'n_samples': n_samples,
            'n_features': self. n_features,
            'n_classes': self.n_classes,
            'max_depth': self.max_depth
        }

    def _build_tree(self, X, y, depth):
        """Construye el árbol recursivamente"""
        n_samples = len(y)
        n_classes_here = len(set(y))
        
        # Condiciones de parada
        if (depth >= self.max_depth or 
            n_classes_here == 1 or 
            n_samples < self.min_samples_split):
            return self._create_leaf(y)
        
        # Encontrar mejor split
        best_feature, best_threshold = self._best_split(X, y)
        
        if best_feature is None:
            return self._create_leaf(y)
        
        # Dividir datos
        left_indices = []
        right_indices = []
        
        for i in range(n_samples):
            if X[i][best_feature] <= best_threshold:
                left_indices.append(i)
            else:
                right_indices. append(i)
        
        # Si no hay split útil
        if len(left_indices) == 0 or len(right_indices) == 0:
            return self._create_leaf(y)
        
        # Crear subconjuntos
        X_left = [X[i] for i in left_indices]
        y_left = [y[i] for i in left_indices]
        X_right = [X[i] for i in right_indices]
        y_right = [y[i] for i in right_indices]
        
        # Recursión
        left_subtree = self._build_tree(X_left, y_left, depth + 1)
        right_subtree = self._build_tree(X_right, y_right, depth + 1)
        
        return {
            'type': 'split',
            'feature': best_feature,
            'threshold': best_threshold,
            'left': left_subtree,
            'right': right_subtree
        }

    def _create_leaf(self, y):
        """Crea un nodo hoja con la clase mayoritaria"""
        # Contar clases
        counts = {}
        for label in y:
            counts[label] = counts.get(label, 0) + 1
        
        # Encontrar clase mayoritaria
        majority_class = max(counts, key=counts.get)
        
        return {
            'type': 'leaf',
            'class': majority_class,
            'samples': len(y),
            'distribution': counts
        }

    def _best_split(self, X, y):
        """Encuentra el mejor split usando Gini impurity"""
        n_samples = len(y)
        if n_samples <= 1:
            return None, None
        
        # Gini inicial
        parent_gini = self._gini_impurity(y)
        
        best_gain = 0.0
        best_feature = None
        best_threshold = None
        
        # Probar cada feature
        for feature_idx in range(self.n_features):
            # Obtener valores únicos ordenados
            values = sorted(set(X[i][feature_idx] for i in range(n_samples)))
            
            # Probar thresholds entre valores consecutivos
            for i in range(len(values) - 1):
                threshold = (values[i] + values[i + 1]) / 2. 0
                
                # Dividir datos
                y_left = []
                y_right = []
                
                for j in range(n_samples):
                    if X[j][feature_idx] <= threshold:
                        y_left.append(y[j])
                    else:
                        y_right.append(y[j])
                
                if len(y_left) == 0 or len(y_right) == 0:
                    continue
                
                # Calcular Gini ponderado
                n_left = len(y_left)
                n_right = len(y_right)
                
                gini_left = self._gini_impurity(y_left)
                gini_right = self._gini_impurity(y_right)
                
                weighted_gini = (n_left / n_samples) * gini_left + (n_right / n_samples) * gini_right
                
                # Calcular ganancia de información
                gain = parent_gini - weighted_gini
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_idx
                    best_threshold = threshold
        
        return best_feature, best_threshold

    def _gini_impurity(self, y):
        """Calcula el índice de Gini"""
        n_samples = len(y)
        if n_samples == 0:
            return 0.0
        
        # Contar clases
        counts = {}
        for label in y:
            counts[label] = counts.get(label, 0) + 1
        
        # Calcular Gini
        gini = 1.0
        for count in counts.values():
            prob = count / n_samples
            gini -= prob * prob
        
        return gini

    def predict_single(self, x):
        """Predice una sola muestra"""
        node = self.tree
        
        while node['type'] != 'leaf':
            if x[node['feature']] <= node['threshold']:
                node = node['left']
            else:
                node = node['right']
        
        return node['class']

    def _get_depth(self, node):
        """Calcula la profundidad del árbol"""
        if node['type'] == 'leaf':
            return 1
        
        left_depth = self._get_depth(node['left'])
        right_depth = self._get_depth(node['right'])
        
        return 1 + max(left_depth, right_depth)

    def _serialize_tree(self, node):
        """Serializa el árbol para transmisión"""
        if node['type'] == 'leaf':
            return {
                'type': 'leaf',
                'class': node['class'],
                'samples': node['samples']
            }
        
        return {
            'type': 'split',
            'feature': node['feature'],
            'threshold': node['threshold'],
            'left': self._serialize_tree(node['left']),
            'right': self._serialize_tree(node['right'])
        }
