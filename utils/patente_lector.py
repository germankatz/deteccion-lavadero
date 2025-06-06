import pytesseract
import re
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def leer_patente(img_patente):
    """
    Realiza OCR sobre la imagen de la patente y devuelve el texto.
    """
    if img_patente is None:
        print("❌ Error: no se pudo cargar la imagen.")
        return ""
    else:
        print("✅ Imagen cargada. Dimensiones:", img_patente.shape)

    # Ruta absoluta basada en la ubicación del script actual
    #base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # sube desde utils/
    #ruta_img = os.path.join(base_dir, 'img_src', 'Screen_3.png')

    #print(os.path.exists(ruta_img)) 
    #print("Ruta completa:", ruta_img)  # podés verificar que esté bien
    #img_rotada = cv2.imread(ruta_img)
 
 
    img = extraer_patente_desde_rectangulo_verde(img_patente)
    #cv2.imshow("Patente recortada", img)
    #cv2.waitKey(0)
    # Cargar imagen
    #img_sinrotar = cv2.imread('../img_src/Screen_3.png', cv2.IMREAD_GRAYSCALE)
    #alto, ancho = img_rotada.shape[:2]
    #roi = (0, 0, ancho, alto)
    #img = rectificar_roi(img_rotada,roi,20)
    
    #binaria = preprocesar_para_ocr(img)    
   
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    izq, centro, der = dividir_patente_en_tres(img)

    izq_text  = ocr_letras(izq)
    centro_text = ocr_numeros(centro)
    der_text  = ocr_letras(der)

    patente_final = f"{izq_text} {centro_text} {der_text}"
    print("Patente detectada:", patente_final)

    # Paso 4: Validar
    if es_patente_valida(patente_final):
        print("Patente válida detectada:", patente_final.strip())
    else:
        print("Patente inválida o mal leída:", patente_final.strip())

    return  patente_final.strip()

def dividir_patente_en_tres(img_patente):
    h, w = img_patente.shape[:2]
    
    tercio = w // 3
    
    izquierda = img_patente[:, :tercio]
    # cv2.imshow("izquierda", izquierda)
    # cv2.waitKey(0)  # Espera que presiones una tecla
    # cv2.destroyAllWindows()
    centro    = img_patente[:, tercio:2*tercio]
    # cv2.imshow("centro", centro)
    # cv2.waitKey(0)  # Espera que presiones una tecla
    # cv2.destroyAllWindows()
    derecha   = img_patente[:, 2*tercio:]
    # cv2.imshow("derecha", derecha)
    # cv2.waitKey(0)  # Espera que presiones una tecla
    # cv2.destroyAllWindows()

    return izquierda, centro, derecha

def ocr_letras(img):
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return pytesseract.image_to_string(img, config=config).strip()

def ocr_numeros(img):
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    return pytesseract.image_to_string(img, config=config).strip()

def preprocesar_para_ocr(img):
    # Escala de grises
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aumentar tamaño si es muy chica
    escala = 2  # o 3 según necesidad
    gris = cv2.resize(gris, (gris.shape[1]*escala, gris.shape[0]*escala), interpolation=cv2.INTER_LINEAR)
    
    suavizada = cv2.bilateralFilter(gris, 11, 17, 17)
     
    # 3. Pasa-altos
    pasa_altos = filtro_pasa_altos(suavizada)


    return pasa_altos

def filtro_pasa_altos(img_gray):
    # Kernel pasa-altos clásico
    kernel = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])
    
    high_pass = cv2.filter2D(img_gray, -1, kernel)
    
    # Normalizamos para evitar saturación
    high_pass = cv2.normalize(high_pass, None, 0, 255, cv2.NORM_MINMAX)

    return high_pass


def es_patente_valida(texto):
    """
    Valida si el texto tiene formato de patente argentina actual (AA 123 BB).
    """
    texto = texto.strip().upper().replace(" ", "")
    patron = r"^[A-Z]{2}[0-9]{3}[A-Z]{2}$"
    return re.match(patron, texto) is not None


def extraer_patente_desde_rectangulo_verde(imagen):
    # Convertimos a HSV para detectar color verde
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Rango típico para verde (puede ajustarse según el tono)
    lower_green = np.array([40, 100, 100])
    upper_green = np.array([80, 255, 255])
    
    # Crear máscara verde
    mascara = cv2.inRange(hsv, lower_green, upper_green)
    
    # Encontrar contornos
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contornos:
        raise Exception("No se encontró ningún contorno verde")
    
    # Tomar el contorno más grande (debería ser el rectángulo)
    c = max(contornos, key=cv2.contourArea)
    
    # Aproximar a 4 puntos
    epsilon = 0.02 * cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, epsilon, True)
    
    if len(approx) != 4:
        raise Exception("No se pudo detectar un rectángulo con 4 vértices")
    
    # Ordenar los puntos (superior izq, sup der, inf der, inf izq)
    pts = approx.reshape(4, 2)
    pts = ordenar_puntos(pts)

    # Dimensiones estimadas del recorte
    ancho = int(max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3])))
    alto  = int(max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2])))

    dst_pts = np.array([
        [0, 0],
        [ancho - 1, 0],
        [ancho - 1, alto - 1],
        [0, alto - 1]
    ], dtype=np.float32)

    # Matriz de transformación
    M = cv2.getPerspectiveTransform(pts.astype(np.float32), dst_pts)

    # Warp
    warp = cv2.warpPerspective(imagen, M, (ancho, alto))

    return warp

def ordenar_puntos(pts):
    # Ordena en: top-left, top-right, bottom-right, bottom-left
    suma = pts.sum(axis=1)
    dif  = np.diff(pts, axis=1)

    ordenados = np.zeros((4, 2), dtype=np.float32)
    ordenados[0] = pts[np.argmin(suma)]  # top-left
    ordenados[2] = pts[np.argmax(suma)]  # bottom-right
    ordenados[1] = pts[np.argmin(dif)]   # top-right
    ordenados[3] = pts[np.argmax(dif)]   # bottom-left
    return ordenados

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


#texto = leer_patente()