import random
import math

class DecisionTree:
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.tree = None

    def _parse_content(self, file_content):
        """Lee CSV: caracteristica1, caracteristica2, ..., clase"""
        X = []
        y = []
        lines = file_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line[0].isalpha(): continue
            parts = line.split(',')
            try:
                vals = [float(p) for p in parts]
                X.append(vals[:-1])
                y.append(int(vals[-1])) # La clase debe ser entero
            except: continue
        return X, y

    def fit(self, X, y):
        self.tree = self._build_tree(X, y, depth=0)
        return {"status": "trained", "depth": self.max_depth, "msg": "Tree structure created in memory"}

    def fit_from_content(self, file_content):
        try:
            X, y = self._parse_content(file_content)
            if not X: return {"status": "error", "msg": "No valid data"}
            return self.fit(X, y)
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    # --- Lógica interna del Árbol (Simplificada) ---
    def _build_tree(self, X, y, depth):
        n_samples = len(y)
        n_labels = len(set(y))
        
        # Criterios de parada
        if depth >= self.max_depth or n_labels == 1 or n_samples < 2:
            return self._most_common(y)

        n_features = len(X[0])
        best_feat, best_thresh = self._best_split(X, y, n_features)
        
        if best_feat is None:
            return self._most_common(y)

        left_idxs, right_idxs = self._split(X, best_feat, best_thresh)
        
        # Construir sub-árboles (Diccionario recursivo)
        return {
            'feature_index': best_feat,
            'threshold': best_thresh,
            'left': self._build_tree([X[i] for i in left_idxs], [y[i] for i in left_idxs], depth+1),
            'right': self._build_tree([X[i] for i in right_idxs], [y[i] for i in right_idxs], depth+1)
        }

    def _most_common(self, y):
        return max(set(y), key=y.count)

    def _best_split(self, X, y, n_features):
        best_gain = -1
        split_idx, split_thresh = None, None
        
        # Probar splits aleatorios para eficiencia
        feat_idxs = random.sample(range(n_features), n_features)
        
        for feat_idx in feat_idxs:
            # Obtener columna
            X_column = [row[feat_idx] for row in X]
            thresholds = set(X_column)
            
            for thr in thresholds:
                gain = self._information_gain(y, X_column, thr)
                if gain > best_gain:
                    best_gain = gain
                    split_idx = feat_idx
                    split_thresh = thr
        return split_idx, split_thresh

    def _information_gain(self, y, X_column, split_thresh):
        # Entropía padre
        parent = self._entropy(y)
        
        # Generar split
        left_idxs, right_idxs = [], []
        for i, val in enumerate(X_column):
            if val <= split_thresh: left_idxs.append(i)
            else: right_idxs.append(i)
            
        if not left_idxs or not right_idxs: return 0
        
        n = len(y)
        n_l, n_r = len(left_idxs), len(right_idxs)
        e_l = self._entropy([y[i] for i in left_idxs])
        e_r = self._entropy([y[i] for i in right_idxs])
        
        child = (n_l/n)*e_l + (n_r/n)*e_r
        return parent - child

    def _split(self, X, feat_idx, threshold):
        left_idxs = [i for i, row in enumerate(X) if row[feat_idx] <= threshold]
        right_idxs = [i for i, row in enumerate(X) if row[feat_idx] > threshold]
        return left_idxs, right_idxs

    def _entropy(self, y):
        hist = [y.count(cls) for cls in set(y)]
        ps = [c/len(y) for c in hist]
        return -sum([p * math.log2(p) for p in ps if p > 0])
