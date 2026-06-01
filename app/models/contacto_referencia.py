from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ContactoReferencia(Base):
    __tablename__ = "contactos_referencia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    adulto_mayor_id: Mapped[int] = mapped_column(Integer, ForeignKey("adultos_mayores.id", ondelete="CASCADE"), nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    parentesco: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)

    adulto_mayor: Mapped["AdultoMayor"] = relationship("AdultoMayor", back_populates="contactos_referencia")
