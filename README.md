# Detección de Patentes en Lavadero

Sistema de detección y seguimiento de patentes de vehículos en un lavadero mediante técnicas de procesamiento de imágenes. El sistema permite identificar las patentes de los vehículos que ingresan al lavadero y llevar un registro del tiempo que permanecen en el establecimiento.

## Características

- Selección de región de interés (ROI) para la detección de patentes
  - ROI por defecto predefinido
  - Selección manual del ROI en el primer frame
- Múltiples métodos de detección de patentes:
  - Pattern matching con rectificación de perspectiva
  - Método alternativo con seguimiento temporal
- Rectificación de perspectiva con dos métodos:
  - Rectificación hardcoded con homografía predefinida
  - Rectificación manual con selección de puntos
- Interfaz de usuario interactiva para configuración
- Seguimiento temporal de patentes con tolerancia configurable
- Visualización en tiempo real de la detección

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- OpenCV
- NumPy
- Questionary (para la interfaz de usuario)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/deteccion-lavadero.git
cd deteccion-lavadero
```

2. Crear y activar un entorno virtual:

```bash
# En Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Instalar las dependencias:

```bash
pip install -r req.txt

# req.txt no incluye tkinter porque debe instalarse con el gestor de paquetes del sistema:
# En Ubuntu/Debian:
sudo apt install python3-tk
```

## Estructura del Proyecto

```
deteccion-lavadero/
├── main.py              # Punto de entrada principal
├── interfaz.py          # Funciones de interfaz de usuario
├── req.txt              # Dependencias del proyecto
├── videos/              # Directorio para videos de entrada
└── utils/               # Módulos de utilidad
    ├── roi_selector.py     # Selección de región de interés
    ├── roi_rectifier.py    # Rectificación de perspectiva
    ├── patente_detector.py # Detección de patentes
    ├── patente_lector.py   # Lectura de texto de patentes
    ├── patente_tracker.py  # Seguimiento temporal
    └── calcula_homografia.py # Cálculo de homografía
```

## Uso

1. Colocar los videos a procesar en el directorio `videos/`

2. Ejecutar el programa:

```bash
python main.py
```

3. Seguir las instrucciones en pantalla:
   - Seleccionar el video a procesar de la lista de archivos en /videos
   - Elegir el método de selección de ROI:
     - Usar ROI por defecto
     - Marcar ROI manualmente
   - Seleccionar el método de detección de patentes:
     - Pattern matching con rectificación
     - Método alternativo con seguimiento
   - Si se elige pattern matching:
     - Elegir método de rectificación (hardcoded o manual)
     - Si es manual, seleccionar los puntos para la homografía
   - Si se elige método alternativo:
     - Configurar la tolerancia de frames para el seguimiento

## Controles

- Durante la selección manual de ROI:
  - Arrastrar para seleccionar el área
  - ENTER para confirmar
  - ESC para cancelar
- Durante la visualización:
  - 'q' para salir
  - Durante la selección de homografía:
    - Arrastrar puntos para ajustar
    - 's' para guardar
    - 'q' para cancelar
