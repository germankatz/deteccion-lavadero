import pytesseract
import platform
import re
import cv2
import numpy as np


def leer_patente(img_patente, roi2):
    """
    Realiza OCR sobre la imagen de la patente y devuelve el texto.
    """
    if img_patente is None:
        print("❌ Error: no se pudo cargar la imagen.")
        return ""
    else:
        print("✅ Imagen cargada. Dimensiones:", img_patente.shape)


    img = rectificar_patente(img_patente, roi2)

    # Mostramos la imagen rectificada
    #cv2.imshow("Patente rectificada", img)
    #cv2.waitKey(0)

    img_procesada =  preprocesar_patente_para_ocr(img)

    #cv2.imshow("Patente procesada", img_procesada)
    #cv2.waitKey(0)

    if platform.system() == 'Windows':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    patente_final = pytesseract.image_to_string(img_procesada, config=config).strip()
    #izq, centro, der = dividir_patente_en_tres(img_procesada)

    #izq_text  = ocr_letras(izq)
    #centro_text = ocr_numeros(centro)
    #der_text  = ocr_letras(der)
    
    #patente_final = f"{izq_text}{centro_text}{der_text}"
    patente_final = corregir_patente(patente_final)
    #print("Patente detectada:", patente_final)


    if es_patente_valida(patente_final):
        print("Patente válida detectada:", patente_final.strip())
        return patente_final.strip() 
    else:
        print("Patente inválida o mal leída:", patente_final.strip())
    
    return None

    


def es_patente_valida(texto):
  
    texto = texto.strip().upper().replace(" ", "")
    patron = r"^[A-Z]{2}[0-9]{3}[A-Z]{2}$"
    return re.match(patron, texto) is not None


def ordenar_puntos(pts):
    """
    Recibe un array de 4 puntos (x,y) y devuelve otro array de 4 puntos
    en este orden: [top-left, top-right, bottom-right, bottom-left].
    """
    # Asegurarse de que sean float32
    pts = pts.astype('float32')
    
    # sumas y diferencias para identificar esquinas
    s = pts.sum(axis=1)        # x + y
    diff = np.diff(pts, axis=1)  # y - x

    rect = np.zeros((4, 2), dtype='float32')
    rect[0] = pts[np.argmin(s)]       # top-left  => suma mínima
    rect[2] = pts[np.argmax(s)]       # bottom-right => suma máxima
    rect[1] = pts[np.argmin(diff)]    # top-right => diferencia mínima (y - x pequeña)
    rect[3] = pts[np.argmax(diff)]    # bottom-left => diferencia máxima (y - x grande)

    return rect

def rectificar_patente(imagen, roi_pts):
    """
    Toma:
      - imagen: np.ndarray (BGR),
      - roi_pts: array de 4 puntos enteros [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
        que definen los vértices de la patente en la imagen original (puede salir
        de cv2.boxPoints + np.intp).
    Retorna:
      - warped: np.ndarray de tamaño EXACTO (400×130), donde el ROI queda aplanado.
    """
    # 1) Reordenar puntos a [tl, tr, br, bl]
    pts_src = ordenar_puntos(roi_pts)

    # 2) Definir puntos destino para un rectángulo de 400×130:
    #    [0,0]       --> esquina superior izq
    #    [399,0]     --> esquina superior der  (ancho = 400)
    #    [399,129]   --> esquina inferior der  (alto = 130)
    #    [0,129]     --> esquina inferior izq
    ancho_dest = 400
    alto_dest  = 130
    pts_dst = np.array([
        [0, 0],
        [ancho_dest - 1, 0],
        [ancho_dest - 1, alto_dest - 1],
        [0, alto_dest - 1]
    ], dtype='float32')

    # 3) Calcular matriz de perspectiva
    M = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # 4) Aplicar warpPerspective sobre la imagen original
    warped = cv2.warpPerspective(imagen, M, (ancho_dest, alto_dest))

    return warped

def bbox_a_puntos(max_loc, w, h):
    """
    Dado un bounding box eje‐alineado:
      - max_loc: (x, y) esquina superior izquierda del ROI
      - w: ancho del ROI
      - h: alto del ROI

    Devuelve un array de 4 puntos enteros con la forma:
      [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]

    que puede usarse directamente en rectificar_patente(imagen, roi_pts).
    """
    x, y = max_loc
    pts = np.array([
        [x,     y],        # top-left
        [x + w, y],        # top-right
        [x + w, y + h],    # bottom-right
        [x,     y + h]     # bottom-left
    ], dtype=np.int32)
    return pts




def preprocesar_patente_para_ocr(img):
      # Convertir la imagen a escala de grises
    imagen_gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbral para obtener la imagen binaria
    _, imagen_binaria = cv2.threshold(imagen_gris, 128, 255, cv2.THRESH_BINARY)
    
  
    return imagen_binaria


def dividir_patente_en_tres(img_patente):
    h, w = img_patente.shape[:2]
    
    tercio = w // 3
    
    izquierda = img_patente[:, :tercio]
    #cv2.imshow("izquierda", izquierda)
    #cv2.waitKey(0)  # Espera que presiones una tecla
    #cv2.destroyAllWindows()
    centro    = img_patente[:, tercio:2*tercio]
    #cv2.imshow("centro", centro)
    #cv2.waitKey(0)  # Espera que presiones una tecla
    #cv2.destroyAllWindows()
    derecha   = img_patente[:, 2*tercio:]
    #cv2.imshow("derecha", derecha)
    #cv2.waitKey(0)  # Espera que presiones una tecla
    #cv2.destroyAllWindows()

    return izquierda, centro, derecha

def ocr_letras(img):
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return pytesseract.image_to_string(img, config=config).strip()

def ocr_numeros(img):
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    return pytesseract.image_to_string(img, config=config).strip()

def corregir_patente(texto_ocr):
    if len(texto_ocr) > 7:
        texto_ocr =texto_ocr[:6]
    texto_ocr = texto_ocr.strip().upper().replace(" ", "")
    
    if len(texto_ocr) != 7:
        return texto_ocr  # No tiene el formato esperado, no corregimos
    
    letras_inicio = texto_ocr[:2]
    numeros_ocr = texto_ocr[2:5]
    letras_final = texto_ocr[5:]
    
    # Correcciones típicas
    correcciones = {
        'O': '0',
        'Q': '0',
        'D': '0',
        'G': '0',
        'I': '1',
        'S': '5',
        'Z': '2'
    }
    
    numeros_corregidos = ''.join([correcciones.get(c, c) for c in numeros_ocr])

    return letras_inicio + numeros_corregidos + letras_final




