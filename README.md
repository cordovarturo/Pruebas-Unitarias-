#  Pruebas Unitarias — API REST con Flask

**Nombre:** Arturo Israel Martínez Córdova  
**Matrícula:** 1224100528  
**Grupo:** GTID153  
**Materia:** Aplicaciones Web Orientadas a Servicios

---

## ¿De qué trata este proyecto?

Este proyecto es una API REST completa hecha con Python y Flask. Incluye manejo de estudiantes, calificaciones, materias, productos y órdenes, todo protegido con autenticación JWT. Lo más importante: tiene **5 suites de pruebas automáticas** que verifican que todo funcione correctamente.

---

##  Cómo está organizado el proyecto

```
Pruebas-unitarias-main/
├── app/
│   ├── __init__.py          ← Crea y configura la app Flask
│   ├── config.py            ← Configuraciones (desarrollo, pruebas, producción)
│   ├── models/              ← Modelos de la base de datos
│   │   ├── estudiante.py
│   │   ├── usuario.py
│   │   ├── materia.py
│   │   ├── calificacion.py
│   │   ├── producto.py
│   │   └── orden.py
│   └── routes/              ← Endpoints de la API
│       ├── auth.py          ← Registro y login
│       ├── estudiantes.py
│       ├── calificaciones.py
│       ├── materias.py
│       ├── productos.py
│       ├── ordenes.py
│       ├── reportes.py
│       └── admin.py
├── tests/
│   ├── conftest.py          ← Configuración compartida de todas las pruebas
│   ├── test_modelos.py      ← Suite 1: pruebas de los modelos
│   ├── test_estudiantes.py  ← Suite 2: pruebas del CRUD de estudiantes
│   ├── test_auth.py         ← Suite 3: pruebas de autenticación JWT
│   ├── test_calificaciones.py ← Suite 4: pruebas de calificaciones
│   └── test_tienda.py       ← Suite 5: prueba completa de la tienda
├── run.py                   ← Archivo para iniciar el servidor
├── pytest.ini               ← Configuración de pytest
└── requirements.txt         ← Dependencias del proyecto
```

---

##  Comandos para correrlo (ejecuta uno por uno en la terminal de VS Code)

### Paso 1 — Abrir la terminal en VS Code

Presiona `Ctrl + ñ` (o ve a **Terminal → New Terminal**) y asegúrate de estar dentro de la carpeta del proyecto:

```bash
cd Pruebas-unitarias-main
```

### Paso 2 — Crear el entorno virtual

```bash
python -m venv venv
```

### Paso 3 — Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

Cuando esté activo verás `(venv)` al inicio de la línea en la terminal.

### Paso 4 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

### Paso 5 — Correr las pruebas

```bash
pytest
```

Esto ejecuta todas las suites automáticamente y muestra el reporte de cobertura.

---

##  Resultado esperado al correr las pruebas

```
tests/test_modelos.py::TestModeloEstudiante::...         PASSED
tests/test_modelos.py::TestModeloUsuario::...            PASSED
tests/test_modelos.py::TestModeloMateria::...            PASSED
tests/test_estudiantes.py::TestCrearEstudiante::...      PASSED
tests/test_estudiantes.py::TestObtenerEstudiante::...    PASSED
tests/test_estudiantes.py::TestActualizarEstudiante::... PASSED
tests/test_estudiantes.py::TestEliminarEstudiante::...   PASSED
tests/test_auth.py::TestRegistro::...                    PASSED
tests/test_auth.py::TestLogin::...                       PASSED
tests/test_calificaciones.py::TestRegistroCalificaciones::... PASSED
tests/test_tienda.py::TestFlujoCOmpleto::...             PASSED

X passed 
```

---

##  ¿Qué prueba cada archivo?

### Suite 1 — `test_modelos.py` (Pruebas Unitarias de Modelos)

Verifica que los modelos de la base de datos funcionen bien por sí solos, sin necesidad de levantar toda la API.

