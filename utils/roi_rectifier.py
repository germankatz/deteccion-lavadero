import cv2
import numpy as np

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

def rectificar_roi_hardcoded(imagen, video_path, roi, M = None, dst_corners = None):
    
    if "Vertical" in video_path and (M == None) and (dst_corners == None):

        M = np.array([
        [1.448935, 0.730282, -155.000000],
        [-0.148001, 1.413944, 75.000000],
        [0.000632, 0.001040, 1.000000],
        ], dtype=np.float32)

        dst_corners = [
            (-155, 75),
            (320, 15),
            (463, 518),
            (210, 622),
        ]
    else:
        M = np.array([
            [2.39530571e+00, 7.26302128e-01, 3.74684219e+01],
            [3.08439998e-01, 1.44370911e+00, 8.92105255e+01],
            [1.10210092e-03, 4.83472034e-04, 1.00000000e+00],], dtype=np.float32)

        dst_corners = [(37.46842105263158, 89.21052631578947),
                    (1316.7473684210527, 203.4),
                    (1347.078947368421, 658.3736842105263),
                    (517.421052631579, 1038.4105263157894),]

    x, y, w, h = roi
    image_roi = imagen[y : y + h, x : x + w]

    # Transformación hardcoded
    xs = [p[0] for p in dst_corners]
    ys = [p[1] for p in dst_corners]
    width  = int(max(xs) - min(xs))
    height = int(max(ys) - min(ys))
    output_size = (width, height)

    # aplicamos warpPerspective sobre la imagen completa
    warp = cv2.warpPerspective(image_roi, M, output_size)
    return warp