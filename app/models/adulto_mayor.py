from datetime import datetime, date
from sqlalchemy import Integer, String, Text, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AdultoMayor(Base):
    __tablename__ = "adultos_mayores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    edad: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sexo: Mapped[str | None] = mapped_column(String(1), nullable=True)
    numero_ci: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    contactos_referencia: Mapped[list["ContactoReferencia"]] = relationship(
        "ContactoReferencia", back_populates="adulto_mayor", cascade="all, delete-orphan"
    )
    casos: Mapped[list["Caso"]] = relationship("Caso", back_populates="adulto_mayor")
