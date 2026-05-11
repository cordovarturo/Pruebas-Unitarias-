from app import db

class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    categoria_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
            "categoria_id": self.categoria_id,
        }

    def __repr__(self):
        return f"<Producto {self.sku} - {self.nombre}>"
