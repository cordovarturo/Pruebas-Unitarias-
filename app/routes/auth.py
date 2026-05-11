from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    username = datos.get("username")
    email = datos.get("email")
    password = datos.get("password")
    rol = datos.get("rol", "docente")

    if not username or not email or not password:
        return jsonify({"error": "username, email y password son requeridos"}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"error": "El username ya existe"}), 409

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    usuario = Usuario(username=username, email=email, rol=rol)
    usuario.set_password(password)
    db.session.add(usuario)
    db.session.commit()

    return jsonify({"id": usuario.id, "mensaje": "Usuario registrado exitosamente"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    username = datos.get("username")
    password = datos.get("password")

    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario or not usuario.check_password(password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    token = create_access_token(identity=str(usuario.id))
    return jsonify({
        "token": token,
        "tipo": "Bearer",
        "usuario": usuario.to_dict(),
    }), 200


@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    user_id = get_jwt_identity()
    usuario = db.session.get(Usuario, int(user_id))
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"usuario": usuario.to_dict()}), 200
