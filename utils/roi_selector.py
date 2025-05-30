import cv2
import tkinter as tk
from utils.patente_detector import detectar_patente

class RoiSelector:
    def __init__(self):
        self.roi = None

    def usar_roi_por_defecto(self):
        self.roi = (333, 551, 382, 714)
        #self.roi = (458, 971, 116, 90)
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
        intervalo_s = 1

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
            cap.release()
            return
        scale = (screen_h * 0.75) / frame.shape[0]
        
        # FPS y cálculo de intervalo en frames
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        intervalo_f = max(1, int(fps * intervalo_s))

        # Iniciar tracker con el ROI ya definido
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, self.roi)

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        findex = 0
        roi = self.roi

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Solo actualizamos el tracker cada intervalo_s segundos
            if findex % intervalo_f == 0:
                ok, nueva = tracker.update(frame)
                if ok:
                    roi = tuple(int(v) for v in nueva)

            x, y, w, h = roi

            # 1) Mostrar vídeo con ROI
            display_frame = frame.copy()
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            resized_frame = cv2.resize(display_frame, None, fx=scale, fy=scale)
            cv2.imshow("Video con ROI", resized_frame)

            # 2) Extraer y binarizar sólo el parche del ROI
            parche = frame[y:y+h, x:x+w]
            bw, candidates,  vis = detectar_patente(parche)

            # 3) Mostrar únicamente el ROI binarizado
            cv2.imshow("ROI Binarizado", bw)
            cv2.imshow("Contornos Placa", vis)


            if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                break

            findex += 1

        cap.release()
        cv2.destroyAllWindows()


