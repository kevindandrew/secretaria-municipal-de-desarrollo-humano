import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.seguimiento import Seguimiento
from app.models.caso import Caso
from app.models.user import Usuario
from app.schemas.seguimiento import SeguimientoCreate, SeguimientoResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seguimientos", tags=["Seguimientos"])
auth = Depends(get_current_user)

SEG_LOAD = [
    selectinload(Seguimiento.profesional).selectinload(Usuario.rol),
]


@router.post("/", response_model=SeguimientoResponse, status_code=status.HTTP_201_CREATED, dependencies=[auth])
async def create_seguimiento(
    data: SeguimientoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    caso = await db.get(Caso, data.caso_id)
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    profesional_id = data.profesional_id or current_user.id
    seg = Seguimiento(
        caso_id=data.caso_id,
        profesional_id=profesional_id,
        observaciones=data.observaciones,
        acciones_realizadas=data.acciones_realizadas,
        derivacion=data.derivacion,
        estado_resultante=data.estado_resultante,
    )
    db.add(seg)
    await db.flush()

    if data.estado_resultante:
        caso.estado = data.estado_resultante
        await db.flush()

    result = await db.execute(
        select(Seguimiento).options(*SEG_LOAD).where(Seguimiento.id == seg.id)
    )
    return result.scalar_one()


@router.get("/caso/{caso_id}", response_model=list[SeguimientoResponse], dependencies=[auth])
async def list_seguimientos(caso_id: int, db: AsyncSession = Depends(get_db)):
    caso = await db.get(Caso, caso_id)
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    result = await db.execute(
        select(Seguimiento)
        .options(*SEG_LOAD)
        .where(Seguimiento.caso_id == caso_id)
        .order_by(Seguimiento.fecha_seguimiento.desc())
    )
    return result.scalars().all()
