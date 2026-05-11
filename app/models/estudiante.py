from datetime import datetime
from app import db

class Estudiante(db.Model):
    __tablename__ = "estudiantes"

    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    carrera = db.Column(db.String(100), nullable=False)
    semestre = db.Column(db.Integer, default=1)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    calificaciones = db.relationship("Calificacion", backref="estudiante", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "matricula": self.matricula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "carrera": self.carrera,
            "semestre": self.semestre,
            "activo": self.activo,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "nombre_completo": f"{self.nombre} {self.apellido}",
        }

    def __repr__(self):
        return f"<Estudiante {self.matricula} - {self.nombre}>"
