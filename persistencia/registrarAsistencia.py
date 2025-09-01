import json
import os
from datetime import datetime, timedelta


class RegistrarAsistencias:
    HORARIOS_TURNOS = {
        "mañana": {"ingreso": "08:00:00", "egreso": "14:00:00"},
        "tarde": {"ingreso": "14:00:00", "egreso": "18:00:00"},
        "noche": {"ingreso": "18:00:00", "egreso": "08:00:00"},
    }

    def __init__(self, ruta_json="data/asistencias.json"):
        self.ruta = os.path.normpath(ruta_json)
        self._asegurar_archivo()

    def _asegurar_archivo(self):
        if not os.path.exists(self.ruta):
            with open(self.ruta, "w") as f:
                json.dump([], f)

    def registrar(self, legajo, turno, tipo):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fecha_actual = timestamp.split(" ")[0]

        registros_hoy = [
            r for r in self.obtener_por_legajo(legajo)
            if r["timestamp"].startswith(fecha_actual)
        ]

        if any(r["tipo"].lower() == tipo.lower() for r in registros_hoy):
            return "ya registrado"

        estado = self._calcular_puntualidad(timestamp, tipo, turno)
        nueva_asistencia = {
            "legajo": legajo,
            "tipo": tipo,
            "timestamp": timestamp,
            "turno": turno,
            "estado": estado
        }

        asistencias = self._cargar()
        asistencias.append(nueva_asistencia)
        self._guardar(asistencias)
        return "registrado"

    def obtener_por_legajo(self, legajo):
        return [a for a in self._cargar() if a["legajo"] == legajo]

    def obtener_ultimo_tipo(self, legajo):
        asistencias = [
            a for a in self.obtener_por_legajo(legajo)
            if "timestamp" in a and "tipo" in a
        ]
        if not asistencias:
            return "Ingreso"

        asistencias.sort(key=lambda x: x["timestamp"], reverse=True)
        return "Egreso" if asistencias[0]["tipo"].lower() == "ingreso" else "Ingreso"

    def puede_registrar_hoy(self, legajo, tipo):
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        registros_hoy = [
            r for r in self.obtener_por_legajo(legajo)
            if r["timestamp"].startswith(fecha_actual)
        ]
        return not any(r["tipo"].lower() == tipo.lower() for r in registros_hoy)

    def calcular_puntualidad(self, timestamp, tipo, turno):
        turno = turno.strip().lower()
        tipo = tipo.strip().lower()
        dt_actual = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

        if turno not in self.HORARIOS_TURNOS:
            return "fuera de turno"

        ingreso_str = self.HORARIOS_TURNOS[turno]["ingreso"]
        egreso_str = self.HORARIOS_TURNOS[turno]["egreso"]

        dt_ingreso = datetime.combine(dt_actual.date(), datetime.strptime(ingreso_str, "%H:%M:%S").time())
        dt_egreso = datetime.combine(dt_actual.date(), datetime.strptime(egreso_str, "%H:%M:%S").time())

        if dt_egreso <= dt_ingreso:
            dt_egreso += timedelta(days=1)

        if not (dt_ingreso <= dt_actual <= dt_egreso):
            return "fuera de turno"

        if tipo == "ingreso":
            return "puntual" if dt_actual <= dt_ingreso else "tarde"
        elif tipo == "egreso":
            return "puntual" if dt_actual >= dt_egreso else "temprano"

        return "tipo desconocido"

    def _cargar(self):
        with open(self.ruta, "r") as f:
            return json.load(f)

    def _guardar(self, asistencias):
        with open(self.ruta, "w") as f:
            json.dump(asistencias, f, indent=2)

