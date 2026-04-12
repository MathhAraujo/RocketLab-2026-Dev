from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AvaliacaoPedido(Base):
    __tablename__ = "avaliacoes_pedidos"

    id_avaliacao: Mapped[str] = mapped_column(String(32), primary_key=True)
    id_pedido: Mapped[str] = mapped_column(
        String(32), ForeignKey("pedidos.id_pedido"), nullable=False
    )
    avaliacao: Mapped[int] = mapped_column(Integer)
    titulo_comentario: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    comentario: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    data_comentario: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    data_resposta: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resposta_admin: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    autor_resposta: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
