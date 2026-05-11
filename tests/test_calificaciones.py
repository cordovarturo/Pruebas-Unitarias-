"""
Suite 4: Pruebas de relaciones entre tablas y cálculos estadísticos.
"""
import pytest


class TestRegistroCalificaciones:

    @pytest.fixture(autouse=True)
    def setup(self, client, auth_headers, estudiante_data):
        """
        autouse=True: este fixture se ejecuta AUTOMÁTICAMENTE antes
        de cada prueba de esta clase. Crea los datos base necesarios.
        """
        # Crear estudiante
        resp_est = client.post("/api/estudiantes/", json=estudiante_data)
        self.id_estudiante = resp_est.get_json()["estudiante"]["id"]

        # Crear materia
        resp_mat = client.post("/api/materias/", json={
            "clave": "PROG101",
            "nombre": "Programación Web",
            "creditos": 5,
            "docente": "Dr. Test",
        }, headers=auth_headers)
        self.id_materia = resp_mat.get_json()["materia"]["id"]

        self.client = client
        self.auth_headers = auth_headers

    def test_registrar_calificacion_valida(self):
        """Registrar una calificación entre 0 y 100 debe retornar 201."""
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 87.5,
            "periodo": "2024-1",
        })
        assert resp.status_code == 201
        datos = resp.get_json()
        assert datos["calificacion"] == 87.5
        assert datos["aprobado"] == True

    @pytest.mark.parametrize("cal_invalida", [-1, 100.1, 200, -50])
    def test_calificacion_fuera_de_rango(self, cal_invalida):
        """Calificaciones fuera de 0-100 deben retornar 400."""
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": cal_invalida,
        })
        assert resp.status_code == 400, \
            f"Calificación {cal_invalida} debería ser rechazada"

    def test_calificacion_exactamente_cero(self):
        """Caso borde: 0 es válido (reprobado pero válido)."""
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 0,
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == False

    def test_calificacion_exactamente_cien(self):
        """Caso borde: 100 es válido (calificación perfecta)."""
        resp = self.client.post("/api/calificaciones/", json={
            "estudiante_id": self.id_estudiante,
            "materia_id": self.id_materia,
            "calificacion": 100,
        })
        assert resp.status_code == 201
        assert resp.get_json()["aprobado"] == True


class TestKardex:

    def test_kardex_calcula_promedio_correctamente(self, client, auth_headers, estudiante_data):
        """
        El kardex debe calcular el promedio general correctamente.
        Con calificaciones: 80, 90, 70 → promedio esperado: 80.0
        """
        # Setup: crear estudiante y materias
        id_est = client.post("/api/estudiantes/", json=estudiante_data) \
            .get_json()["estudiante"]["id"]

        calificaciones_a_registrar = [
            ("MAT101", "Matemáticas", 80),
            ("FIS101", "Física", 90),
            ("QUI101", "Química", 70),
        ]

        for clave, nombre, cal in calificaciones_a_registrar:
            mat = client.post("/api/materias/", json={
                "clave": clave, "nombre": nombre, "creditos": 4,
            }, headers=auth_headers).get_json()["materia"]

            client.post("/api/calificaciones/", json={
                "estudiante_id": id_est,
                "materia_id": mat["id"],
                "calificacion": cal,
            })

        # Act: obtener kardex
        resp = client.get(f"/api/estudiantes/{id_est}/kardex")
        assert resp.status_code == 200
        kardex = resp.get_json()

        # Assert: verificar cálculos
        estadisticas = kardex["estadisticas"]
        assert estadisticas["promedio_general"] == 80.0
        assert estadisticas["total_materias"] == 3
        assert estadisticas["materias_aprobadas"] == 3
        assert estadisticas["materias_reprobadas"] == 0
        assert estadisticas["calificacion_maxima"] == 90
        assert estadisticas["calificacion_minima"] == 70

    def test_kardex_detecta_estatus_en_riesgo(self, client, auth_headers, estudiante_data):
        """Un promedio menor a 70 debe marcarse como 'En riesgo'."""
        id_est = client.post("/api/estudiantes/", json=estudiante_data) \
            .get_json()["estudiante"]["id"]

        mat = client.post("/api/materias/", json={
            "clave": "REP101", "nombre": "Reprobada", "creditos": 3,
        }, headers=auth_headers).get_json()["materia"]

        client.post("/api/calificaciones/", json={
            "estudiante_id": id_est,
            "materia_id": mat["id"],
            "calificacion": 50,  # ← Reprobado
        })

        kardex = client.get(f"/api/estudiantes/{id_est}/kardex").get_json()
        assert kardex["estadisticas"]["estatus"] == "En riesgo"
        assert kardex["estadisticas"]["materias_reprobadas"] == 1

    def test_kardex_sin_calificaciones(self, client, estudiante_data):
        """Un estudiante sin calificaciones debe retornar 200 con lista vacía."""
        id_est = client.post("/api/estudiantes/", json=estudiante_data) \
            .get_json()["estudiante"]["id"]

        resp = client.get(f"/api/estudiantes/{id_est}/kardex")
        assert resp.status_code == 200
        datos = resp.get_json()
        assert datos["calificaciones"] == []
        assert "mensaje" in datos
