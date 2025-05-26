class PatenteTracker:
    """
    Clase para rastrear y mantener un registro de las patentes detectadas en un video.
    Permite llevar un control del tiempo que cada patente permanece visible y maneja
    casos donde la patente puede ocultarse temporalmente.
    """
    
    def __init__(self, tolerancia_frames):
        """
        Inicializa el tracker de patentes.
        
        Args:
            tolerancia_frames (int): Número máximo de frames consecutivos que una patente
                                   puede estar oculta antes de considerarla como una nueva
                                   detección. 
        """
        self.patente_actual = None
        self.frames_visibles = 0
        self.frames_oculta = 0
        self.tolerancia = tolerancia_frames
        self.historial = []  # [(texto_patente, total_frames)]

    def actualizar(self, texto_detectado):
        """
        Actualiza el estado del tracker con una nueva detección de patente.
        
        Args:
            texto_detectado (str): El texto de la patente detectada en el frame actual.
                                 Si es None o vacío, se considera que no se detectó patente.
        
        Comportamiento:
        - Si no se detecta patente:
            * Incrementa el contador de frames ocultos
            * Si supera la tolerancia, cierra el registro actual
        - Si se detecta la misma patente:
            * Incrementa el contador de frames visibles
            * Reinicia el contador de frames ocultos
        - Si se detecta una patente diferente:
            * Cierra el registro de la patente anterior
            * Inicia un nuevo registro con la nueva patente
        """
        if not texto_detectado:
            self.frames_oculta += 1
            if self.patente_actual and self.frames_oculta > self.tolerancia:
                self._cerrar_registro_actual()
            return

        if self.patente_actual == texto_detectado:
            self.frames_visibles += 1
            self.frames_oculta = 0
        else:
            if self.patente_actual:
                self._cerrar_registro_actual()
            self.patente_actual = texto_detectado
            self.frames_visibles = 1
            self.frames_oculta = 0

    def _cerrar_registro_actual(self):
        """
        Método interno que finaliza el registro de la patente actual.
        
        Acciones:
        - Agrega la patente actual y su tiempo de visibilidad al historial
        - Imprime un mensaje con la información de la patente
        - Reinicia los contadores y la patente actual
        """
        self.historial.append((self.patente_actual, self.frames_visibles))
        print(f"📛 Patente {self.patente_actual} estuvo visible {self.frames_visibles} frames.")
        self.patente_actual = None
        self.frames_visibles = 0
        self.frames_oculta = 0

    def finalizar(self):
        """
        Finaliza el tracking y asegura que se registre la última patente detectada.
        Debe llamarse al terminar el procesamiento del video.
        """
        if self.patente_actual:
            self._cerrar_registro_actual()

    def get_historial(self):
        """
        Obtiene el historial completo de patentes detectadas.
        
        Returns:
            list: Lista de tuplas (texto_patente, frames_visibles) ordenadas
                 cronológicamente por detección.
        """
        return self.historial
