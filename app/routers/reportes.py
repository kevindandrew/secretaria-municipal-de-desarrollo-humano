from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["Reportes"])
auth = Depends(get_current_user)


@router.get("/estadisticas", dependencies=[auth])
async def estadisticas(db: AsyncSession = Depends(get_db)):
    return await reporte_service.get_estadisticas(db)


@router.get("/casos-por-tipologia", dependencies=[auth])
async def casos_por_tipologia(db: AsyncSession = Depends(get_db)):
    return await reporte_service.get_casos_por_tipologia(db)


@router.get("/casos-por-estado", dependencies=[auth])
async def casos_por_estado(db: AsyncSession = Depends(get_db)):
    return await reporte_service.get_casos_por_estado(db)


@router.get("/casos-por-fecha", dependencies=[auth])
async def casos_por_fecha(
    fecha_inicio: datetime | None = Query(None),
    fecha_fin: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await reporte_service.get_casos_por_fecha(db, fecha_inicio, fecha_fin)
