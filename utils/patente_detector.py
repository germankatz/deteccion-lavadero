import cv2
import numpy as np
import matplotlib.pyplot as plt

# Principal fuente (crack): https://www.youtube.com/watch?v=9dyaI3GyUtc&ab_channel=SantiagoFiorino

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

def detectar_patente(frame_roi, umbral=145):
    gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY_INV)

    bw = cv2.bilateralFilter(bw, 11, 17, 17)

    contornos, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    aspect_ratio_objetivo = 400.0 / 130.0  # ≃3.08
    min_area = frame_roi.shape[0] * frame_roi.shape[1] * 0.01

    mejor_candidato = None
    menor_error_aspect_ratio = float('inf')

    for cnt in contornos:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if not es_rectangulo(approx):
            continue

        # De acá sale el bb final.
        x, y, w, h = cv2.boundingRect(approx)
        aspect = float(w) / float(h)
        error_aspect = abs(aspect - aspect_ratio_objetivo)

        if error_aspect < menor_error_aspect_ratio:
            menor_error_aspect_ratio = error_aspect
            mejor_candidato = approx

    img_contornos = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    if mejor_candidato is not None:
        # En alguna parte de estos parámetros salen..
        cv2.drawContours(img_contornos, [mejor_candidato], -1, (0, 255, 0), 2)

    return bw, mejor_candidato, img_contornos

