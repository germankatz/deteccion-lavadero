import cv2
import numpy as np

# Principal fuente (crack): https://www.youtube.com/watch?v=9dyaI3GyUtc&ab_channel=SantiagoFiorino

def detectar_patente(frame_roi, umbral = 135):
    """
    Recibe un parche BGR con la zona de la placa, lo pasa a blanco y negro
    y le aplica un threshold para resaltar los caracteres.
    Devuelve la imagen binarizada lista para mostrar.
    """
    # 1) Pasar a escala de grises. Esto para que sea más sencillo detectar una patente que, en general, es blanco y negro.
    gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)

    # ! 2) Paso Clave
    #  Aplicar un threshold. Ajusta 'umbral' a la iluminación del video.
    # Según el umbral, todo valor por encima del umbral será 255, por debajo, sera 0
    # Con esto, binarizo la imagen. 
    # Además, hago un inverso para obtener blanco las letras, ya que por default serán negras.

    _, bw = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY_INV)
    # bw = cv2.medianBlur(bw, 3)
    
    kernel = np.ones((5,5), np.uint8)
    bw_closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    
    # Con esto, en tiempo real, voy a tener marcadas las patentes.. pero ahora tengo que detectarlas lo más automáticamente posibles.
    # 3) Busco los contornos que definen a la imagen, y aplicandoselá al threshold..

    contornos, _ = cv2.findContours(bw_closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Busco el aspecto de ratio de una patente en la vida real (400mm x 130mm)
    aspect_ratio = 400.0 / 130.0  # ≃3.08
    tol_ratio    = 0.7
    # Descarta contornos muy pequeños (<10% del área del parche)
    min_area = frame_roi.shape[0] * frame_roi.shape[1] * 0.001

    candidates = []
    for cnt in contornos:
        area = cv2.contourArea(cnt)
        # if area < min_area:
        #     continue
        
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = float(w) / float(h)
        # print(aspect)
        if not np.isclose(aspect, aspect_ratio, atol=tol_ratio):
            continue

        candidates.append(cnt)

    # 4) Dibujar sólo los candidatos sobre la binarización
    img_contornos = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(img_contornos, candidates, -1, (0, 255, 0), 2)

    return bw, candidates, img_contornos