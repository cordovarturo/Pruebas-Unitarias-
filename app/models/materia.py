from app import db

class Materia(db.Model):
    __tablename__ = "materias"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    creditos = db.Column(db.Integer, nullable=False)
    docente = db.Column(db.String(150), nullable=True)

    calificaciones = db.relationship("Calificacion", backref="materia", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "clave": self.clave,
            "nombre": self.nombre,
            "creditos": self.creditos,
            "docente": self.docente,
        }

    def __repr__(self):
        return f"<Materia {self.clave} - {self.nombre}>"
