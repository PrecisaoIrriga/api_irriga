from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)



# Agricultor model
class AgricultorBase(SQLModel):
    nome: str = Field(max_length=255)
    cpf: str = Field(unique=True, index=True, max_length=14)

class AgricultorCreate(AgricultorBase):
    pass

class Agricultor(AgricultorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    localizacao: str | None = Field(default=None, max_length=255)

class AgricultorPublic(AgricultorBase):
    pass

class AgricultoresPublic(SQLModel):
    data: list[AgricultorPublic]
    count: int

class AgricultorUpdate(SQLModel):
    nome: str | None = Field(default=None, max_length=255)
    cpf: str | None = Field(default=None, max_length=14)
    localizacao: str | None = Field(default=None, max_length=255)

# Setores model

class SetorBase(SQLModel):
    nome: str = Field(max_length=255)
    tamanho: float | None = Field(default=None)
    agricultor_id: uuid.UUID = Field(foreign_key="agricultor.id")

class SetorCreate(SetorBase):
    pass

class Setor(SetorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class SetorPublic(SetorBase):
    pass

class SetoresPublic(SQLModel):
    data: list[SetorPublic]
    count: int

class SetorUpdate(SQLModel):
    nome: str | None = Field(default=None, max_length=255)
    tamanho: float | None = Field(default=None)

# Aparelhos model

class AparelhoBase(SQLModel):
    setor_id: uuid.UUID = Field(foreign_key="setor.id")
    modelo: str | None = Field(default=None, max_length=255)
    agricultor_id: uuid.UUID = Field(foreign_key="agricultor.id")
    status: str | None = Field(default=None, max_length=50)
    ultima_conexao: str | None = Field(default=None, max_length=50)

class AparelhoCreate(AparelhoBase):
    pass

class Aparelho(AparelhoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class AparelhoPublic(AparelhoBase):
    pass

class AparelhosPublic(SQLModel):
    data: list[AparelhoPublic]
    count: int

class AparelhoUpdate(SQLModel):
    modelo: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=50)
    ultima_conexao: str | None = Field(default=None, max_length=50)

# Controladores model

class ControladoresBase(SQLModel):
    aparelho_id: uuid.UUID = Field(foreign_key="aparelho.id", unique=True, index=True)
    total_relays: int | None = Field(default=None)
    info_relays: str | None = Field(default=None, max_length=100)
    assinatura: str = Field(max_length=100)

class ControladorCreate(ControladoresBase):
    pass

class Controlador(ControladoresBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ControladorPublic(ControladoresBase):
    pass

class ControladoresPublic(SQLModel):
    data: list[ControladorPublic]
    count: int

class ControladorUpdate(SQLModel):
    total_relays: int | None = Field(default=None)
    info_relays: str | None = Field(default=None, max_length=100)
    assinatura: str | None = Field(default=None, max_length=100)

# Emissor models

class EmissorBase(AparelhoBase):
    pass


# Comandos model

class ComandoBase(SQLModel):
    controlador_id: uuid.UUID = Field(foreign_key="controlador.id")
    timestamp_criado: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    timestamp_executado: datetime | None = Field(default=None)
    comando: str = Field(max_length=100)
    param: str = Field(max_length=100)
    status: str = Field(default="Pendente", max_length=50)
 
class ComandoCreate(ComandoBase):
    pass

class Comando(ComandoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ComandoPublic(ComandoBase):
    pass

class ComandosPublic(SQLModel):
    data: list[ComandoPublic]
    count: int

class ComandoUpdate(SQLModel):
    timestamp_executado: datetime | None = Field(default=None)
    status: str | None = Field(default=None, max_length=50)



