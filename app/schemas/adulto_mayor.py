from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class ContactoReferenciaBase(BaseModel):
    nombres: str
    apellidos: str
    parentesco: str | None = None
    telefono: str | None = None
    direccion: str | None = None


class ContactoReferenciaCreate(ContactoReferenciaBase):
    adulto_mayor_id: int


class ContactoReferenciaResponse(ContactoReferenciaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    adulto_mayor_id: int


class AdultoMayorBase(BaseModel):
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None = None
    edad: int | None = None
    sexo: str | None = None
    numero_ci: str
    direccion: str | None = None
    telefono: str | None = None


class AdultoMayorCreate(AdultoMayorBase):
    contactos_referencia: list[ContactoReferenciaBase] = []


class AdultoMayorUpdate(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: date | None = None
    edad: int | None = None
    sexo: str | None = None
    numero_ci: str | None = None
    direccion: str | None = None
    telefono: str | None = None


class AdultoMayorResponse(AdultoMayorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None


class AdultoMayorDetailResponse(AdultoMayorResponse):
    contactos_referencia: list[ContactoReferenciaResponse] = []
