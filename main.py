import os
import cv2
from utils.roi_selector import RoiSelector
from interfaz import elegir_roi, seleccionar_video, elegir_tolerancia_frames, elegir_metodo_patente, elegir_metodo_rectificacion, calcular_homografia
from utils.roi_selector import RoiSelector
from utils.roi_rectifier import rectificar_roi, rectificar_roi_hardcoded, M_default, dst_corners_default
from utils.patente_detector import detectar_patente
from utils.patente_lector import leer_patente
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

                roi_rectificado = rectificar_roi_hardcoded(frame, roi_selector.roi, M, dst_corners)



                # mostrar imagen como video
                cv2.imshow("Imagen patente", roi_rectificado)
                # esperar 300ms 
                cv2.imshow("Imagen patente", roi_rectificado)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()



        elif metodo_rectificacion == "rectificacion_roi":
            ret, frame = cap.read()

    # Metodo de agu
    elif metodo_patente == "pattern_matching_alternativo":
        # Tolerancia
        tolerancia_frames = elegir_tolerancia_frames()
        if tolerancia_frames is None:
            return print("Saliendo...")

        tracker = PatenteTracker(tolerancia_frames=10)
        roi_selector.mostrar_video_con_roi(video_path)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # roi_rect = rectificar_roi(frame, roi_selector.roi)
            # imagen_patente = detectar_patente(roi_rect)
            # texto = leer_patente(imagen_patente)
            # tracker.actualizar(texto)

        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        tracker.finalizar()



if __name__ == "__main__":
    main()
