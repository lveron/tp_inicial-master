from reconocimiento.embedding import EmbeddingManager

def reconocer_empleado(frame, legajo, umbral=0.7):
    manager = EmbeddingManager()
    base = manager.cargar_embeddings()

    if legajo not in base:
        return {"estado": "legajo no encontrado", "coincide": False}

    try:
        emb_capturado = manager.generar_embedding(frame)
    except ValueError:
        return {"estado": "no se pudo generar embedding", "coincide": False}

    emb_guardado = base[legajo]["embedding"]
    coincide = manager.comparar_embeddings(emb_capturado, emb_guardado, threshold=umbral)

    return {
        "estado": "coincidencia" if coincide else "no coincide",
        "coincide": coincide,
        "legajo": legajo if coincide else None
    }
