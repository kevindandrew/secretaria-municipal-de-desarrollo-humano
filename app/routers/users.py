import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import Usuario
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse, MessageResponse
import math

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Usuarios"])

solo_admin = Depends(require_role(["administrador"]))


@router.get("/", response_model=PaginatedResponse[UserResponse], dependencies=[solo_admin])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    total = await db.scalar(select(func.count(Usuario.id)))
    result = await db.execute(
        select(Usuario)
        .options(selectinload(Usuario.rol))
        .offset(offset)
        .limit(page_size)
        .order_by(Usuario.id)
    )
    users = result.scalars().all()
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[solo_admin])
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(Usuario).where(Usuario.username == data.username))
    if existing:
        raise HTTPException(status_code=400, detail="Username ya existe")

    user = Usuario(
        nombre=data.nombre,
        apellido=data.apellido,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        rol_id=data.rol_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == user.id)
    )
    return result.scalar_one()


@router.get("/{user_id}", response_model=UserResponse, dependencies=[solo_admin])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserResponse, dependencies=[solo_admin])
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        if field == "password":
            user.password_hash = hash_password(value)
        else:
            setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.id == user_id)
    )
    return result.scalar_one()


@router.patch("/{user_id}/toggle-active", response_model=MessageResponse, dependencies=[solo_admin])
async def toggle_active(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.activo = not user.activo
    await db.flush()
    estado = "activado" if user.activo else "desactivado"
    return MessageResponse(message=f"Usuario {estado} exitosamente")
