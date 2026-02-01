from pydantic import BaseModel
from datetime import datetime
from usuario import Usuario


class Status(enumerate):
    pendente: str = "Pendente"
    em_andamento: str = "Em Andamento"
    concluido: str = "Concluída"


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
