import cv2
import numpy as np
import matplotlib.pyplot as plt

# Principal fuente (crack): https://www.youtube.com/watch?v=9dyaI3GyUtc&ab_channel=SantiagoFiorino

# VARIABLES GLOBALES
min_patente_width = 80  # Ancho mínimo esperado de una patente en pixeles
min_patente_height = 30  # Alto mínimo esperado de una patente en pixeles
tolerance = 0.2  # Tolerancia del 30% en el aspecto
ideal_aspect_ratio = min_patente_width / min_patente_height  # Relación de aspecto ideal
_template_cache = {}  # Cache para plantillas cargadas

def es_rectangulo(approx, tolerancia_angular=19):
    def angle(pt1, pt2, pt0):
        v1 = pt1 - pt0
        v2 = pt2 - pt0
        cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))

    if len(approx) != 4:
        return False

    pts = approx.reshape(4, 2)
    angles = [
        angle(pts[0], pts[2], pts[1]),
        angle(pts[1], pts[3], pts[2]),
        angle(pts[2], pts[0], pts[3]),
        angle(pts[3], pts[1], pts[0]),
    ]
    return all(abs(a - 90) < tolerancia_angular for a in angles)

def cumple_dimensiones(width, height):
    """
    Verifica si el contorno aproximado cumple con las dimensiones mínimas
    de una patente típica.
    
    Args:
        width (int): Ancho del contorno aproximado.
        height (int): Alto del contorno aproximado.
    
    Returns:
        bool: True si cumple con las dimensiones, False en caso contrario.
    """
    # Check aspect ratio
    aspect_ratio = width / height


    # Verifica si cumple con las dimensiones mínimas y el aspecto esperado
    if (width < min_patente_width or height < min_patente_height or 
        aspect_ratio < (ideal_aspect_ratio) * (1 - tolerance) or
        aspect_ratio > (ideal_aspect_ratio) * (1 + tolerance)):
        return False
    
    return True
    
    
def cumple_dimensiones_debug(width, height):
    """
    Misma lógica de cumple_dimensiones, pero con prints para debugging:
    muestra width, height, aspect_ratio y qué chequeo no se cumple.
    """
    # Evitar división por cero
    if height == 0:
        print(f"[DEBUG] height=0 → altura 0 no permitida.")
        return False

    aspect_ratio = width / height
    ideal_ar = min_patente_width / min_patente_height
    ar_min = ideal_ar * (1 - tolerance)
    ar_max = ideal_ar * (1 + tolerance)

    # Imprimimos todos los valores clave
    print("------ cumple_dimensiones_debug ------")
    print(f" width          = {width}")
    print(f" height         = {height}")
    print(f" aspect_ratio   = {aspect_ratio:.3f}")
    print(f" ideal_ar       = {ideal_ar:.3f}")
    print(f" rango_ar       = [{ar_min:.3f}, {ar_max:.3f}]")
    print(f" min_patente_w  = {min_patente_width}")
    print(f" min_patente_h  = {min_patente_height}")

    # 1) Chequeo ancho mínimo
    if width < min_patente_width:
        print(f" → FALLA: width ({width}) < min_patente_width ({min_patente_width})")
        return False

    # 2) Chequeo alto mínimo
    if height < min_patente_height:
        print(f" → FALLA: height ({height}) < min_patente_height ({min_patente_height})")
        return False

    # 3) Chequeo relación de aspecto mínima
    if aspect_ratio < ar_min:
        print(f" → FALLA: aspect_ratio ({aspect_ratio:.3f}) < ar_min ({ar_min:.3f})")
        return False

    # 4) Chequeo relación de aspecto máxima
    if aspect_ratio > ar_max:
        print(f" → FALLA: aspect_ratio ({aspect_ratio:.3f}) > ar_max ({ar_max:.3f})")
        return False

    # Si llegamos hasta aquí, cumple todo
    print(" → OK: cumple dimensiones y relación de aspecto")
    return True

