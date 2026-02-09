"""
Tarefa Schemas - Pydantic models for validation and serialization
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from models.tarefa import StatusTarefa


class TarefaBase(BaseModel):
    """Base Tarefa schema"""

    titulo: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)


class TarefaCreate(TarefaBase):
    """Schema for creating a new tarefa"""

    pass


class TarefaUpdate(BaseModel):
    """Schema for updating a tarefa"""

    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    status: Optional[StatusTarefa] = None
    data_conclusao: Optional[datetime] = None


class TarefaResponse(TarefaBase):
    """Schema for tarefa response"""

    id: str
    status: StatusTarefa
    criado_por: str
    atualizado_por: str
    data_criacao: datetime
    data_atualizacao: datetime
    data_conclusao: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None},
    )