def detectar_patentes_pattern_matching(frame_roi,
                                       escalas=[0.25, 0.4, 0.5, 0.65]):
    """
    Detecta la mejor coincidencia de dos plantillas (patente_new y patente_old)
    en un mismo frame_roi, probando varios factores de escala.

    Args:
        frame_roi (ndarray): Región de interés de la imagen (BGR).
        escalas (list of float): Factores de escala a probar.

    Returns:
        dict con:
            all: {
                'new': {max_val, max_loc, best_scale, w, h},
                'old': {…}
            }
            best: sub-dict del ganador ('new' u 'old')
            label: 'new' o 'old'
    """
    # Rutas de las dos plantillas
    templates = {
        'new': 'img_src/patente_new.png',
        'old': 'img_src/patente_old.jpg'
    }

    # Preprocesar el frame: blur + gris
    frame_blur = cv2.GaussianBlur(frame_roi, (5,5), 0)
    frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)

    resultados = {}

    for key, path in templates.items():
        tpl = cv2.imread(path)
        if tpl is None:
            raise FileNotFoundError(f"No se encuentra la plantilla en {path}")
        tpl = cv2.GaussianBlur(tpl, (5,5), 0)

        mejor = {'max_val': -1, 'max_loc': None, 'best_scale': None, 'w':0, 'h':0}

        h0, w0 = tpl.shape[:2]
        for scale in escalas:
            w = int(w0 * scale)
            h = int(h0 * scale)
            if w < 10 or h < 10: continue

            tpl_rs = cv2.resize(tpl, (w,h), interpolation=cv2.INTER_AREA)
            tpl_gray = cv2.cvtColor(tpl_rs, cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(frame_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > mejor['max_val']:
                mejor.update({
                    'max_val': max_val,
                    'max_loc': max_loc,
                    'best_scale': scale,
                    'w': w, 'h': h
                })

        resultados[key] = mejor

    # Decidir cuál plantilla ganó
    if resultados['new']['max_val'] >= resultados['old']['max_val']:
        ganador, label = resultados['new'], 'new'
    else:
        ganador, label = resultados['old'], 'old'

    return {
        'all': resultados,
        'best': ganador,
        'label': label
    }
def detectar_patentes_pattern_matching(frame_roi,
                                       escalas=[0.05, 0.10, 0.15, 0.20, 0.25]):
    """
    Detecta la mejor coincidencia de dos plantillas (patente_new y patente_old)
    en un mismo frame_roi, probando varios factores de escala.
    DETECCIÓN EN RGB con blur suave.

    Args:
        frame_roi (ndarray): Región de interés de la imagen (BGR).
        escalas (list of float): Factores de escala a probar.

    Returns:
        dict con:
            all: {
                'new': {max_val, max_loc, best_scale, w, h},
                'old': {…}
            }
            best: sub-dict del ganador ('new' u 'old')
            label: 'new' o 'old'
    """
    # Rutas de las dos plantillas
    templates = {
        'new': 'img_src/patente_new.png',
        'old': 'img_src/patente_old.jpg'
    }

    # Preprocesar el frame: blur MUY suave + mantener RGB
    frame_blur = cv2.GaussianBlur(frame_roi, (3,3), 0)  # Blur más suave (3x3 en vez de 5x5)

    resultados = {}

    for key, path in templates.items():
        tpl = cv2.imread(path)
        if tpl is None:
            raise FileNotFoundError(f"No se encuentra la plantilla en {path}")
        tpl = cv2.GaussianBlur(tpl, (3,3), 0)  # Blur más suave también en plantilla

        mejor = {'max_val': -1, 'max_loc': None, 'best_scale': None, 'w':0, 'h':0}

        h0, w0 = tpl.shape[:2]
        for scale in escalas:
            w = int(w0 * scale)
            h = int(h0 * scale)
            if w < 10 or h < 10: continue

            tpl_rs = cv2.resize(tpl, (w,h), interpolation=cv2.INTER_AREA)
            
            # DETECCIÓN EN RGB: comparar los 3 canales
            res_b = cv2.matchTemplate(frame_blur[:,:,0], tpl_rs[:,:,0], cv2.TM_CCOEFF_NORMED)
            res_g = cv2.matchTemplate(frame_blur[:,:,1], tpl_rs[:,:,1], cv2.TM_CCOEFF_NORMED)
            res_r = cv2.matchTemplate(frame_blur[:,:,2], tpl_rs[:,:,2], cv2.TM_CCOEFF_NORMED)
            
            # Combinar los 3 canales (promedio ponderado)
            res = (res_b + res_g + res_r) / 3.0
            
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > mejor['max_val']:
                mejor.update({
                    'max_val': max_val,
                    'max_loc': max_loc,
                    'best_scale': scale,
                    'w': w, 'h': h
                })

        resultados[key] = mejor

    # Decidir cuál plantilla ganó
    if resultados['new']['max_val'] >= resultados['old']['max_val']:
        ganador, label = resultados['new'], 'new'
    else:
        ganador, label = resultados['old'], 'old'

    return {
        'all': resultados,
        'best': ganador,
        'label': label
    }


def visualizar_deteccion_patentes(frame_roi, resultado_deteccion, 
                                  escalas=[0.05, 0.10, 0.15, 0.20, 0.25],
                                  figsize=(15, 10)):
    """
    Visualiza el proceso de detección de patentes mostrando:
    - Imagen original vs con blur
    - Plantillas redimensionadas a la mejor escala
    - Mapas de correlación
    - Detección ganadora marcada
    
    Args:
        frame_roi (ndarray): ROI original (BGR)
        resultado_deteccion (dict): Resultado de detectar_patentes_pattern_matching
        escalas (list): Mismas escalas usadas en la detección
        figsize (tuple): Tamaño de la figura
    """
    
    # Preparar datos
    frame_blur = cv2.GaussianBlur(frame_roi, (3,3), 0)  # Blur más suave
    frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
    frame_rgb = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2RGB)
    frame_blur_rgb = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2RGB)
    
    templates = {
        'new': 'img_src/patente_new.png',
        'old': 'img_src/patente_old.jpg'
    }
    
    fig, axes = plt.subplots(3, 3, figsize=figsize)
    fig.suptitle('Análisis de Detección de Patentes', fontsize=16, fontweight='bold')
    
    # Fila 1: Comparación original vs blur
    axes[0,0].imshow(frame_rgb)
    axes[0,0].set_title('Frame Original')
    axes[0,0].axis('off')
    
    axes[0,1].imshow(frame_blur_rgb)
    axes[0,1].set_title('Frame con Blur Suave (3x3)')
    axes[0,1].axis('off')
    
    axes[0,2].imshow(frame_gray, cmap='gray')
    axes[0,2].set_title('Frame en Escala de Grises')
    axes[0,2].axis('off')
    
    # Fila 2: Plantillas y mapas de correlación
    col_idx = 0
    colores_bbox = {'new': 'lime', 'old': 'orange'}
    
    for key, path in templates.items():
        # Cargar y procesar plantilla
        tpl = cv2.imread(path)
        if tpl is None:
            continue
            
        tpl_blur = cv2.GaussianBlur(tpl, (3,3), 0)  # Blur más suave
        
        # Obtener mejor escala para esta plantilla
        best_result = resultado_deteccion['all'][key]
        best_scale = best_result['best_scale']
        
        if best_scale is not None:
            # Redimensionar plantilla a la mejor escala
            h0, w0 = tpl_blur.shape[:2]
            w_scaled = int(w0 * best_scale)
            h_scaled = int(h0 * best_scale)
            
            tpl_scaled = cv2.resize(tpl_blur, (w_scaled, h_scaled), interpolation=cv2.INTER_AREA)
            tpl_scaled_gray = cv2.cvtColor(tpl_scaled, cv2.COLOR_BGR2GRAY)
            tpl_scaled_rgb = cv2.cvtColor(tpl_scaled, cv2.COLOR_BGR2RGB)
            
            # Mostrar plantilla redimensionada
            axes[1, col_idx].imshow(tpl_scaled_rgb)
            axes[1, col_idx].set_title(f'Plantilla {key.upper()}\nEscala: {best_scale:.2f}')
            axes[1, col_idx].axis('off')
            
            # Calcular mapa de correlación EN RGB (como en la función principal)
            res_b = cv2.matchTemplate(frame_blur[:,:,0], tpl_scaled[:,:,0], cv2.TM_CCOEFF_NORMED)
            res_g = cv2.matchTemplate(frame_blur[:,:,1], tpl_scaled[:,:,1], cv2.TM_CCOEFF_NORMED)
            res_r = cv2.matchTemplate(frame_blur[:,:,2], tpl_scaled[:,:,2], cv2.TM_CCOEFF_NORMED)
            res = (res_b + res_g + res_r) / 3.0
            
            axes[2, col_idx].imshow(res, cmap='hot', interpolation='nearest')
            axes[2, col_idx].set_title(f'Mapa Correlación {key.upper()}\nMax: {best_result["max_val"]:.3f}')
            axes[2, col_idx].axis('off')
            
            # Marcar punto de máxima correlación
            max_loc = best_result['max_loc']
            if max_loc is not None:
                axes[2, col_idx].plot(max_loc[0], max_loc[1], 'wo', markersize=8, markeredgecolor='black')
        
        col_idx += 1
    
    # Fila 2, columna 3: Frame con detección ganadora
    frame_result = frame_rgb.copy()
    best_result = resultado_deteccion['best']
    label_ganador = resultado_deteccion['label']
    
    if best_result['max_loc'] is not None:
        x, y = best_result['max_loc']
        w, h = best_result['w'], best_result['h']
        
        # Dibujar rectángulo de detección
        color = colores_bbox[label_ganador]
        if color == 'lime':
            color_rgb = (0, 255, 0)
        else:  # orange
            color_rgb = (255, 165, 0)
        
        # Convertir a formato matplotlib (necesitamos usar Rectangle patch)
        from matplotlib.patches import Rectangle
        rect = Rectangle((x, y), w, h, linewidth=3, edgecolor=np.array(color_rgb)/255, facecolor='none')
        axes[1, 2].add_patch(rect)
    
    axes[1, 2].imshow(frame_result)
    axes[1, 2].set_title(f'GANADOR: {label_ganador.upper()}\nCorrelación: {best_result["max_val"]:.3f}')
    axes[1, 2].axis('off')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Mostrar resumen en texto
    print("="*50)
    print("RESUMEN DE DETECCIÓN")
    print("="*50)
    print(f"Ganador: {label_ganador.upper()}")
    print(f"Correlación máxima: {best_result['max_val']:.4f}")
    print(f"Mejor escala: {best_result['best_scale']:.3f}")
    print(f"Posición: {best_result['max_loc']}")
    print(f"Dimensiones: {best_result['w']}x{best_result['h']}")
    print("\nComparación:")
    for key in ['new', 'old']:
        res = resultado_deteccion['all'][key]
        print(f"  {key.upper()}: {res['max_val']:.4f} (escala {res['best_scale']:.3f})")
    
    plt.show()


# Función de uso combinado
def detectar_y_visualizar_patentes(frame_roi, escalas=[0.05, 0.10, 0.15, 0.20, 0.25]):
    """
    Función combinada que detecta y visualiza en un solo paso.
    """
    # Detectar
    resultado = detectar_patentes_pattern_matching(frame_roi, escalas)
    
    # Visualizar
    visualizar_deteccion_patentes(frame_roi, resultado, escalas)
    
    return resultado
