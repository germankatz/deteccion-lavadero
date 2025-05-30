import os
import cv2
from utils.roi_selector import RoiSelector
from interfaz import elegir_roi, seleccionar_video, elegir_tolerancia_frames, elegir_angulo
from utils.roi_selector import RoiSelector
from utils.roi_rectifier import rectificar_roi
from utils.patente_detector import detectar_patente
from utils.patente_lector import leer_patente
from utils.patente_tracker import PatenteTracker

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
    
    # Tolerancia
    tolerancia_frames = elegir_tolerancia_frames()
    if tolerancia_frames is None:
        return print("Saliendo...")
    
    # Abrir el video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ No se pudo abrir el video.")
        return

    tracker = PatenteTracker(tolerancia_frames=10)
    # roi_selector.mostrar_video_con_roi(video_path)

    angulo = elegir_angulo()
    ret, frame = cap.read()
    try:
        roi_rectificada = rectificar_roi(frame, roi_selector.roi, float(angulo))
        cv2.imshow("ROI Rectificada", roi_rectificada)
        cv2.waitKey(0)
    except Exception as e:
        print(f"⚠️  Error al rectificar ROI: {e}")
        # imagen_patente = detectar_patente(roi_rect)
        # texto = leer_patente(imagen_patente)
        # tracker.actualizar(texto)

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    tracker.finalizar()



if __name__ == "__main__":
    main()
