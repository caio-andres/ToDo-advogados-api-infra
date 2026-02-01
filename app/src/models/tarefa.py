from pydantic import BaseModel
from datetime import datetime
from usuario import Usuario
from enum import Enum


class Status(Enum):
    PENDENTE: str = "Pendente"
    EM_ANDAMENTO: str = "Em Andamento"
    CONCLUIDO: str = "Concluída"


class Tarefa(BaseModel):
    id: str
    titulo: str
    descricao: str
    status: Status
    criado_por: Usuario.id
    atualizado_por: Usuario.id
    data_criacao: datetime
    data_atualizacao: datetime
    data_conclusao: datetime
