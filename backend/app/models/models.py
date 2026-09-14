import uuid

from sqlalchemy import Boolean, Column, Date, DECIMAL, Enum, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    telefone = Column(String(30), nullable=True)
    cpf = Column(String(14), nullable=True, unique=True, index=True)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    atendimentos = relationship("Atendimento", back_populates="cliente")
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), unique=True, index=True, nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    status = Column(String(50), nullable=False)
    previsao_entrega = Column(Date, nullable=True)
    codigo_rastreio = Column(String(100), nullable=True)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    cliente = relationship("Cliente", back_populates="pedidos")


class Atendimento(Base):
    __tablename__ = "atendimentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    acesso_cliente_token = Column(UUID(as_uuid=True), unique=True, index=True, nullable=False, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    categoria = Column(Enum("ENTREGA", "FINANCEIRO", "CANCELAMENTO", "SUPORTE", "INFORMACAO", "RECLAMACAO", "OUTROS", name="categoria_enum", create_type=False), nullable=False)
    prioridade = Column(Enum("BAIXA", "MEDIA", "ALTA", "URGENTE", name="prioridade_enum", create_type=False), nullable=False)
    sentimento = Column(Enum("POSITIVO", "NEUTRO", "NEGATIVO", name="sentimento_enum", create_type=False), nullable=False)
    status = Column(Enum("NOVO", "CLASSIFICADO", "RESPONDIDO_IA", "FILA_HUMANA", "EM_ATENDIMENTO", "RESOLVIDO", name="status_enum", create_type=False), nullable=False, default="NOVO")
    precisa_humano = Column(Boolean, nullable=False, default=False)
    confianca_ia = Column(DECIMAL(4, 3), nullable=False)
    resumo_ia = Column(Text, nullable=True)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    cliente = relationship("Cliente", back_populates="atendimentos")
    mensagens = relationship("Mensagem", back_populates="atendimento", cascade="all, delete-orphan")


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    atendimento_id = Column(UUID(as_uuid=True), ForeignKey("atendimentos.id", ondelete="CASCADE"), nullable=False)
    origem = Column(Enum("CLIENTE", "IA", "ATENDENTE", "SISTEMA", name="origem_enum", create_type=False), nullable=False)
    conteudo = Column(Text, nullable=False)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    atendimento = relationship("Atendimento", back_populates="mensagens")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(20), nullable=False, default="ATENDENTE")
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
