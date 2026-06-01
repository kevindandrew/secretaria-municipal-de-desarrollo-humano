import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.caso import Caso
from app.models.adulto_mayor import AdultoMayor
from app.models.tipologia import Tipologia
from app.models.user import Usuario

logger = logging.getLogger(__name__)


async def get_estadisticas(db: AsyncSession) -> dict:
    """Retorna conteos generales para el dashboard."""
    total_casos = await db.scalar(select(func.count(Caso.id)))
    total_adultos = await db.scalar(select(func.count(AdultoMayor.id)))
    total_usuarios = await db.scalar(select(func.count(Usuario.id)).where(Usuario.activo == True))

    casos_abiertos = await db.scalar(select(func.count(Caso.id)).where(Caso.estado == "abierto"))
    casos_seguimiento = await db.scalar(select(func.count(Caso.id)).where(Caso.estado == "en_seguimiento"))
    casos_cerrados = await db.scalar(select(func.count(Caso.id)).where(Caso.estado == "cerrado"))
    casos_derivados = await db.scalar(select(func.count(Caso.id)).where(Caso.estado == "derivado"))

    return {
        "total_casos": total_casos,
        "total_adultos_mayores": total_adultos,
        "total_usuarios_activos": total_usuarios,
        "casos_por_estado": {
            "abierto": casos_abiertos,
            "en_seguimiento": casos_seguimiento,
            "cerrado": casos_cerrados,
            "derivado": casos_derivados,
        },
    }


async def get_casos_por_tipologia(db: AsyncSession) -> list[dict]:
    """Agrupa casos por tipología."""
    result = await db.execute(
        select(Tipologia.nombre, func.count(Caso.id).label("total"))
        .join(Caso, Caso.tipologia_id == Tipologia.id, isouter=True)
        .group_by(Tipologia.id, Tipologia.nombre)
        .order_by(func.count(Caso.id).desc())
    )
    return [{"tipologia": row.nombre, "total": row.total} for row in result.all()]


async def get_casos_por_estado(db: AsyncSession) -> list[dict]:
    """Agrupa casos por estado."""
    result = await db.execute(
        select(Caso.estado, func.count(Caso.id).label("total"))
        .group_by(Caso.estado)
    )
    return [{"estado": row.estado, "total": row.total} for row in result.all()]


async def get_casos_por_fecha(
    db: AsyncSession,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
) -> list[dict]:
    """Lista casos filtrados por rango de fechas."""
    query = select(
        func.date(Caso.fecha_apertura).label("fecha"),
        func.count(Caso.id).label("total"),
    ).group_by(func.date(Caso.fecha_apertura)).order_by(func.date(Caso.fecha_apertura))

    if fecha_inicio:
        query = query.where(Caso.fecha_apertura >= fecha_inicio)
    if fecha_fin:
        query = query.where(Caso.fecha_apertura <= fecha_fin)

    result = await db.execute(query)
    return [{"fecha": str(row.fecha), "total": row.total} for row in result.all()]
