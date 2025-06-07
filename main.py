import os
import cv2
from utils.roi_selector import RoiSelector
from interfaz import elegir_roi, seleccionar_video, elegir_tolerancia_frames, elegir_metodo_patente, elegir_metodo_rectificacion, calcular_homografia
from utils.roi_selector import RoiSelector
from utils.roi_rectifier import rectificar_roi, rectificar_roi_hardcoded, M_default, dst_corners_default
from utils.patente_detector import detectar_patentes_pattern_matching, detectar_patente
from utils.patente_lector import leer_patente, bbox_a_puntos
from utils.patente_tracker import PatenteTracker
from utils.calcula_homografia import pick_points_and_compute_homography

def main():

    # Video selector
    video_path = seleccionar_video()
    if not video_path:
        return
    
    # ROI
    roi_selector = RoiSelector()
    opcion = elegir_roi()

    if opcion == "1":
        roi_selector.usar_roi_por_defecto()
    elif opcion == "2":
        roi_selector.marcar_roi_manual(video_path)
    elif opcion == "0":
        return print("Saliendo...")
    
    print(f"ROI seleccionada: {roi_selector.roi}")
    
    # Abrir el video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ No se pudo abrir el video.")
        return
    
    metodo_patente = elegir_metodo_patente()
    if metodo_patente is None:
        return print("Saliendo...")

    
    if metodo_patente == "pattern_matching":
        metodo_rectificacion = elegir_metodo_rectificacion()
        if metodo_rectificacion is None:
            return print("Saliendo...")

        # Leo la patente
        ret, frame = cap.read()
        if metodo_rectificacion == "rectificacion_hardcoded":
            M = M_default
            dst_corners = dst_corners_default
            metodo_homografia_hardcoded =  calcular_homografia()
            if not metodo_homografia_hardcoded:
                M, dst_corners = pick_points_and_compute_homography(frame, roi_selector.roi)

            # Para este punto tengo una imagen ya rectificada
            # roi_rectificado = rectificar_roi_hardcoded(frame, roi_selector.roi, M, dst_corners)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # ! Esto me devuelve la imagen deformada
                roi_rectificado = rectificar_roi_hardcoded(frame, roi_selector.roi, M, dst_corners)

                # Detectar patente
                info = detectar_patentes_pattern_matching(roi_rectificado)
                gan = info['best']
                lbl = info['label']

                # Si no hay location válida, saltamos dibujado de rectángulo
                if gan['max_loc'] is not None:
                    tl = gan['max_loc'] 
                    br = (tl[0] + gan['w'], tl[1] + gan['h'])
                    cv2.rectangle(roi_rectificado, tl, br, (0, 255, 0), 2)
                    texto = f"{lbl} (val={gan['max_val']:.2f}, scale={gan['best_scale']})"
                    # x, y, w, h = roi_rectificado
                    
                    # patente_rectificada = frame[tl[1]:tl[1] + gan['h'], tl[0]:tl[0] + gan['w']]
                    # Puntos 
                    roi_patente = bbox_a_puntos(gan['max_loc'], gan['w'], gan['h'])
                    texto = leer_patente(roi_rectificado, roi_patente)  # Usar directamente la región extraída
                    # Si quieres mostrar texto, descomenta esto:
                    # cv2.putText(roi_rectificado, texto, (tl[0], tl[1] - 10),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    #print(texto)

                cv2.imshow("Imagen patente", roi_rectificado)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

    # Metodo de agu
    elif metodo_patente == "pattern_matching_alternativo":
        # Tolerancia
        tolerancia_frames = elegir_tolerancia_frames()
        if tolerancia_frames is None:
            return print("Saliendo...")

        tracker = PatenteTracker(tolerancia_frames=10)
        # roi_selector.mostrar_video_con_roi(video_path)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 1. Rectificar ROI
            # Se rompe todo si rectificamos con la imagen completa, como no hay tiempo lo salteamos
            # roi_rect = rectificar_roi_hardcoded(frame, roi_selector.roi) 
            x, y, w, h = roi_selector.roi
            roi_rect = frame[y:y+h, x:x+w]
            # 2. Detectar patente usando la función del archivo
            bw_image, mejor_candidato, img_contornos = detectar_patente(roi_rect)
            
            # Si se detectó una patente válida
            if mejor_candidato is not None:
                print(mejor_candidato)
                cv2.drawContours(roi_rect, [mejor_candidato], -1, (0, 255, 0), 2)
                # boundingRect me lo deja en (x, y, w, h)
                texto = leer_patente(roi_rect, mejor_candidato)  # Usar directamente la región extraída
                tracker.actualizar(texto)
            else:
                print("No hay patente válida en este frame")
            # Opcional: Mostrar el frame procesado
            cv2.imshow('ROI con deteccion', roi_rect)
            cv2.imshow('Imagen binarizada', bw_image)
            cv2.imshow('Contornos', img_contornos)
            
            # Salir con 'q'
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break

        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        tracker.finalizar()



if __name__ == "__main__":
    main()
