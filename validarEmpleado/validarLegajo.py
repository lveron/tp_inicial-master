class ValidadorLegajo:
    def __init__(self, base_legajos):
        self.base = set(str(l).strip() for l in base_legajos)

    def validar(self, legajo):
        legajo = str(legajo).strip()
        if not legajo:
            return {"valido": False, "mensaje": "Legajo vacío."}
        if legajo not in self.base:
            return {"valido": False, "mensaje": f"Legajo {legajo} no encontrado."}
        return {"valido": True, "mensaje": "Legajo válido."}