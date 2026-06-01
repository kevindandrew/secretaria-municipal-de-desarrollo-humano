from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class RolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class UserBase(BaseModel):
    nombre: str
    apellido: str
    username: str
    email: str | None = None
    rol_id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: str | None = None
    rol_id: int | None = None
    password: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    username: str
    email: str | None
    rol_id: int
    rol: RolResponse
    activo: bool
    created_at: datetime
    updated_at: datetime | None
