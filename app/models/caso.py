from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Caso(Base):
    __tablename__ = "casos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_correlativo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    adulto_mayor_id: Mapped[int] = mapped_column(Integer, ForeignKey("adultos_mayores.id"), nullable=False)
    tipologia_id: Mapped[int] = mapped_column(Integer, ForeignKey("tipologias.id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    desarrollo: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="abierto")
    prioridad: Mapped[str] = mapped_column(String(10), nullable=False, default="media")
    profesional_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_apertura: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    adulto_mayor: Mapped["AdultoMayor"] = relationship("AdultoMayor", back_populates="casos")
    tipologia: Mapped["Tipologia"] = relationship("Tipologia", back_populates="casos")
    profesional: Mapped["Usuario"] = relationship("Usuario", back_populates="casos_asignados", foreign_keys=[profesional_id])
    seguimientos: Mapped[list["Seguimiento"]] = relationship("Seguimiento", back_populates="caso", cascade="all, delete-orphan")
    adjuntos: Mapped[list["Adjunto"]] = relationship("Adjunto", back_populates="caso", foreign_keys="Adjunto.caso_id")
