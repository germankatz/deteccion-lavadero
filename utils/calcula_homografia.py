import cv2
import numpy as np

def pick_points_and_compute_homography(imagen, roi):
    """
    Permite arrastrar 4 puntos en la imagen y retorna:
      - M: matriz de homografía 3x3
      - pts: lista de 4 puntos [(x0,y0), ...] en orden TL, TR, BR, BL
    Instrucciones:
      - Arrastra cada punto circular con el ratón para ver la deformación en tiempo real.
      - Pulsa 's' para calcular y mostrar la matriz.
      - Pulsa 'q' para salir sin calcular.
    """
    
    x, y, w, h = roi
    image = imagen[y : y + h, x : x + w]

    window_name = "Arrastra los 4 puntos - Presiona 's' para calcular, 'q' para salir"
    pts = []
    dragging_pt = None
    radius = 8
    color = (0, 255, 0)
    
    # Configurar el lienzo grande
    canvas_size = 800
    canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
    
    # Calcular posición para centrar la imagen original en el lienzo
    img_h, img_w = image.shape[:2]
    start_x = (canvas_size - img_w) // 2
    start_y = (canvas_size - img_h) // 2
    
    # Inicializar 4 puntos en las esquinas de la imagen (en coordenadas del lienzo)
    pts = [
        (start_x, start_y),                    # TL
        (start_x + img_w - 1, start_y),        # TR
        (start_x + img_w - 1, start_y + img_h - 1),  # BR
        (start_x, start_y + img_h - 1)         # BL
    ]

    def draw_interface(canvas_bg):
        # Limpiar lienzo
        canvas_display = canvas_bg.copy()
        
        # Dibujar la imagen original en el centro
        canvas_display[start_y:start_y + img_h, start_x:start_x + img_w] = image
        
        # Dibujar un borde alrededor de la imagen original para referencia
        cv2.rectangle(canvas_display, (start_x-2, start_y-2), 
                     (start_x + img_w + 1, start_y + img_h + 1), (100, 100, 100), 2)
        
        # Dibujar los puntos
        for i, (px, py) in enumerate(pts):
            cv2.circle(canvas_display, (int(px), int(py)), radius, color, -1)
            cv2.circle(canvas_display, (int(px), int(py)), radius, (255, 255, 255), 2)
            # Numerar los puntos
            cv2.putText(canvas_display, str(i+1), (int(px+12), int(py-12)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return canvas_display

    def update_transformation():
        try:
            # Puntos fuente (esquinas de la imagen original)
            src = np.array([
                (start_x, start_y),
                (start_x + img_w - 1, start_y),
                (start_x + img_w - 1, start_y + img_h - 1),
                (start_x, start_y + img_h - 1)
            ], dtype=np.float32)
            
            dst = np.array(pts, dtype=np.float32)
            
            # Calcular matriz de homografía
            M = cv2.getPerspectiveTransform(src, dst)
            
            # Crear lienzo para la transformación
            transformed_canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
            
            # Aplicar transformación solo a la región de la imagen original
            img_with_padding = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
            img_with_padding[start_y:start_y + img_h, start_x:start_x + img_w] = image
            
            transformed_canvas = cv2.warpPerspective(img_with_padding, M, (canvas_size, canvas_size))
            
            # Dibujar los puntos destino en la imagen transformada
            for i, (px, py) in enumerate(pts):
                cv2.circle(transformed_canvas, (int(px), int(py)), 5, (0, 255, 255), -1)
                cv2.circle(transformed_canvas, (int(px), int(py)), 5, (255, 255, 255), 2)
                cv2.putText(transformed_canvas, str(i+1), (int(px+8), int(py-8)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            # Combinar ambas vistas: original a la izquierda, transformada a la derecha
            combined = np.zeros((canvas_size, canvas_size * 2, 3), dtype=np.uint8)
            
            # Vista original con puntos (lado izquierdo)
            original_view = draw_interface(canvas)
            combined[:, :canvas_size] = original_view
            
            # Vista transformada (lado derecho)
            combined[:, canvas_size:] = transformed_canvas
            
            # Línea divisoria
            cv2.line(combined, (canvas_size, 0), (canvas_size, canvas_size), (100, 100, 100), 2)
            
            # Etiquetas
            cv2.putText(combined, "ORIGINAL - Arrastra puntos", (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(combined, "TRANSFORMACION", (canvas_size + 20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return combined
            
        except Exception as e:
            # Si hay error, mostrar solo la vista original
            error_view = draw_interface(canvas)
            combined = np.zeros((canvas_size, canvas_size * 2, 3), dtype=np.uint8)
            combined[:, :canvas_size] = error_view
            cv2.putText(combined, "Transformación inválida", (canvas_size + 50, canvas_size//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return combined

    def mouse_cb(event, x, y, flags, param):
        nonlocal dragging_pt
        
        # Solo considerar clics en la parte izquierda (vista original)
        if x >= canvas_size:
            return
            
        if event == cv2.EVENT_LBUTTONDOWN:
            # Seleccionar punto cercano
            for i, (px, py) in enumerate(pts):
                if (x-px)**2 + (y-py)**2 <= (radius + 5)**2:
                    dragging_pt = i
                    break
        elif event == cv2.EVENT_MOUSEMOVE and dragging_pt is not None:
            # Mover punto (mantenerlo dentro del lienzo izquierdo)
            pts[dragging_pt] = (max(0, min(canvas_size-1, x)), max(0, min(canvas_size-1, y)))
        elif event == cv2.EVENT_LBUTTONUP:
            dragging_pt = None

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_cb)

    while True:
        # Mostrar la vista combinada
        display = update_transformation()
        cv2.imshow(window_name, display)
        
        key = cv2.waitKey(20) & 0xFF
        if key == ord('s'):
            # Calcular homografía final (convertir puntos a coordenadas relativas de la imagen original)
            src = np.array([(0, 0), (img_w-1, 0), (img_w-1, img_h-1), (0, img_h-1)], dtype=np.float32)
            
            # Convertir puntos del lienzo a coordenadas relativas de la imagen
            pts_relative = []
            for px, py in pts:
                rel_x = px - start_x
                rel_y = py - start_y
                pts_relative.append((rel_x, rel_y))
            
            dst = np.array(pts_relative, dtype=np.float32)
            M = cv2.getPerspectiveTransform(src, dst)
            
            print("Matriz de homografía (3x3):")
            print(M)
            print("Puntos destino (relativos a la imagen ROI):", pts_relative)
            print("Puntos destino (coordenadas del lienzo):", pts)
            break
        elif key == ord('q'):
            M = None
            pts_relative = None
            break

    cv2.destroyAllWindows()
    return M, pts_relative if 'pts_relative' in locals() else None