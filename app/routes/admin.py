from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(id):
    uid = get_jwt_identity()
    usuario_actual = db.session.get(Usuario, int(uid))
    if not usuario_actual or usuario_actual.rol != "admin":
        return jsonify({"error": "Solo administradores pueden eliminar usuarios"}), 403

    usuario = db.session.get(Usuario, id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario eliminado"}), 200
