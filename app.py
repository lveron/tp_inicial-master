# app.py
import datetime
from datetime import datetime

from deepface import DeepFace
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_cors import CORS

from generarEmbedinng import generar_embedding
from persistencia.registrarAsistencia import RegistrarAsistencias
from reconocimiento.verificador import reconocer_empleado
from validarEmpleado.validarLegajo import ValidadorLegajo
from validarEmpleado.validarTurno import ValidadorTurno
import cv2
import numpy as np
import json
import os

app = Flask(__name__)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/')
def home():
    return "Backend activo"
def cargar_base_empleados():
    ruta = os.path.normpath("data/embeddings.json")
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
base = cargar_base_empleados()  # función que carga tu JSON
val_legajo = ValidadorLegajo(base)
val_turno = ValidadorTurno(base)
asistencia = RegistrarAsistencias()

@app.route("/validar", methods=["POST"])
def validar():
    data = request.get_json()
    legajo = data.get("legajo")
    turno = data.get("turno")

    if not legajo or not turno:
        return jsonify({"valido": False, "mensaje": "Faltan datos."})

    r1 = val_legajo.validar(legajo)
    if not r1["valido"]:
        return jsonify(r1)

    r2 = val_turno.validar(legajo, turno)
    return jsonify(r2)

@app.route("/reconocer", methods=["POST"])
def reconocer():
    legajo = request.form.get("legajo")
    turno = request.form.get("turno")
    imagen_file = request.files.get("imagen")

    if not legajo or not turno:
        return jsonify({"exito": False, "mensaje": "Faltan datos."}), 400

    if not imagen_file:
        print("⚠️ No se recibió imagen en el request.")
        return jsonify({"exito": False, "mensaje": "No se recibió imagen."}), 400

    try:
        npimg = np.frombuffer(imagen_file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    except Exception as e:
        print("❌ Error al decodificar imagen:", e)
        return jsonify({"exito": False, "mensaje": "Error al procesar imagen."}), 500

    print("📸 Imagen recibida correctamente para legajo:", legajo)

    resultado = reconocer_empleado(frame, legajo)
    if not resultado["coincide"]:
        return jsonify({"exito": False, "mensaje": "Empleado no reconocido."})

    tipo = asistencia.obtener_ultimo_tipo(legajo)
    if not asistencia.puede_registrar_hoy(legajo, tipo):
        return jsonify({"exito": False, "mensaje": f"Ya se registró un {tipo.lower()} hoy."})

    estado = asistencia.calcular_puntualidad(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo, turno)
    if estado == "fuera de turno":
        return jsonify({"exito": False, "mensaje": "Fuera de turno."})

    asistencia.registrar(legajo, turno, tipo)
    return jsonify({"exito": True, "mensaje": f"{tipo} registrado correctamente."})

@app.route("/ping", methods=["GET"])
def ping():
    print("📡 Recibí un ping desde el navegador")
    return jsonify({"mensaje": "Conexión OK"})

# Crear carpeta temp si no existe
if not os.path.exists("temp"):
    os.makedirs("temp")
@app.route("/registrar_empleado", methods=["POST"])
def registrar_empleado():
    imagen_file = request.files.get("imagen")
    legajo = request.form.get("legajo", "").strip()
    area = request.form.get("area", "").strip()
    rol = request.form.get("rol", "").strip()
    turno = request.form.get("turno", "").strip()

    if not imagen_file or not legajo or not area or not rol or not turno:
        return jsonify({"exito": False, "mensaje": "Faltan datos o imagen"}), 400

    base = cargar_base_empleados()
    if legajo in base:
        return jsonify({"exito": False, "mensaje": "Legajo ya registrado"}), 400

    # Guardar imagen temporal
    ruta_temp = f"temp/{legajo}.jpg"
    imagen_file.save(ruta_temp)

    # Generar embedding
    try:
        embedding = generar_embedding(ruta_temp)
    except Exception as e:
        return jsonify({"exito": False, "mensaje": f"Error al procesar imagen: {str(e)}"}), 500

    if not isinstance(embedding, list) or len(embedding) < 128:
        return jsonify({"exito": False, "mensaje": "Embedding inválido"}), 400

    # Guardar en base
    base[legajo] = {
        "area": area,
        "rol": rol,
        "turno": turno,
        "embedding": embedding
    }

    with open("data/embeddings.json", "w") as f:
        json.dump(base, f, indent=4)

    os.remove(ruta_temp)

    return jsonify({"exito": True, "mensaje": "Empleado registrado correctamente"})



if __name__ == "__main__":
    app.run(debug=True)

