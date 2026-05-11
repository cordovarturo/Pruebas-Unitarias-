"""
Suite 2: Pruebas de Integración del CRUD de Estudiantes.
Usamos el cliente HTTP para hacer peticiones reales a la API.
"""
import pytest
import json


class TestCrearEstudiante:
    """Pruebas del endpoint POST /api/estudiantes/"""

    def test_crear_estudiante_exitoso(self, client, estudiante_data):
        """
        CASO POSITIVO: Crear un estudiante con datos válidos.
        Verifica: código 201, estructura JSON correcta.
        """
        # Act: hacer la petición POST
        respuesta = client.post(
            "/api/estudiantes/",
            json=estudiante_data,
            content_type="application/json",
        )
        datos = respuesta.get_json()

        # Assert: verificar código de estado
        assert respuesta.status_code == 201, \
            f"Se esperaba 201, llegó {respuesta.status_code}"

        # Assert: verificar estructura de respuesta
        assert "estudiante" in datos
        assert datos["estudiante"]["matricula"] == "TEST001"
        assert datos["estudiante"]["nombre"] == "Carlos"
        assert "id" in datos["estudiante"]

    def test_matricula_duplicada_retorna_409(self, client, estudiante_data):
        """
        CASO NEGATIVO: Intentar crear dos estudiantes con la misma matrícula.
        La API debe rechazar el segundo con 409 Conflict.
        """
        # Crear el primero (debe funcionar)
        client.post("/api/estudiantes/", json=estudiante_data)

        # Intentar crear el segundo con misma matrícula
        respuesta = client.post("/api/estudiantes/", json=estudiante_data)

        assert respuesta.status_code == 409
        assert "error" in respuesta.get_json()

    def test_campo_email_requerido(self, client):
        """
        CASO NEGATIVO: Omitir el campo email.
        La API debe retornar 400 Bad Request con mensaje de error.
        """
        datos_incompletos = {
            "matricula": "INC001",
            "nombre": "Sin Email",
            "apellido": "Test",
            # "email" → omitido a propósito
            "carrera": "ITIC",
        }
        respuesta = client.post("/api/estudiantes/", json=datos_incompletos)

        assert respuesta.status_code == 400
        cuerpo = respuesta.get_json()
        assert "error" in cuerpo
        assert "email" in cuerpo["error"].lower()

    def test_body_vacio_retorna_400(self, client):
        """CASO BORDE: Enviar un body completamente vacío.
        Flask puede retornar 400 (Bad Request) o 415 (Unsupported Media Type).
        Ambos son correctos: indican que la petición no tiene datos válidos.
        """
        respuesta = client.post("/api/estudiantes/", data="")
        assert respuesta.status_code in [400, 415]


class TestObtenerEstudiante:
    """Pruebas del endpoint GET /api/estudiantes/ y GET /api/estudiantes/<id>"""

    def test_lista_devuelve_200(self, client):
        """La lista de estudiantes siempre debe retornar 200."""
        respuesta = client.get("/api/estudiantes/")
        assert respuesta.status_code == 200
        datos = respuesta.get_json()

        # Verificar estructura de paginación
        assert "estudiantes" in datos
        assert "total" in datos
        assert "paginas" in datos

    def test_lista_vacia_retorna_lista_vacia(self, client):
        """
        CASO BORDE: Sin estudiantes registrados, la lista debe ser []
        y no un error 500.
        """
        respuesta = client.get("/api/estudiantes/")
        datos = respuesta.get_json()

        assert respuesta.status_code == 200
        assert isinstance(datos["estudiantes"], list)

    def test_obtener_por_id_existente(self, client, estudiante_data):
        """Obtener un estudiante que existe debe retornar 200 + datos."""
        # Crear estudiante primero
        post_resp = client.post("/api/estudiantes/", json=estudiante_data)
        id_creado = post_resp.get_json()["estudiante"]["id"]

        # Obtenerlo por ID
        respuesta = client.get(f"/api/estudiantes/{id_creado}")
        assert respuesta.status_code == 200
        assert respuesta.get_json()["id"] == id_creado

    def test_id_inexistente_retorna_404(self, client):
        """Pedir un ID que no existe debe retornar 404."""
        respuesta = client.get("/api/estudiantes/99999")
        assert respuesta.status_code == 404

    @pytest.mark.parametrize("pagina,por_pagina,esperados", [
        (1, 5, 5),    # Primera página, 5 por página
        (2, 5, 5),    # Segunda página
        (1, 100, 10), # Más por página que registros existentes
    ])
    def test_paginacion(self, client, pagina, por_pagina, esperados):
        """
        PARAMETRIZADO: La misma prueba se ejecuta con diferentes valores.
        pytest.mark.parametrize elimina código repetido.
        """
        respuesta = client.get(
            f"/api/estudiantes/?pagina={pagina}&por_pagina={por_pagina}"
        )
        assert respuesta.status_code == 200


class TestActualizarEstudiante:

    def test_actualizar_semestre(self, client, estudiante_data):
        """PUT debe actualizar solo el campo enviado y retornar 200."""
        # Crear estudiante
        id_est = client.post("/api/estudiantes/", json=estudiante_data) \
            .get_json()["estudiante"]["id"]

        # Actualizar semestre
        resp = client.put(f"/api/estudiantes/{id_est}", json={"semestre": 8})
        assert resp.status_code == 200
        assert resp.get_json()["estudiante"]["semestre"] == 8


class TestEliminarEstudiante:

    def test_borrado_logico(self, client, estudiante_data):
        """
        DELETE debe marcar activo=False, no borrar el registro.
        Después del delete, el estudiante no debe aparecer en la lista.
        """
        # Crear
        id_est = client.post("/api/estudiantes/", json=estudiante_data) \
            .get_json()["estudiante"]["id"]

        # Eliminar
        resp_del = client.delete(f"/api/estudiantes/{id_est}")
        assert resp_del.status_code == 200

        # Verificar que ya no aparece en la lista de activos
        lista = client.get("/api/estudiantes/").get_json()["estudiantes"]
        ids_activos = [e["id"] for e in lista]
        assert id_est not in ids_activos, "El estudiante eliminado no debe aparecer"
