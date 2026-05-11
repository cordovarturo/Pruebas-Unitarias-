"""
Suite 1: Pruebas Unitarias de Modelos
Estas pruebas verifican que los modelos funcionan correctamente
de forma AISLADA, sin necesidad de la API completa.
"""
import pytest
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.models.materia import Materia


# ════════════════════════════════════════════════════════════
# CLASE 1: Pruebas del modelo Estudiante
# ════════════════════════════════════════════════════════════
class TestModeloEstudiante:

    def test_crear_estudiante_con_datos_validos(self, session):
        """
        CASO POSITIVO: Verifica que un estudiante se crea correctamente
        con todos los campos requeridos.
        Patrón AAA (Arrange-Act-Assert).
        """
        # ── Arrange ──
        datos = {
            "matricula": "ITIC001",
            "nombre": "María",
            "apellido": "González",
            "email": "maria@uni.edu.mx",
            "carrera": "ITIC",
            "semestre": 5,
        }
        # ── Act ──
        est = Estudiante(**datos)
        session.add(est)
        session.commit()

        # ── Assert ──
        assert est.id is not None, "El ID debe generarse automáticamente"
        assert est.nombre == "María", "El nombre debe guardarse igual"
        assert est.activo == True, "El estudiante debe estar activo por defecto"
        assert est.semestre == 5, "El semestre debe ser 5"
        assert est.fecha_registro is not None, "Debe tener fecha de registro"

    def test_to_dict_contiene_campos_requeridos(self, session):
        """
        Verifica que el método to_dict() retorna exactamente
        los campos que necesita el frontend.
        """
        est = Estudiante(
            matricula="ITIC002", nombre="Pedro", apellido="Sosa",
            email="pedro@uni.edu.mx", carrera="ITIC", semestre=3,
        )
        session.add(est)
        session.commit()

        resultado = est.to_dict()

        campos_esperados = [
            "id", "matricula", "nombre", "apellido",
            "email", "carrera", "semestre", "activo",
            "fecha_registro", "nombre_completo",
        ]
        for campo in campos_esperados:
            assert campo in resultado, f"Falta el campo: {campo}"

        assert resultado["nombre_completo"] == "Pedro Sosa"
        assert resultado["activo"] == True

    def test_repr_retorna_string_legible(self, session):
        """El método __repr__ debe retornar una cadena descriptiva."""
        est = Estudiante(
            matricula="ITIC003", nombre="Luis", apellido="Pérez",
            email="luis@uni.edu.mx", carrera="ITIC", semestre=1,
        )
        representacion = repr(est)
        assert "ITIC003" in representacion
        assert "Luis" in representacion

    def test_semestre_por_defecto_es_uno(self, session):
        """Si no se especifica semestre, debe ser 1 por defecto."""
        est = Estudiante(
            matricula="ITIC004", nombre="Ana", apellido="Cruz",
            email="ana@uni.edu.mx", carrera="ITIC",
            # ← No pasamos semestre
        )
        session.add(est)
        session.commit()
        assert est.semestre == 1


# ════════════════════════════════════════════════════════════
# CLASE 2: Pruebas del modelo Usuario (seguridad de contraseñas)
# ════════════════════════════════════════════════════════════
class TestModeloUsuario:

    def test_password_se_hashea_al_guardar(self, session):
        """
        CRÍTICO: La contraseña NUNCA debe guardarse en texto plano.
        Verificamos que set_password() almacena el hash, no el original.
        """
        usuario = Usuario(username="profe01", email="profe@uni.mx")
        usuario.set_password("MiPassword123")

        assert usuario.password_hash != "MiPassword123", \
            "¡ERROR CRÍTICO! La contraseña está en texto plano"
        assert len(usuario.password_hash) > 50, \
            "El hash debe ser suficientemente largo"

    def test_check_password_valida_correctamente(self, session):
        """check_password debe retornar True con la contraseña correcta."""
        usuario = Usuario(username="profe02", email="profe2@uni.mx")
        usuario.set_password("Segura456!")

        assert usuario.check_password("Segura456!") == True
        assert usuario.check_password("incorrecta") == False
        assert usuario.check_password("") == False
        assert usuario.check_password("Segura456") == False  # Sin "!"

    def test_rol_por_defecto_es_docente(self, session):
        """Si no se especifica rol, debe ser 'docente'."""
        usuario = Usuario(username="nuevo", email="nuevo@uni.mx")
        usuario.set_password("pass")
        session.add(usuario)
        session.commit()
        assert usuario.rol == "docente"


# ════════════════════════════════════════════════════════════
# CLASE 3: Pruebas del modelo Materia
# ════════════════════════════════════════════════════════════
class TestModeloMateria:

    def test_crear_materia_exitosamente(self, session):
        """Una materia debe guardarse con todos sus campos."""
        materia = Materia(
            clave="PROG101", nombre="Programación Web",
            creditos=5, docente="Dr. Hernández",
        )
        session.add(materia)
        session.commit()

        assert materia.id is not None
        assert materia.clave == "PROG101"
        assert materia.creditos == 5
