from flask import Blueprint, request, jsonify
from app import db
from app.models.estudiante import Estudiante
from app.models.calificacion import Calificacion

estudiantes_bp = Blueprint("estudiantes", __name__)

@estudiantes_bp.route("/", methods=["POST"])
def crear_estudiante():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    campos_requeridos = ["matricula", "nombre", "apellido", "email", "carrera"]
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    if Estudiante.query.filter_by(matricula=datos["matricula"]).first():
        return jsonify({"error": "La matrícula ya existe"}), 409

    if Estudiante.query.filter_by(email=datos["email"]).first():
        return jsonify({"error": "El email ya existe"}), 409

    est = Estudiante(
        matricula=datos["matricula"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        email=datos["email"],
        carrera=datos["carrera"],
        semestre=datos.get("semestre", 1),
    )
    db.session.add(est)
    db.session.commit()
    return jsonify({"estudiante": est.to_dict()}), 201


@estudiantes_bp.route("/", methods=["GET"])
def listar_estudiantes():
    pagina = request.args.get("pagina", 1, type=int)
    por_pagina = request.args.get("por_pagina", 10, type=int)

    query = Estudiante.query.filter_by(activo=True)
    paginado = query.paginate(page=pagina, per_page=por_pagina, error_out=False)

    return jsonify({
        "estudiantes": [e.to_dict() for e in paginado.items],
        "total": paginado.total,
        "paginas": paginado.pages,
        "pagina_actual": pagina,
    }), 200


@estudiantes_bp.route("/<int:id>", methods=["GET"])
def obtener_estudiante(id):
    est = db.session.get(Estudiante, id)
    if not est or not est.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify(est.to_dict()), 200


@estudiantes_bp.route("/<int:id>", methods=["PUT"])
def actualizar_estudiante(id):
    est = db.session.get(Estudiante, id)
    if not est or not est.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    datos = request.get_json() or {}
    for campo in ["nombre", "apellido", "email", "carrera", "semestre"]:
        if campo in datos:
            setattr(est, campo, datos[campo])

    db.session.commit()
    return jsonify({"estudiante": est.to_dict()}), 200


@estudiantes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_estudiante(id):
    est = db.session.get(Estudiante, id)
    if not est or not est.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    est.activo = False
    db.session.commit()
    return jsonify({"mensaje": "Estudiante eliminado correctamente"}), 200


@estudiantes_bp.route("/<int:id>/kardex", methods=["GET"])
def kardex(id):
    est = db.session.get(Estudiante, id)
    if not est:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    calificaciones = Calificacion.query.filter_by(estudiante_id=id).all()

    if not calificaciones:
        return jsonify({
            "estudiante": est.to_dict(),
            "calificaciones": [],
            "mensaje": "El estudiante no tiene calificaciones registradas",
        }), 200

    valores = [c.calificacion for c in calificaciones]
    promedio = sum(valores) / len(valores)
    aprobadas = sum(1 for v in valores if v >= 60)
    reprobadas = len(valores) - aprobadas

    if promedio < 70:
        estatus = "En riesgo"
    elif promedio < 85:
        estatus = "Regular"
    else:
        estatus = "Bueno"

    return jsonify({
        "estudiante": est.to_dict(),
        "calificaciones": [c.to_dict() for c in calificaciones],
        "estadisticas": {
            "promedio_general": round(promedio, 2),
            "total_materias": len(calificaciones),
            "materias_aprobadas": aprobadas,
            "materias_reprobadas": reprobadas,
            "calificacion_maxima": max(valores),
            "calificacion_minima": min(valores),
            "estatus": estatus,
        },
    }), 200
