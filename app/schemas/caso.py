from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.adulto_mayor import AdultoMayorResponse
from app.schemas.user import UserResponse


class TipologiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None = None
    activo: bool


class CasoBase(BaseModel):
    adulto_mayor_id: int
    tipologia_id: int
    descripcion: str
    desarrollo: str | None = None
    prioridad: str = "media"


class CasoCreate(CasoBase):
    profesional_id: int | None = None


class CasoUpdate(BaseModel):
    tipologia_id: int | None = None
    descripcion: str | None = None
    desarrollo: str | None = None
    prioridad: str | None = None
    profesional_id: int | None = None
    fecha_cierre: datetime | None = None


class CasoEstadoUpdate(BaseModel):
    estado: str
    fecha_cierre: datetime | None = None


class CasoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_correlativo: str
    adulto_mayor_id: int
    tipologia_id: int
    descripcion: str
    desarrollo: str | None
    estado: str
    prioridad: str
    profesional_id: int
    fecha_apertura: datetime
    fecha_cierre: datetime | None
    created_at: datetime
    updated_at: datetime | None
    tipologia: TipologiaResponse
    adulto_mayor: AdultoMayorResponse
    profesional: UserResponse


class CasoListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_correlativo: str
    adulto_mayor_id: int
    tipologia_id: int
    descripcion: str
    estado: str
    prioridad: str
    profesional_id: int
    fecha_apertura: datetime
    fecha_cierre: datetime | None
    tipologia: TipologiaResponse
    adulto_mayor: AdultoMayorResponse
