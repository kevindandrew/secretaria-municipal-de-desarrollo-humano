from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Adjunto(Base):
    __tablename__ = "adjuntos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caso_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("casos.id"), nullable=True)
    seguimiento_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("seguimientos.id"), nullable=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_archivo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ruta_almacenamiento: Mapped[str] = mapped_column(Text, nullable=False)
    tamanio_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subido_por: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    caso: Mapped["Caso | None"] = relationship("Caso", back_populates="adjuntos", foreign_keys=[caso_id])
    seguimiento: Mapped["Seguimiento | None"] = relationship("Seguimiento", back_populates="adjuntos", foreign_keys=[seguimiento_id])
    subido_por_usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="adjuntos")
