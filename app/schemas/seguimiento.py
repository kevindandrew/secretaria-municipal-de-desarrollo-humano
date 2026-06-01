from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class SeguimientoBase(BaseModel):
    caso_id: int
    observaciones: str
    acciones_realizadas: str | None = None
    derivacion: str | None = None
    estado_resultante: str | None = None


class SeguimientoCreate(SeguimientoBase):
    profesional_id: int | None = None


class SeguimientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    caso_id: int
    profesional_id: int
    observaciones: str
    acciones_realizadas: str | None
    derivacion: str | None
    estado_resultante: str | None
    fecha_seguimiento: datetime
    created_at: datetime
    profesional: UserResponse