| Clase | ¿Qué verifica? |
|---|---|
| `TestModeloEstudiante` | Que un estudiante se crea con los datos correctos |
| `TestModeloUsuario` | Que un usuario se guarda bien en la base de datos |
| `TestModeloMateria` | Que una materia tiene todos sus campos en orden |

### Suite 2 — `test_estudiantes.py` (Pruebas de Integración CRUD)

Prueba que los endpoints de estudiantes respondan correctamente a peticiones HTTP reales.

| Clase | Endpoint | ¿Qué verifica? |
|---|---|---|
| `TestCrearEstudiante` | `POST /api/estudiantes/` | Crear, rechazar duplicados, validar campos |
| `TestObtenerEstudiante` | `GET /api/estudiantes/` | Listar, buscar por ID, paginación |
| `TestActualizarEstudiante` | `PUT /api/estudiantes/<id>` | Modificar datos existentes |
| `TestEliminarEstudiante` | `DELETE /api/estudiantes/<id>` | Borrado lógico (marcar como inactivo) |

### Suite 3 — `test_auth.py` (Pruebas de Autenticación JWT)

Verifica que el sistema de registro y login con tokens JWT funcione correctamente.

| Clase | ¿Qué verifica? |
|---|---|
| `TestRegistro` | Registro exitoso, rechazo de usuarios duplicados, validación de campos |
| `TestLogin` | Login exitoso, rechazo de contraseña incorrecta, usuario inexistente |

### Suite 4 — `test_calificaciones.py` (Pruebas de Relaciones y Cálculos)

Verifica que las relaciones entre tablas (estudiante ↔ materia ↔ calificación) funcionen bien, incluyendo cálculos de promedios.

| ¿Qué verifica? |
|---|
| Registrar una calificación para un estudiante en una materia |
| Calcular el promedio de calificaciones correctamente |
| No permitir calificaciones fuera del rango válido |

### Suite 5 — `test_tienda.py` (Prueba de Flujo Completo)

Esta es la prueba más completa: simula el flujo real de una tienda de principio a fin.

| Paso | ¿Qué hace? |
|---|---|
| 1 | Un administrador se registra y crea productos en el catálogo |
| 2 | Un cliente se registra y hace login |
| 3 | El cliente hace un pedido con los productos disponibles |
| 4 | Se verifica que el pedido quedó guardado correctamente |

---

##  Comandos útiles adicionales

```bash
# Correr solo una suite específica
pytest tests/test_modelos.py -v

# Correr solo una clase específica
pytest tests/test_auth.py::TestRegistro -v

# Correr solo una prueba específica
pytest tests/test_estudiantes.py::TestCrearEstudiante::test_crear_estudiante_exitoso -v

# Ver los print() dentro de las pruebas (útil para depurar)
pytest -v -s

# Detener al primer fallo (útil cuando hay muchos errores)
pytest -v -x

# Ver reporte de cobertura en el navegador
pytest --cov=app --cov-report=html
# Luego abre: htmlcov/index.html
```

---

##  Solución a errores comunes

| Error que ves | Qué hacer |
|---|---|
| `ModuleNotFoundError: app` | Asegúrate de correr `pytest` desde la carpeta `Pruebas-unitarias-main/`, no desde dentro de `tests/` |
| `(venv)` no aparece en la terminal | El entorno virtual no está activo. Repite el Paso 3 |
| `pip install` falla | Verifica tener Python 3.8 o superior con `python --version` |
| `FAILED` en alguna prueba | Lee el mensaje de error — generalmente dice exactamente qué falló y en qué línea |
| Error de cobertura `< 80%` | El proyecto exige mínimo 80% de cobertura. Si hay código sin probar, aparece este error |

---

##  Tecnologías usadas

- Python 3.8+
- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1 — para la base de datos
- Flask-JWT-Extended 4.6.0 — para la autenticación con tokens
- Flask-Bcrypt 1.0.1 — para encriptar contraseñas
- pytest 8.2.2 — para correr las pruebas
- pytest-flask 1.3.0 — integración de pytest con Flask
- pytest-cov 5.0.0 — para medir qué tanto del código está cubierto por pruebas
