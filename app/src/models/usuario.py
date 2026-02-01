from pydantic import BaseModel
from datetime import datetime


class Usuario(BaseModel):
    id: str
    nome: str
    senha: str
    criado_em: datetime
