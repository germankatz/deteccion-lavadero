import os
import questionary

def limpiar_consola():
    os.system("cls" if os.name == "nt" else "clear")


def seleccionar_video(carpeta="videos"):
    # limpiar_consola()
    videos = [f for f in os.listdir(carpeta) if f.lower().endswith((".mp4", ".avi", ".mov"))]

    if not videos:
        print("No se encontraron videos en la carpeta.")
        return None

    seleccion = questionary.select(
        "Seleccioná un video:",
        choices=videos
    ).ask()

    return os.path.join(carpeta, seleccion)

def elegir_roi():
    # limpiar_consola()
    opcion = questionary.select(
        "Seleccioná una opción:",
        choices=[
            "1. Usar ROI por defecto",
            "2. Marcar ROI manualmente en primer frame",
            "0. Salir"
        ]
    ).ask()

    return opcion[0]  # "1", "2" o "0"


def elegir_tolerancia_frames():
    # limpiar_consola()
    opcion = questionary.select(
        "Seleccioná una opción:",
        choices=[
            "1. Usar tolerancia por defecto (10 segundos)",
            "2. Ingresar tolerancia manualmente (en segundos)", 
            "0. Salir"
        ]
    ).ask()

    if opcion[0] == "1":
        return 10
    elif opcion[0] == "2":
        return questionary.text(
            "Ingresá la tolerancia en segundos:"
        ).ask() 
    elif opcion[0] == "0":
        return None