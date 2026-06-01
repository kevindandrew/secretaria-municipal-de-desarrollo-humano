import logging
import math
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.caso import Caso
from app.models.user import Usuario
from app.schemas.caso import CasoCreate, CasoUpdate, CasoEstadoUpdate, CasoResponse, CasoListResponse
from app.schemas.seguimiento import SeguimientoResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services import caso_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/casos", tags=["Casos"])
auth = Depends(get_current_user)

CASO_LOAD = [
    selectinload(Caso.adulto_mayor),
    selectinload(Caso.tipologia),
    selectinload(Caso.profesional).selectinload(Usuario.rol),
]

CASO_FULL_LOAD = CASO_LOAD + [
    selectinload(Caso.seguimientos).selectinload(
        Caso.seguimientos.property.mapper.class_.profesional
    ).selectinload(Usuario.rol),
]


@router.get("/", response_model=PaginatedResponse[CasoListResponse], dependencies=[auth])
async def list_casos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    estado: str | None = Query(None),
    prioridad: str | None = Query(None),
    tipologia_id: int | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Caso)
    count_q = select(func.count(Caso.id))

    filters = []
    if estado:
        filters.append(Caso.estado == estado)
    if prioridad:
        filters.append(Caso.prioridad == prioridad)
    if tipologia_id:
        filters.append(Caso.tipologia_id == tipologia_id)
    if fecha_desde:
        filters.append(Caso.fecha_apertura >= fecha_desde)
    if fecha_hasta:
        filters.append(Caso.fecha_apertura <= fecha_hasta)

    if filters:
        query = query.where(*filters)
        count_q = count_q.where(*filters)

    total = await db.scalar(count_q)
    offset = (page - 1) * page_size
    result = await db.execute(
        query.options(selectinload(Caso.adulto_mayor), selectinload(Caso.tipologia))
        .offset(offset).limit(page_size)
        .order_by(Caso.fecha_apertura.desc())
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/", response_model=CasoResponse, status_code=status.HTTP_201_CREATED, dependencies=[auth])
async def create_caso(
    data: CasoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return await caso_service.create_caso(data, current_user.id, db)


@router.get("/{caso_id}", response_model=CasoResponse, dependencies=[auth])
async def get_caso(caso_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Caso).options(*CASO_FULL_LOAD).where(Caso.id == caso_id)
    )
    caso = result.scalar_one_or_none()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return caso


@router.put("/{caso_id}", response_model=CasoResponse, dependencies=[auth])
async def update_caso(caso_id: int, data: CasoUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Caso).where(Caso.id == caso_id))
    caso = result.scalar_one_or_none()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(caso, field, value)

    await db.flush()
    result = await db.execute(
        select(Caso).options(*CASO_FULL_LOAD).where(Caso.id == caso_id)
    )
    return result.scalar_one()


@router.patch("/{caso_id}/estado", response_model=MessageResponse, dependencies=[auth])
async def cambiar_estado(caso_id: int, data: CasoEstadoUpdate, db: AsyncSession = Depends(get_db)):
    await caso_service.update_estado(caso_id, data, db)
    return MessageResponse(message=f"Estado actualizado a '{data.estado}'")
