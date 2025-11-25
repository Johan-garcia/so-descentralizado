class ImageProcessor:
    def __init__(self):
        pass

    def _parse_matrix(self, file_content):
        """Convierte texto CSV en una matriz de imagen (lista de listas)"""
        matrix = []
        lines = file_content.strip().split('\n')
        for line in lines:
            if not line.strip(): continue
            parts = line.split(',')
            row = [int(float(p)) for p in parts] # Asegurar enteros 0-255
            matrix.append(row)
        return matrix

    def process_from_content(self, file_content, operation='invert'):
        try:
            matrix = self._parse_matrix(file_content)
            if not matrix: return {"status": "error", "msg": "Empty image data"}
            
            result_matrix = []
            
            if operation == 'invert':
                # Invertir colores (Negativo): 255 - valor
                for row in matrix:
                    new_row = [255 - pixel for pixel in row]
                    result_matrix.append(new_row)
            
            elif operation == 'threshold':
                # Blanco y negro puro
                for row in matrix:
                    new_row = [255 if pixel > 127 else 0 for pixel in row]
                    result_matrix.append(new_row)
                    
            return {
                "status": "success", 
                "operation": operation,
                "original_size": f"{len(matrix)}x{len(matrix[0])}",
                "processed_matrix": result_matrix
            }
            
        except Exception as e:
            return {"status": "error", "msg": str(e)}
