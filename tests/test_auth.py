"""
Suite 3: Pruebas de Autenticación y Autorización JWT.
"""
import pytest


class TestRegistro:

    def test_registro_exitoso(self, client):
        """Registrar un usuario nuevo con datos válidos → 201."""
        resp = client.post("/api/auth/registro", json={
            "username": "nuevo_docente",
            "email": "nuevo@uni.mx",
            "password": "Segura123!",
            "rol": "docente",
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert "id" in datos
        assert "mensaje" in datos

    def test_username_duplicado(self, client):
        """Registrar dos usuarios con el mismo username → 409."""
        payload = {
            "username": "duplicado",
            "email": "a@test.mx",
            "password": "Pass1234!",
            "rol": "docente",
        }
        client.post("/api/auth/registro", json=payload)

        # Segundo intento con mismo username
        payload["email"] = "b@test.mx"  # Email diferente, username igual
        resp = client.post("/api/auth/registro", json=payload)
        assert resp.status_code == 409


class TestLogin:

    def test_login_exitoso_retorna_token(self, client):
        """
        Login con credenciales correctas debe retornar:
        - Código 200
        - Un token JWT (string no vacío)
        - Tipo "Bearer"
        - Información del usuario
        """
        # Registrar primero
        client.post("/api/auth/registro", json={
            "username": "user_login",
            "email": "ul@test.mx",
            "password": "LoginPass1!",
        })

        # Login
        resp = client.post("/api/auth/login", json={
            "username": "user_login",
            "password": "LoginPass1!",
        })
        assert resp.status_code == 200
        datos = resp.get_json()

        # Verificar token
        assert "token" in datos
        assert len(datos["token"]) > 50, "El token debe ser un JWT válido"
        assert datos["tipo"] == "Bearer"

        # Verificar info del usuario
        assert datos["usuario"]["username"] == "user_login"

    def test_password_incorrecta_retorna_401(self, client):
        """Credenciales incorrectas → 401 Unauthorized."""
        client.post("/api/auth/registro", json={
            "username": "user_401",
            "email": "u401@test.mx",
            "password": "CorrectPass1!",
        })
        resp = client.post("/api/auth/login", json={
            "username": "user_401",
            "password": "PasswordIncorrecta!",
        })
        assert resp.status_code == 401
        assert "error" in resp.get_json()

    def test_usuario_inexistente_retorna_401(self, client):
        """Un username que no existe → 401 (no 404, por seguridad)."""
        resp = client.post("/api/auth/login", json={
            "username": "noexisto",
            "password": "cualquiera",
        })
        # IMPORTANTE: Siempre 401, nunca 404.
        # Si dijéramos 404 estaríamos confirmando que el usuario no existe.
        assert resp.status_code == 401


class TestRutasProtegidas:

    def test_ruta_protegida_sin_token_retorna_401(self, client):
        """
        Acceder a una ruta protegida SIN token → 401.
        El decorador @jwt_required() debe bloquear el acceso.
        """
        resp = client.get("/api/auth/perfil")  # Sin header Authorization
        assert resp.status_code == 401

    def test_ruta_protegida_con_token_valido(self, client, auth_headers):
        """
        Con token válido en el header → 200.
        auth_headers viene del fixture en conftest.py.
        """
        resp = client.get("/api/auth/perfil", headers=auth_headers)
        assert resp.status_code == 200
        assert "usuario" in resp.get_json()

    def test_token_manipulado_retorna_422(self, client):
        """
        Un token modificado (firma inválida) debe ser rechazado.
        Simula un ataque de falsificación de token.
        """
        # Token JWT manipulado (payload real pero firma cambiada)
        token_falso = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIifQ.firma_falsa"
        headers = {"Authorization": f"Bearer {token_falso}"}
        resp = client.get("/api/auth/perfil", headers=headers)

        # Flask-JWT retorna 422 para tokens con formato inválido
        assert resp.status_code in [401, 422]

    def test_header_sin_bearer_retorna_error(self, client):
        """El header Authorization debe incluir la palabra 'Bearer'."""
        headers = {"Authorization": "token_directo_sin_bearer"}
        resp = client.get("/api/auth/perfil", headers=headers)
        assert resp.status_code in [401, 422]


class TestControlDeRoles:
    """
    Prueba que solo los usuarios con el rol correcto pueden
    acceder a ciertas rutas.
    """

    def test_docente_no_puede_acceder_a_ruta_admin(self, client, auth_headers):
        """
        Un usuario con rol "docente" NO debe poder acceder
        a rutas exclusivas de "admin".
        """
        resp = client.delete("/api/admin/usuarios/1", headers=auth_headers)
        # Esperamos 403 Forbidden (autenticado pero sin permisos)
        assert resp.status_code == 403
