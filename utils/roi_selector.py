import cv2
import tkinter as tk

class RoiSelector:
    def __init__(self):
        self.roi = None

    def usar_roi_por_defecto(self):
        self.roi = (370, 559, 349, 449)
        print(f"✅ ROI por defecto: {self.roi}")

    def _get_screen_size(self):
        """Devuelve el tamaño de pantalla (ancho, alto)"""
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        return width, height

    def marcar_roi_manual(self, video_path):

        """Permite al usuario seleccionar manualmente un ROI en el primer frame del video"""
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo leer el video.")
            return

        # Escalar a 75% de la altura de pantalla
        screen_w, screen_h = self._get_screen_size()
        target_h = int(screen_h * 0.75)
        scale = target_h / frame.shape[0]
        resized_frame = cv2.resize(frame, None, fx=scale, fy=scale)

        # Mostrar instrucciones
        # cv2.putText(resized_frame, "Presiona ENTER para confirmar, ESC para cancelar",
        #             (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        # cv2.imshow("Instrucciones", resized_frame)
        # cv2.waitKey(2000)
        # cv2.destroyWindow("Instrucciones")

        # Selección del ROI
        cv2.namedWindow("ROI", cv2.WINDOW_NORMAL)
        roi = cv2.selectROI("ROI", resized_frame, fromCenter=False, showCrosshair=True)
        print(roi)
        cv2.destroyAllWindows()

        if roi == (0, 0, 0, 0):
            print("❌ No se seleccionó ningún ROI.")
            return

        # Convertir a escala original
        x, y, w, h = [int(v / scale) for v in roi]
        self.roi = (x, y, w, h)
        print(f"✅ ROI seleccionado: {self.roi}")
        cap.release()

    def mostrar_video_con_roi(self, video_path):

        intervalo_s = 3

        """Reproduce el video completo mostrando el ROI en cada frame"""
        if self.roi is None:
            print("❌ No hay ROI definido.")
            return

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ No se pudo abrir el video.")
            return

        # Escalar video a 75% de la pantalla
        screen_w, screen_h = self._get_screen_size()
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo leer el primer frame.")
            return
        scale = (screen_h * 0.75) / frame.shape[0]
        
        # Obtener FPS real del video
        fps = 30
        intervalo_f = max(1, int(fps * intervalo_s))

        # Inicializar tracker con ROI
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, self.roi)


        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Volver al primer frame
        findex = 0
        roi = self.roi
        while True:
            
            ret, frame = cap.read()
            if not ret:
                break
            
            if(fps % intervalo_f == 0):
                fps = 0
                _, roi = tracker.update(frame)

            # if success:
            #     x, y, w, h = [int(v) for v in roi]
            #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # else:
            #     cv2.putText(frame, "Tracking perdido", (50, 50),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            
            x, y, w, h = [int(v) for v in roi]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Redimensionar para visualización
            resized_frame = cv2.resize(frame, None, fx=scale, fy=scale)
            cv2.imshow("Video con ROI (tracking)", resized_frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
            
            findex += 1

        cap.release()
        cv2.destroyAllWindows()

