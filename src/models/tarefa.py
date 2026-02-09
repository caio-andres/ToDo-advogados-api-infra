"""
Tarefa ORM Model
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class StatusTarefa(str, PyEnum):
    """Status enum for Tarefa"""

    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class Tarefa(Base):
    """Tarefa model"""

    __tablename__ = "tarefa"

    # Primary Key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Fields
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[StatusTarefa] = mapped_column(
        Enum(StatusTarefa), nullable=False, default=StatusTarefa.PENDENTE
    )

    # Foreign Keys
    criado_por: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    atualizado_por: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    data_conclusao: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    criador: Mapped["Usuario"] = relationship(
        "Usuario", back_populates="tarefas", foreign_keys=[criado_por]
    )

    def __repr__(self) -> str:
        return f"<​Tarefa(id={self.id}, titulo={self.titulo}, status={self.status})>"
