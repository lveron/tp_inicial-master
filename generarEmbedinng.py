import face_recognition
import json
import os
import numpy as np

RUTA_EMBEDDINGS = "data/embeddings.json"
UMBRAL_SIMILITUD = 0.6  # Ajustable según tu tolerancia

def generar_embedding(ruta_imagen):
    """
    Genera el embedding facial desde una imagen y verifica si ya existe uno similar.
    """
    image = face_recognition.load_image_file(ruta_imagen)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        raise RuntimeError("No se detectó ninguna cara en la imagen.")

    nuevo_embedding = encodings[0]

    # Cargar base existente
    if os.path.exists(RUTA_EMBEDDINGS):
        with open(RUTA_EMBEDDINGS, "r") as f:
            base = json.load(f)
    else:
        base = {}

    # Comparar con embeddings existentes
    for legajo, datos in base.items():
        existente = np.array(datos["embedding"])
        distancia = np.linalg.norm(nuevo_embedding - existente)
        if distancia < UMBRAL_SIMILITUD:
            raise RuntimeError(f"Ya existe un empleado con embedding similar (legajo: {legajo})")

    return nuevo_embedding.tolist()
