# Plataforma de Atención Inmediata del Adulto Mayor — Backend

API REST construida con FastAPI + PostgreSQL para la gestión de casos de atención al adulto mayor.

## Requisitos previos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL con la base de datos `adulto_mayor_db` ya creada

## Instalación

```bash
# Instalar dependencias
uv sync

# Copiar y configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

## Base de datos

```bash
# Crear la base de datos (si no existe)
psql -U postgres -c "CREATE DATABASE adulto_mayor_db;"

# Generar la primera migración
uv run alembic revision --autogenerate -m "initial_schema"

# Aplicar migraciones
uv run alembic upgrade head

# Ejecutar seeders (roles, admin, tipologías y datos de prueba)
uv run python -m app.seeders.seed
```

## Ejecutar el servidor

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentación interactiva

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Credenciales del admin por defecto

- **Username:** admin
- **Password:** Admin1234!

## Estructura de rutas

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/v1/auth/login | Login y obtención de token JWT |
| GET | /api/v1/users | Listar usuarios (admin) |
| POST | /api/v1/users | Crear usuario (admin) |
| GET | /api/v1/adultos-mayores | Listar adultos mayores |
| POST | /api/v1/adultos-mayores | Registrar adulto mayor |
| GET | /api/v1/casos | Listar casos con filtros |
| POST | /api/v1/casos | Crear caso |
| POST | /api/v1/seguimientos | Registrar seguimiento |
| GET | /api/v1/reportes/estadisticas | Dashboard con conteos |

## Roles del sistema

- **administrador**: acceso total, gestión de usuarios
- **tecnico**: gestión de casos y seguimientos
- **consulta**: solo lectura

## Estados de un caso

`abierto` → `en_seguimiento` → `cerrado` / `derivado`
