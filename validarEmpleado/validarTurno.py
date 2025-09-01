class ValidadorTurno:
    def __init__(self, base_empleados):
        self.base = base_empleados

    def validar(self, legajo, turno_ingresado):
        turno_ingresado = turno_ingresado.strip().lower()

        if legajo not in self.base:
            return {"valido": False, "mensaje": f"Legajo {legajo} no existe."}

        turno_real = self.base[legajo].get("turno", "").strip().lower()
        if not turno_real:
            return {"valido": False, "mensaje": f"Turno no definido para legajo {legajo}."}

        if turno_ingresado == turno_real:
            return {"valido": True, "mensaje": "Turno válido."}
        else:
            return {
                "valido": False,
                "mensaje": f"Turno incorrecto. Se esperaba '{turno_real}', se ingresó '{turno_ingresado}'."
            }
