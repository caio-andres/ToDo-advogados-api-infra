"""
Usuario ORM Model
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    # Primary Key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Fields
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Timestamps
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    data_atualizacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tarefas: Mapped[list["Tarefa"]] = relationship(
        "Tarefa", back_populates="criador", foreign_keys="Tarefa.criado_por"
    )

    def __repr__(self) -> str:
        return f"<​Usuario(id={self.id}, email={self.email})>"
