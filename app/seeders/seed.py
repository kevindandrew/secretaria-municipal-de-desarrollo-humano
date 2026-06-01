import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.role import Rol
from app.models.user import Usuario
from app.models.tipologia import Tipologia
from app.models.adulto_mayor import AdultoMayor
from app.models.caso import Caso
from app.models.seguimiento import Seguimiento

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_roles(db: AsyncSession) -> dict[str, Rol]:
    roles_data = [
        {"nombre": "administrador", "descripcion": "Acceso total al sistema"},
        {"nombre": "tecnico", "descripcion": "Gestión de casos y seguimientos"},
        {"nombre": "consulta", "descripcion": "Solo lectura"},
    ]
    roles = {}
    for rd in roles_data:
        existing = await db.scalar(select(Rol).where(Rol.nombre == rd["nombre"]))
        if not existing:
            r = Rol(**rd)
            db.add(r)
            await db.flush()
            roles[rd["nombre"]] = r
            logger.info("Rol creado: %s", rd["nombre"])
        else:
            roles[rd["nombre"]] = existing
    return roles


async def seed_admin(db: AsyncSession, rol_admin: Rol):
    existing = await db.scalar(select(Usuario).where(Usuario.username == "admin"))
    if not existing:
        admin = Usuario(
            nombre="Admin",
            apellido="Sistema",
            username="admin",
            password_hash=hash_password("Admin1234!"),
            rol_id=rol_admin.id,
            activo=True,
        )
        db.add(admin)
        await db.flush()
        logger.info("Usuario admin creado")
    else:
        logger.info("Admin ya existe, omitiendo")


async def seed_tipologias(db: AsyncSession) -> list[Tipologia]:
    nombres = [
        "Abandono",
        "Extravío",
        "Institucionalización a hogares transitorios o permanentes",
        "Abordaje psicosocial",
        "Maltrato psicológico dentro del vínculo familiar",
        "Atención y consulta de derechos",
        "Situación de riesgo",
    ]
    tipologias = []
    for nombre in nombres:
        existing = await db.scalar(select(Tipologia).where(Tipologia.nombre == nombre))
        if not existing:
            t = Tipologia(nombre=nombre)
            db.add(t)
            await db.flush()
            tipologias.append(t)
            logger.info("Tipología creada: %s", nombre)
        else:
            tipologias.append(existing)
    return tipologias


async def seed_adultos_mayores(db: AsyncSession) -> list[AdultoMayor]:
    data = [
        {"nombres": "Juan Carlos", "apellidos": "Pérez Rodríguez", "numero_ci": "1234567",
         "edad": 75, "sexo": "M", "telefono": "0991234567", "direccion": "Av. Principal 123"},
        {"nombres": "María Elena", "apellidos": "González López", "numero_ci": "2345678",
         "edad": 82, "sexo": "F", "telefono": "0987654321", "direccion": "Calle 5 de Mayo 456"},
        {"nombres": "Roberto", "apellidos": "Martínez Soria", "numero_ci": "3456789",
         "edad": 78, "sexo": "M", "telefono": "0976543210", "direccion": "Barrio San Miguel, casa 12"},
    ]
    adultos = []
    for d in data:
        existing = await db.scalar(select(AdultoMayor).where(AdultoMayor.numero_ci == d["numero_ci"]))
        if not existing:
            am = AdultoMayor(**d)
            db.add(am)
            await db.flush()
            adultos.append(am)
            logger.info("Adulto mayor creado: %s %s", d["nombres"], d["apellidos"])
        else:
            adultos.append(existing)
    return adultos


async def seed_casos(
    db: AsyncSession,
    adultos: list[AdultoMayor],
    tipologias: list[Tipologia],
    admin: Usuario,
):
    casos_data = [
        {
            "numero_correlativo": "CASO-2025-0001",
            "adulto_mayor_id": adultos[0].id,
            "tipologia_id": tipologias[0].id,
            "descripcion": "Caso de abandono familiar detectado por vecinos",
            "estado": "abierto",
            "prioridad": "alta",
            "profesional_id": admin.id,
        },
        {
            "numero_correlativo": "CASO-2025-0002",
            "adulto_mayor_id": adultos[1].id,
            "tipologia_id": tipologias[3].id,
            "descripcion": "Seguimiento de abordaje psicosocial post-crisis",
            "estado": "en_seguimiento",
            "prioridad": "media",
            "profesional_id": admin.id,
        },
        {
            "numero_correlativo": "CASO-2025-0003",
            "adulto_mayor_id": adultos[2].id,
            "tipologia_id": tipologias[5].id,
            "descripcion": "Consulta de derechos sobre pensión alimentaria",
            "estado": "cerrado",
            "prioridad": "baja",
            "profesional_id": admin.id,
        },
    ]
    casos = []
    for cd in casos_data:
        existing = await db.scalar(select(Caso).where(Caso.numero_correlativo == cd["numero_correlativo"]))
        if not existing:
            c = Caso(**cd)
            db.add(c)
            await db.flush()
            casos.append(c)
            logger.info("Caso creado: %s", cd["numero_correlativo"])
        else:
            casos.append(existing)
    return casos


async def seed_seguimientos(db: AsyncSession, casos: list[Caso], admin: Usuario):
    sigs_data = [
        {
            "caso_id": casos[0].id,
            "profesional_id": admin.id,
            "observaciones": "Primera visita domiciliaria realizada. Se constató situación de abandono.",
            "acciones_realizadas": "Contacto con familiares, coordinación con trabajo social.",
            "estado_resultante": "en_seguimiento",
        },
        {
            "caso_id": casos[0].id,
            "profesional_id": admin.id,
            "observaciones": "Segunda visita. Familiar hijo mayor acepta hacerse cargo.",
            "acciones_realizadas": "Firma de compromiso familiar y plan de cuidados.",
            "estado_resultante": "en_seguimiento",
        },
    ]
    for sd in sigs_data:
        existing = await db.scalar(
            select(Seguimiento).where(
                Seguimiento.caso_id == sd["caso_id"],
                Seguimiento.observaciones == sd["observaciones"],
            )
        )
        if not existing:
            s = Seguimiento(**sd)
            db.add(s)
            await db.flush()
            logger.info("Seguimiento creado para caso_id %s", sd["caso_id"])


async def run_seed():
    async with AsyncSessionLocal() as db:
        try:
            roles = await seed_roles(db)
            await seed_admin(db, roles["administrador"])
            await seed_tipologias(db)

            admin = await db.scalar(select(Usuario).where(Usuario.username == "admin"))
            tipologias = (await db.execute(select(Tipologia))).scalars().all()
            adultos = await seed_adultos_mayores(db)
            casos = await seed_casos(db, adultos, tipologias, admin)
            await seed_seguimientos(db, casos, admin)

            await db.commit()
            logger.info("Seed completado exitosamente")
        except Exception as e:
            await db.rollback()
            logger.error("Error en seed: %s", e)
            raise


def main():
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
