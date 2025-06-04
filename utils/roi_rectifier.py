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

# Valores calculados con
M_default = np.array([
        [1.448935, 0.730282, -155.000000],
        [-0.148001, 1.413944, 75.000000],
        [0.000632, 0.001040, 1.000000],
    ], dtype=np.float32)

dst_corners_default = [
    (-155, 75),
    (320, 15),
    (463, 518),
    (210, 622),
]
# ##### N and points for horizontal
# M_default = np.array([
#     [ 1.416052,    0.335372,  -23.552632],
#     [-0.044943,    1.110917,   77.723686],
#     [ 0.000502,    0.000388,    1.000000],
# ], dtype=np.float32)

# dst_corners_default = [
#     (-23.55263157894737,  77.72368421052632),
#     (857.3157894736842,   25.907894736842106),
#     (858.4934210526316,  449.85526315789474),
#     (156.625,            642.9868421052631),
# ]


def rectificar_roi_hardcoded(imagen, roi, M = M_default, dst_corners = dst_corners_default):
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