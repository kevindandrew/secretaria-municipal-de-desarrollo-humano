import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.user import Usuario
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """Autentica un usuario y retorna un token JWT."""
    result = await db.execute(
        select(Usuario)
        .options(selectinload(Usuario.rol))
        .where(Usuario.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    token = create_access_token({"sub": user.username, "rol": user.rol.nombre})
    logger.info("Login exitoso para usuario %s", user.username)

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        rol=user.rol.nombre,
    )