def detectar_patente(frame_roi, umbral=145):
    gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY_INV)
    # _, bw = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY)
    
    bw = cv2.bilateralFilter(bw, 11, 9, 9)

    contornos, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    aspect_ratio_objetivo = 400.0 / 130.0  # ≃3.08
    # min_area = frame_roi.shape[0] * frame_roi.shape[1] * 0.05
    min_area = 1300
    max_area = 1600

    # print(f"Area minima: {min_area}")
    mejor_candidato = None
    menor_error_aspect_ratio = float('inf')
    area_contourns = []

    for cnt in contornos:
        area = cv2.contourArea(cnt)
        area_contourns.append(area)
        if area < min_area or area > max_area :
            # print(area)
            continue
        
        print(f"DEBUG - Area minima pasada: {area} ")
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # if not es_rectangulo(approx):
        #     continue

        # print(f"DEBUG - Es rectangulo: {area} ")
        # Obtenemos el bounding box del posible rectángulo
        x, y, w, h = cv2.boundingRect(approx)

        # # validar ancho/alto y aspecto mínimo
        # if not cumple_dimensiones(w, h):
        #     continue
        
        print(f"DEBUG - Cumplio dimensiones: {area} ")
        aspect = float(w) / float(h)
        error_aspect = abs(aspect - aspect_ratio_objetivo)

        if error_aspect < menor_error_aspect_ratio:
            menor_error_aspect_ratio = error_aspect
            # mejor_candidato = approx
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            mejor_candidato = np.intp(box)

    # Dibujar todos los contornos detectados en rojo para debug
    # img_debug_contornos = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    # cv2.drawContours(img_debug_contornos, contornos, -1, (0, 0, 255), 1)
    # print(f"DEBUG - Area Contornos: {area_contourns} ")
    # cv2.imshow("DEBUG - Todos los contornos", img_debug_contornos)
    # cv2.waitKey(1)  # Pequeña pausa para actualizar ventana

    img_contornos = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    if mejor_candidato is not None:
        # En alguna parte de estos parámetros salen..
        cv2.drawContours(img_contornos, [mejor_candidato], -1, (0, 255, 0), 2)

    return bw, mejor_candidato, img_contornos



def cargar_plantilla_cached(path):
    """Carga plantilla con cache para evitar lecturas repetitivas del disco."""
    if path not in _template_cache:
        tpl = cv2.imread(path)
        if tpl is None:
            raise FileNotFoundError(f"No se encuentra la plantilla en {path}")
        # Aplicar blur una sola vez y guardar en cache
        _template_cache[path] = cv2.GaussianBlur(tpl, (3, 3), 0)
    return _template_cache[path]

def filtrar_escalas_validas(w0, h0, escalas, min_w=60, min_h=20, tolerance=0.2):
    """
    Pre-filtra las escalas que cumplirían con las dimensiones mínimas.
    Evita calcular escalas que sabemos que fallarán.
    """
    ideal_aspect_ratio = min_w / min_h
    escalas_validas = []
    
    for scale in escalas:
        w = int(w0 * scale)
        h = int(h0 * scale)
        
        # Saltar escalas muy pequeñas
        if w < 10 or h < 10:
            continue
            
        # Pre-filtro rápido de dimensiones
        if w < min_w or h < min_h:
            continue
            
        # Pre-filtro de aspect ratio
        aspect_ratio = w / h
        ar_min = ideal_aspect_ratio * (1 - tolerance)
        ar_max = ideal_aspect_ratio * (1 + tolerance)
        
        if aspect_ratio < ar_min or aspect_ratio > ar_max:
            continue
            
        escalas_validas.append(scale)
    
    return escalas_validas
