import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.caso import Caso
from app.models.adulto_mayor import AdultoMayor
from app.models.tipologia import Tipologia
from app.schemas.caso import CasoCreate, CasoUpdate, CasoEstadoUpdate

logger = logging.getLogger(__name__)

ESTADOS_VALIDOS = {"abierto", "en_seguimiento", "cerrado", "derivado"}
PRIORIDADES_VALIDAS = {"alta", "media", "baja"}


async def generar_numero_correlativo(db: AsyncSession) -> str:
    """Genera el próximo número correlativo en formato CASO-YYYY-NNNN."""
    year = datetime.now(timezone.utc).year
    result = await db.execute(
        select(func.count(Caso.id)).where(
            Caso.numero_correlativo.like(f"CASO-{year}-%")
        )
    )
    count = result.scalar_one() + 1
    return f"CASO-{year}-{count:04d}"


async def create_caso(data: CasoCreate, profesional_id: int, db: AsyncSession) -> Caso:
    """Crea un nuevo caso con número correlativo auto-generado."""
    am = await db.get(AdultoMayor, data.adulto_mayor_id)
    if not am:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adulto mayor no encontrado")

    tip = await db.get(Tipologia, data.tipologia_id)
    if not tip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipología no encontrada")

    if data.prioridad not in PRIORIDADES_VALIDAS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Prioridad inválida. Valores: {PRIORIDADES_VALIDAS}")

    numero = await generar_numero_correlativo(db)
    assigned_professional = data.profesional_id if data.profesional_id else profesional_id

    caso = Caso(
        numero_correlativo=numero,
        adulto_mayor_id=data.adulto_mayor_id,
        tipologia_id=data.tipologia_id,
        descripcion=data.descripcion,
        desarrollo=data.desarrollo,
        estado="abierto",
        prioridad=data.prioridad,
        profesional_id=assigned_professional,
    )
    db.add(caso)
    await db.flush()
    await db.refresh(caso)

    result = await db.execute(
        select(Caso)
        .options(
            selectinload(Caso.adulto_mayor),
            selectinload(Caso.tipologia),
            selectinload(Caso.profesional).selectinload(Caso.profesional.property.mapper.class_.rol),
        )
        .where(Caso.id == caso.id)
    )
    return result.scalar_one()


async def update_estado(caso_id: int, data: CasoEstadoUpdate, db: AsyncSession) -> Caso:
    """Actualiza el estado de un caso."""
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado inválido. Valores: {ESTADOS_VALIDOS}")

    caso = await db.get(Caso, caso_id)
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")

    caso.estado = data.estado
    if data.estado == "cerrado":
        caso.fecha_cierre = data.fecha_cierre or datetime.now(timezone.utc)

    await db.flush()
    return caso
