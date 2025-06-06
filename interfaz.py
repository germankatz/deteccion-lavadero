import os
import questionary

def limpiar_consola():
    # os.system("cls" if os.name == "nt" else "clear")
    return 


def seleccionar_video(carpeta="videos"):
    limpiar_consola()
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
    limpiar_consola()
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
    limpiar_consola()
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
    
def elegir_angulo():
    limpiar_consola()
    opcion = questionary.select(
        "Seleccioná una opción:",
        choices=[
            "1. Usar angulo por defecto (60 grados)",
            "2. Ingresar angulo manualmente (en grados)",
            "0. Salir"
        ]
    ).ask()

    if opcion[0] == "1":
        return 60
    elif opcion[0] == "2":
        return questionary.text(
            "Ingresá el angulo en grados:"
        ).ask()
    elif opcion[0] == "0":
        return None

def elegir_metodo_patente():
    limpiar_consola()
    opcion = questionary.select(
        "Seleccioná una opción:",
        choices=[
            "1. Usar metodo por defecto (Pattern matching)",
            "2. Usar metodo alternativo (Método de area BW)",
            "0. Salir"
        ]
    ).ask()

    if opcion[0] == "1":
        return "pattern_matching"
    elif opcion[0] == "2":
        return "pattern_matching_alternativo"
    elif opcion[0] == "0":
        return None
    
def elegir_metodo_rectificacion():
    limpiar_consola()
    opcion = questionary.select(
        "Seleccioná una opción:",
        choices=[
            "1. Usar metodo por defecto (Rectificación hardcoded)",
            "0. Salir"
        ]
    ).ask()

    if opcion[0] == "1":
        return "rectificacion_hardcoded"
    elif opcion[0] == "0":
        return None

def calcular_homografia():
    limpiar_consola()
    opcion = questionary.select(
        "Seleccioná una opción:",
        choices=[
            "1. Usar homografía por defecto",
            "2. Calcular homografía",
            "0. Salir"
        ]
    ).ask()

    if opcion[0] == "1":
        return True
    elif opcion[0] == "2":
        return False
    elif opcion[0] == "0":
        return None

