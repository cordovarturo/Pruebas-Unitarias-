from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.materia import Materia

materias_bp = Blueprint("materias", __name__)

@materias_bp.route("/", methods=["POST"])
@jwt_required()
def crear_materia():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    for campo in ["clave", "nombre", "creditos"]:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    if Materia.query.filter_by(clave=datos["clave"]).first():
        return jsonify({"error": "La clave ya existe"}), 409

    materia = Materia(
        clave=datos["clave"],
        nombre=datos["nombre"],
        creditos=datos["creditos"],
        docente=datos.get("docente"),
    )
    db.session.add(materia)
    db.session.commit()
    return jsonify({"materia": materia.to_dict()}), 201


@materias_bp.route("/", methods=["GET"])
def listar_materias():
    materias = Materia.query.all()
    return jsonify({"materias": [m.to_dict() for m in materias]}), 200
