from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Seguimiento(Base):
    __tablename__ = "seguimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caso_id: Mapped[int] = mapped_column(Integer, ForeignKey("casos.id"), nullable=False)
    profesional_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    observaciones: Mapped[str] = mapped_column(Text, nullable=False)
    acciones_realizadas: Mapped[str | None] = mapped_column(Text, nullable=True)
    derivacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado_resultante: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fecha_seguimiento: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    caso: Mapped["Caso"] = relationship("Caso", back_populates="seguimientos")
    profesional: Mapped["Usuario"] = relationship("Usuario", back_populates="seguimientos")
    adjuntos: Mapped[list["Adjunto"]] = relationship("Adjunto", back_populates="seguimiento", foreign_keys="Adjunto.seguimiento_id")
