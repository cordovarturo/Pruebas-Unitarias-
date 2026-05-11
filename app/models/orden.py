from datetime import datetime
from app import db

class OrdenDetalle(db.Model):
    __tablename__ = "orden_detalles"

    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("ordenes.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

class Orden(db.Model):
    __tablename__ = "ordenes"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, default=0.0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    detalles = db.relationship("OrdenDetalle", backref="orden", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "total": self.total,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
