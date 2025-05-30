import cv2

def rectificar_roi(imagen, roi, angulo=60):
    """
    Aplica transformación para rectificar el ROI (perspectiva, etc.)
    """
    # Seleccionar la ROI en los canales RGB
    x, y, w, h = roi
    image_roi = imagen[y : y + h, x : x + w]

    # Convertir la imagen a escala de grises
    imagen_gris = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbral para obtener la imagen binaria
    _, imagen_binaria = cv2.threshold(imagen_gris, 128, 255, cv2.THRESH_BINARY)

    # Matriz de transformación angulo
    matriz_rotacion = cv2.getRotationMatrix2D((image_roi.shape[1] / 2, image_roi.shape[0] / 2), angulo, 1)

    # Rotar la imagen
    imagen_rotada = cv2.warpAffine(imagen_binaria, matriz_rotacion, (image_roi.shape[1], image_roi.shape[0]))
 
    return imagen_rotada
