from datetime import datetime
from app import db

class Calificacion(db.Model):
    __tablename__ = "calificaciones"

    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id"), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), nullable=False)
    calificacion = db.Column(db.Float, nullable=False)
    periodo = db.Column(db.String(20), nullable=True, default="2024-1")
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def aprobado(self):
        return self.calificacion >= 60

    def to_dict(self):
        return {
            "id": self.id,
            "estudiante_id": self.estudiante_id,
            "materia_id": self.materia_id,
            "calificacion": self.calificacion,
            "aprobado": self.aprobado,
            "periodo": self.periodo,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }

    def __repr__(self):
        return f"<Calificacion est={self.estudiante_id} mat={self.materia_id} cal={self.calificacion}>"
