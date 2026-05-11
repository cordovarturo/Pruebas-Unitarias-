from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.producto import Producto
from app.models.usuario import Usuario

productos_bp = Blueprint("productos", __name__)

def _get_usuario_actual():
    try:
        from flask_jwt_extended import get_jwt_identity
        uid = get_jwt_identity()
        return db.session.get(Usuario, int(uid)) if uid else None
    except Exception:
        return None

@productos_bp.route("/", methods=["POST"])
@jwt_required()
def crear_producto():
    uid = get_jwt_identity()
    usuario = db.session.get(Usuario, int(uid))
    if not usuario or usuario.rol not in ("admin",):
        return jsonify({"error": "Solo administradores pueden crear productos"}), 403

    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    for campo in ["sku", "nombre", "precio"]:
        if campo not in datos:
            return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

    if Producto.query.filter_by(sku=datos["sku"]).first():
        return jsonify({"error": "El SKU ya existe"}), 409

    prod = Producto(
        sku=datos["sku"],
        nombre=datos["nombre"],
        precio=datos["precio"],
        stock=datos.get("stock", 0),
        categoria_id=datos.get("categoria_id"),
    )
    db.session.add(prod)
    db.session.commit()
    return jsonify({"producto": prod.to_dict()}), 201


@productos_bp.route("/", methods=["GET"])
def listar_productos():
    buscar = request.args.get("buscar", "")
    query = Producto.query
    if buscar:
        query = query.filter(Producto.nombre.ilike(f"%{buscar}%"))
    productos = query.all()
    return jsonify({"productos": [p.to_dict() for p in productos]}), 200


@productos_bp.route("/<int:id>", methods=["GET"])
def obtener_producto(id):
    prod = db.session.get(Producto, id)
    if not prod:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(prod.to_dict()), 200
