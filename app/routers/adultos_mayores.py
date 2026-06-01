import logging
import math
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.adulto_mayor import AdultoMayor
from app.models.contacto_referencia import ContactoReferencia
from app.models.caso import Caso
from app.schemas.adulto_mayor import (
    AdultoMayorCreate, AdultoMayorUpdate,
    AdultoMayorResponse, AdultoMayorDetailResponse,
)
from app.schemas.caso import CasoListResponse
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/adultos-mayores", tags=["Adultos Mayores"])
auth = Depends(get_current_user)


@router.get("/", response_model=PaginatedResponse[AdultoMayorResponse], dependencies=[auth])
async def list_adultos_mayores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    buscar: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(AdultoMayor)
    count_query = select(func.count(AdultoMayor.id))

    if buscar:
        filtro = or_(
            AdultoMayor.nombres.ilike(f"%{buscar}%"),
            AdultoMayor.apellidos.ilike(f"%{buscar}%"),
            AdultoMayor.numero_ci.ilike(f"%{buscar}%"),
            AdultoMayor.telefono.ilike(f"%{buscar}%"),
        )
        query = query.where(filtro)
        count_query = count_query.where(filtro)

    total = await db.scalar(count_query)
    offset = (page - 1) * page_size
    result = await db.execute(
        query.offset(offset).limit(page_size).order_by(AdultoMayor.apellidos)
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/", response_model=AdultoMayorDetailResponse, status_code=status.HTTP_201_CREATED, dependencies=[auth])
async def create_adulto_mayor(data: AdultoMayorCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(AdultoMayor).where(AdultoMayor.numero_ci == data.numero_ci))
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un adulto mayor con ese CI")

    am = AdultoMayor(**data.model_dump(exclude={"contactos_referencia"}))
    db.add(am)
    await db.flush()

    for c in data.contactos_referencia:
        contacto = ContactoReferencia(adulto_mayor_id=am.id, **c.model_dump())
        db.add(contacto)

    await db.flush()
    result = await db.execute(
        select(AdultoMayor)
        .options(selectinload(AdultoMayor.contactos_referencia))
        .where(AdultoMayor.id == am.id)
    )
    return result.scalar_one()


@router.get("/{am_id}", response_model=AdultoMayorDetailResponse, dependencies=[auth])
async def get_adulto_mayor(am_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AdultoMayor)
        .options(selectinload(AdultoMayor.contactos_referencia))
        .where(AdultoMayor.id == am_id)
    )
    am = result.scalar_one_or_none()
    if not am:
        raise HTTPException(status_code=404, detail="Adulto mayor no encontrado")
    return am


@router.put("/{am_id}", response_model=AdultoMayorDetailResponse, dependencies=[auth])
async def update_adulto_mayor(am_id: int, data: AdultoMayorUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AdultoMayor)
        .options(selectinload(AdultoMayor.contactos_referencia))
        .where(AdultoMayor.id == am_id)
    )
    am = result.scalar_one_or_none()
    if not am:
        raise HTTPException(status_code=404, detail="Adulto mayor no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(am, field, value)

    await db.flush()
    await db.refresh(am)
    result = await db.execute(
        select(AdultoMayor)
        .options(selectinload(AdultoMayor.contactos_referencia))
        .where(AdultoMayor.id == am_id)
    )
    return result.scalar_one()


@router.get("/{am_id}/historial", response_model=list[CasoListResponse], dependencies=[auth])
async def historial_casos(am_id: int, db: AsyncSession = Depends(get_db)):
    am = await db.get(AdultoMayor, am_id)
    if not am:
        raise HTTPException(status_code=404, detail="Adulto mayor no encontrado")

    result = await db.execute(
        select(Caso)
        .options(
            selectinload(Caso.tipologia),
            selectinload(Caso.adulto_mayor),
        )
        .where(Caso.adulto_mayor_id == am_id)
        .order_by(Caso.fecha_apertura.desc())
    )
    return result.scalars().all()