def detectar_patentes_pattern_matching(frame_roi, escalas=None):
    """
    Versión optimizada de detectar_patentes_pattern_matching.
    
    Optimizaciones aplicadas:
    1. Cache de plantillas para evitar recargas
    2. Pre-filtro de escalas inválidas
    3. Escalas reducidas por defecto (menos iteraciones)
    4. Template matching usando canal azul + blanco y negro
    5. Early stopping cuando se encuentra una buena correlación
    """
    
    # Escalas reducidas por defecto - menos iteraciones = más velocidad
    if escalas is None:
        escalas = [0.1, 0.15, 0.2, 0.25, 0.3]  # 5 escalas en lugar de 10
    
    templates = [
        {'label': 'new', 'path': 'img_src/patente_new.png'},
        # {'label': 'old', 'path': 'img_src/patente_old.jpg'}
    ]
    
    # Extraer canal azul del frame (patentes argentinas tienen fondo azul)
    frame_blue = frame_roi[:, :, 0]  # Canal azul (BGR format)
    frame_blue_blur = cv2.GaussianBlur(frame_blue, (3, 3), 0)
    
    # También preparar versión en escala de grises para comparación
    frame_gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
    frame_gray_blur = cv2.GaussianBlur(frame_gray, (3, 3), 0)
    
    resultados = {}
    
    for tpl_info in templates:
        label = tpl_info['label']
        path = tpl_info['path']
        
        # Usar cache para evitar recargar plantillas
        tpl_blur = cargar_plantilla_cached(path)
        
        # Preparar plantilla en canal azul
        tpl_blue = tpl_blur[:, :, 0]  # Canal azul de la plantilla
        
        # Preparar plantilla en escala de grises
        tpl_gray = cv2.cvtColor(tpl_blur, cv2.COLOR_BGR2GRAY)
        
        mejor = {
            'max_val': -1,
            'max_loc': None,
            'best_scale': None,
            'w': 0,
            'h': 0,
            'method': None  # Para saber qué método dio el mejor resultado
        }
        
        h0, w0 = tpl_blue.shape
        
        # Pre-filtrar escalas válidas (evita iteraciones innecesarias)
        escalas_validas = filtrar_escalas_validas(w0, h0, escalas)
        
        for scale in escalas_validas:
            w = int(w0 * scale)
            h = int(h0 * scale)
            
            # Redimensionar plantillas
            tpl_blue_scaled = cv2.resize(tpl_blue, (w, h), interpolation=cv2.INTER_AREA)
            tpl_gray_scaled = cv2.resize(tpl_gray, (w, h), interpolation=cv2.INTER_AREA)
            
            # Template matching con canal azul
            res_blue = cv2.matchTemplate(frame_blue_blur, tpl_blue_scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val_blue, _, max_loc_blue = cv2.minMaxLoc(res_blue)
            
            # Template matching con escala de grises
            res_gray = cv2.matchTemplate(frame_gray_blur, tpl_gray_scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val_gray, _, max_loc_gray = cv2.minMaxLoc(res_gray)
            
            # Elegir el mejor resultado entre ambos métodos
            if max_val_blue > max_val_gray:
                max_val = max_val_blue
                max_loc = max_loc_blue
                method = 'blue_channel'
            else:
                max_val = max_val_gray
                max_loc = max_loc_gray
                method = 'grayscale'
            
            if max_val > mejor['max_val']:
                mejor.update({
                    'max_val': max_val,
                    'max_loc': max_loc,
                    'best_scale': scale,
                    'w': w,
                    'h': h,
                    'method': method
                })
                
                # Early stopping: si encontramos una correlación muy alta, no seguir
                if max_val > 0.8:  # Umbral ajustable
                    print(f"[DEBUG] {label}: Early stopping con correlación {max_val:.3f} usando {method}")
                    break
        
        resultados[label] = mejor
    
    # Determinar ganador
    label_ganador = max(resultados.keys(),
                        key=lambda k: resultados[k]['max_val'],
                        default=None)
    
    ganador = resultados[label_ganador] if label_ganador else {}
    
    # Debug info sobre el método ganador
    if ganador and 'method' in ganador:
        print(f"[DEBUG] Mejor detección usando: {ganador['method']} con correlación {ganador['max_val']:.3f}")
    
    return {
        'all': resultados,
        'best': ganador,
        'label': label_ganador
    }