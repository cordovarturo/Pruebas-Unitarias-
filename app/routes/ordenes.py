from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.producto import Producto
from app.models.orden import Orden, OrdenDetalle

ordenes_bp = Blueprint("ordenes", __name__)

@ordenes_bp.route("/", methods=["POST"])
@jwt_required()
def crear_orden():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Se requiere JSON"}), 400

    productos_pedido = datos.get("productos", [])
    if not productos_pedido:
        return jsonify({"error": "Se requiere al menos un producto"}), 400

    # Verificar stock antes de modificar nada (transacción atómica)
    items = []
    for item in productos_pedido:
        prod = db.session.get(Producto, item["producto_id"])
        if not prod:
            return jsonify({"error": f"Producto {item['producto_id']} no encontrado"}), 404
        cantidad = item["cantidad"]
        if prod.stock < cantidad:
            return jsonify({
                "error": f"Stock insuficiente para '{prod.nombre}'. "
                         f"Disponible: {prod.stock}, solicitado: {cantidad}"
            }), 400
        items.append((prod, cantidad))

    # Crear la orden
    total = sum(prod.precio * cantidad for prod, cantidad in items)
    orden = Orden(cliente_id=datos.get("cliente_id", 1), total=total)
    db.session.add(orden)
    db.session.flush()  # Para obtener el ID sin commit

    for prod, cantidad in items:
        detalle = OrdenDetalle(
            orden_id=orden.id,
            producto_id=prod.id,
            cantidad=cantidad,
            precio_unitario=prod.precio,
        )
        db.session.add(detalle)
        prod.stock -= cantidad

    db.session.commit()

    return jsonify({
        "orden_id": orden.id,
        "total": orden.total,
        "productos_comprados": len(items),
    }), 201


@ordenes_bp.route("/", methods=["GET"])
@jwt_required()
def listar_ordenes():
    ordenes = Orden.query.all()
    return jsonify({"ordenes": [o.to_dict() for o in ordenes]}), 200
