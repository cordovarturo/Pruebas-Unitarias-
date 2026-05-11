from flask import Blueprint, request, jsonify
from app import db
from app.models.calificacion import Calificacion
from app.models.estudiante import Estudiante
from app.models.materia import Materia

calificaciones_bp = Blueprint("calificaciones", __name__)

@calificaciones_bp.route("/", methods=["POST"])
def registrar_calificacion():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    for campo in ["estudiante_id", "materia_id", "calificacion"]:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    cal_valor = datos["calificacion"]
    if not isinstance(cal_valor, (int, float)) or cal_valor < 0 or cal_valor > 100:
        return jsonify({"error": "La calificación debe estar entre 0 y 100"}), 400

    if not db.session.get(Estudiante, datos["estudiante_id"]):
        return jsonify({"error": "Estudiante no encontrado"}), 404

    if not db.session.get(Materia, datos["materia_id"]):
        return jsonify({"error": "Materia no encontrada"}), 404

    cal = Calificacion(
        estudiante_id=datos["estudiante_id"],
        materia_id=datos["materia_id"],
        calificacion=cal_valor,
        periodo=datos.get("periodo", "2024-1"),
    )
    db.session.add(cal)
    db.session.commit()

    resultado = cal.to_dict()
    return jsonify(resultado), 201


@calificaciones_bp.route("/", methods=["GET"])
def listar_calificaciones():
    cals = Calificacion.query.all()
    return jsonify({"calificaciones": [c.to_dict() for c in cals]}), 200
