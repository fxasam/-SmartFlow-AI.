import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


Categoria = Literal["ENTREGA", "FINANCEIRO", "CANCELAMENTO", "SUPORTE", "INFORMACAO", "RECLAMACAO", "OUTROS"]
Prioridade = Literal["BAIXA", "MEDIA", "ALTA", "URGENTE"]
Sentimento = Literal["POSITIVO", "NEUTRO", "NEGATIVO"]
Status = Literal["NOVO", "CLASSIFICADO", "RESPONDIDO_IA", "FILA_HUMANA", "EM_ATENDIMENTO", "RESOLVIDO"]
Origem = Literal["CLIENTE", "IA", "ATENDENTE", "SISTEMA"]


class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)
    cpf: str | None = Field(default=None, max_length=14)


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: EmailStr | None
    telefone: str | None
    cpf: str | None = None


class PedidoCreate(BaseModel):
    numero: str = Field(..., min_length=4, max_length=50)
    cliente_id: uuid.UUID
    status: str = Field(..., min_length=2, max_length=50)
    previsao_entrega: date | None = None
    codigo_rastreio: str | None = Field(default=None, max_length=100)


class PedidoUpdate(BaseModel):
    numero: str | None = Field(default=None, min_length=4, max_length=50)
    status: str | None = Field(default=None, min_length=2, max_length=50)
    previsao_entrega: date | None = None
    codigo_rastreio: str | None = Field(default=None, max_length=100)


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero: str
    cliente_id: uuid.UUID
    status: str
    previsao_entrega: date | None
    codigo_rastreio: str | None
    criado_em: datetime


class AtendimentoCreate(BaseModel):
    cliente: ClienteCreate
    mensagem: str = Field(..., min_length=1, max_length=4000)


class AtendimentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cliente_id: uuid.UUID
    categoria: Categoria
    prioridade: Prioridade
    sentimento: Sentimento
    status: Status
    precisa_humano: bool
    confianca_ia: float
    resumo_ia: str | None
    criado_em: datetime
    atualizado_em: datetime


class AtendimentoCreateResponse(AtendimentoResponse):
    acesso_cliente_token: uuid.UUID


class MensagemCreate(BaseModel):
    origem: Origem
    conteudo: str = Field(..., min_length=1, max_length=4000)


class MensagemClienteCreate(BaseModel):
    conteudo: str = Field(..., min_length=1, max_length=4000)


class MensagemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    atendimento_id: uuid.UUID
    origem: Origem
    conteudo: str
    criado_em: datetime


class AtendimentoDetalheResponse(AtendimentoResponse):
    acesso_cliente_token: uuid.UUID
    cliente: ClienteResponse
    mensagens: list[MensagemResponse]


class AtendimentoClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mensagens: list[MensagemResponse]


class AtendimentoStatusUpdate(BaseModel):
    status: Status


class MetricasResumo(BaseModel):
    atendimentos_hoje: int
    resolvidos_ia: int
    aguardando_humano: int
    urgentes: int


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=100)
    perfil: Literal["ADMIN", "ATENDENTE"] = "ATENDENTE"


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: EmailStr
    perfil: Literal["ADMIN", "ATENDENTE"]
    ativo: bool
    criado_em: datetime
