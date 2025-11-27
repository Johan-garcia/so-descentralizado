class ImageProcessor:
    def __init__(self):
        pass

    def process_from_content(self, content, operation='invert'):
        """
        Procesa una imagen en formato CSV
        Operaciones: invert, blur, sharpen, edge_detect
        """
        lines = [l.strip() for l in content.strip().split('\n') 
                if l.strip() and not l.startswith('#')]
        
        if not lines:
            return {'status': 'error', 'msg': 'No data provided'}
        
        # Parse matrix
        matrix = []
        for line in lines:
            try:
                row = [int(v.strip()) for v in line.split(',')]
                matrix.append(row)
            except ValueError:
                continue
        
        if not matrix:
            return {'status': 'error', 'msg': 'No valid matrix data'}
        
        rows = len(matrix)
        cols = len(matrix[0]) if matrix else 0
        
        print(f" [IMAGE] 🖼️  Procesando imagen {rows}x{cols} - Operación: {operation}")
        
        if operation == 'invert':
            result = self.invert(matrix)
        elif operation == 'blur':
            result = self.blur(matrix)
        elif operation == 'sharpen':
            result = self.sharpen(matrix)
        elif operation == 'edge_detect':
            result = self.edge_detect(matrix)
        else:
            result = matrix
        
        return {
            'status': 'success',
            'processed_matrix': result,
            'operation': operation,
            'dimensions': f"{rows}x{cols}"
        }

    def invert(self, matrix):
        """Invertir colores (255 - valor)"""
        return [[255 - pixel for pixel in row] for row in matrix]

    def blur(self, matrix):
        """Blur simple (promedio 3x3)"""
        rows = len(matrix)
        cols = len(matrix[0])
        result = [[0 for _ in range(cols)] for _ in range(rows)]
        
        for i in range(rows):
            for j in range(cols):
                total = 0
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols:
                            total += matrix[ni][nj]
                            count += 1
                result[i][j] = total // count
        
        return result

    def sharpen(self, matrix):
        """Sharpening básico"""
        rows = len(matrix)
        cols = len(matrix[0])
        result = [[0 for _ in range(cols)] for _ in range(rows)]
        
        kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                value = 0
                for ki in range(3):
                    for kj in range(3):
                        value += matrix[i + ki - 1][j + kj - 1] * kernel[ki][kj]
                result[i][j] = max(0, min(255, value))
        
        return result

    def edge_detect(self, matrix):
        """Detección de bordes (Sobel simple)"""
        rows = len(matrix)
        cols = len(matrix[0])
        result = [[0 for _ in range(cols)] for _ in range(rows)]
        
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                gx = (matrix[i-1][j+1] + 2*matrix[i][j+1] + matrix[i+1][j+1]) - \
                     (matrix[i-1][j-1] + 2*matrix[i][j-1] + matrix[i+1][j-1])
                gy = (matrix[i+1][j-1] + 2*matrix[i+1][j] + matrix[i+1][j+1]) - \
                     (matrix[i-1][j-1] + 2*matrix[i-1][j] + matrix[i-1][j+1])
                result[i][j] = min(255, abs(gx) + abs(gy))
        
        return result
