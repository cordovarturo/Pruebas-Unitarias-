import pytest
from app import create_app, db as _db
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.config import TestingConfig

# ─── Fixture: Aplicación de prueba ───────────────────────────────────
@pytest.fixture(scope="session")
def app():
    """
    Crea la aplicación Flask en modo de pruebas.
    scope="session" significa que se crea UNA VEZ para toda la sesión.
    """
    app = create_app(TestingConfig)
    yield app

# ─── Fixture: Base de datos ──────────────────────────────────────────
@pytest.fixture(scope="session")
def db(app):
    """
    Crea las tablas en la BD de prueba (SQLite en memoria).
    La BD desaparece al terminar la sesión de pruebas.
    ¡Nunca toca la BD real de PostgreSQL!
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

# ─── Fixture: Transacción limpia por prueba ──────────────────────────
@pytest.fixture(scope="function")
def session(db):
    """
    Cada prueba corre dentro de una transacción que se revierte al final.
    Esto garantiza que las pruebas sean INDEPENDIENTES entre sí.
    Patrón: "Arrange → Act → Assert → Rollback"
    """
    with db.engine.connect() as connection:
        transaction = connection.begin()
        db.session.bind = connection
        yield db.session
        db.session.remove()
        transaction.rollback()

# ─── Fixture: Cliente HTTP de prueba ─────────────────────────────────
@pytest.fixture(scope="function")
def client(app):
    """
    Cliente HTTP que simula peticiones a la API.
    Con él podemos hacer GET, POST, PUT, DELETE sin levantar el servidor.
    """
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()
        _db.create_all()

# ─── Fixture: Estudiante de prueba ───────────────────────────────────
@pytest.fixture
def estudiante_data():
    """Datos válidos de un estudiante para reutilizar en pruebas."""
    return {
        "matricula": "TEST001",
        "nombre": "Carlos",
        "apellido": "Ramírez",
        "email": "carlos@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5,
    }

# ─── Fixture: Token JWT de prueba ────────────────────────────────────
@pytest.fixture
def auth_headers(client):
    """
    Genera un token JWT válido para pruebas de rutas protegidas.
    Registra un usuario, hace login y devuelve los headers listos.
    """
    client.post("/api/auth/registro", json={
        "username": "docente_test",
        "email": "doc@test.mx",
        "password": "Password123!",
        "rol": "docente",
    })
    resp = client.post("/api/auth/login", json={
        "username": "docente_test",
        "password": "Password123!",
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
