"""
Usuario Schemas - Pydantic models for validation and serialization
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import re


class UsuarioBase(BaseModel):
    """Base Usuario schema"""

    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    """Schema for creating a new usuario"""

    senha: str = Field(..., min_length=8, max_length=100)

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, v: str) -> str:
        """Validate password strength"""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v


class UsuarioLogin(BaseModel):
    """Schema for usuario login"""

    email: EmailStr
    senha: str = Field(..., min_length=8)


class UsuarioResponse(UsuarioBase):
    """Schema for usuario response"""

    id: str
    data_criacao: datetime
    data_atualizacao: datetime

    model_config = ConfigDict(
        from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()}
    )
