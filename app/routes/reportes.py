from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.orden import Orden, OrdenDetalle
from app.models.producto import Producto
from app.models.usuario import Usuario

reportes_bp = Blueprint("reportes", __name__)

@reportes_bp.route("/ventas", methods=["GET"])
@jwt_required()
def reporte_ventas():
    uid = get_jwt_identity()
    usuario = db.session.get(Usuario, int(uid))
    if not usuario or usuario.rol != "admin":
        return jsonify({"error": "Solo administradores pueden ver reportes"}), 403

    ordenes = Orden.query.all()
    total_ingresos = sum(o.total for o in ordenes)

    # Top productos por cantidad vendida
    from sqlalchemy import func
    top = (
        db.session.query(
            Producto.nombre,
            func.sum(OrdenDetalle.cantidad).label("vendidos")
        )
        .join(OrdenDetalle, OrdenDetalle.producto_id == Producto.id)
        .group_by(Producto.id)
        .order_by(func.sum(OrdenDetalle.cantidad).desc())
        .limit(5)
        .all()
    )

    return jsonify({
        "resumen": {
            "total_ordenes": len(ordenes),
            "ingresos": total_ingresos,
        },
        "top_productos": [{"nombre": n, "vendidos": v} for n, v in top],
    }), 200
