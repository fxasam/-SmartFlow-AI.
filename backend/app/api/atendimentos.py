import re
import secrets
import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.security import exigir_administrador, exigir_administrador_ou_n8n
from app.database import get_db
from app.models.models import Atendimento, Cliente, Mensagem, Pedido, Usuario
from app.schemas.schemas import AtendimentoClienteResponse, AtendimentoCreate, AtendimentoCreateResponse, AtendimentoDetalheResponse, AtendimentoResponse, AtendimentoStatusUpdate, MensagemClienteCreate, MensagemCreate, MensagemResponse, MetricasResumo
from app.services.ia_service import classificar_mensagem, gerar_resposta_automatica, gerar_resposta_com_historico


router = APIRouter()


def somente_numeros(valor: str | None) -> str:
    if not valor:
        return ""
    return re.sub(r"\D", "", valor)


def localizar_pedido_no_historico(historico: list[Mensagem], db: Session):
    for mensagem in reversed(historico):
        if mensagem.origem != "CLIENTE":
            continue

        numeros = re.findall(r"\b\d{4,20}\b", mensagem.conteudo)

        for numero in numeros:
            pedido = db.query(Pedido).filter(Pedido.numero == numero).first()
            if pedido:
                return pedido

    return None


def validar_identidade_cliente(conteudo: str, cliente: Cliente) -> bool:
    texto = conteudo.strip().lower()

    if cliente.email and cliente.email.strip().lower() in texto:
        return True

    cpf_cliente = somente_numeros(cliente.cpf)
    cpf_informado = somente_numeros(conteudo)

    return bool(cpf_cliente and cpf_informado and cpf_cliente == cpf_informado)


def parece_identificacao(conteudo: str) -> bool:
    texto = conteudo.strip()

    if "@" in texto:
        return True

    return len(somente_numeros(texto)) == 11


def pedido_foi_validado_no_atendimento(historico: list[Mensagem], cliente: Cliente) -> bool:
    for mensagem in historico:
        if mensagem.origem != "CLIENTE":
            continue

        if validar_identidade_cliente(mensagem.conteudo, cliente):
            return True

    return False


def montar_resposta_pedido(pedido: Pedido) -> str:
    status_formatado = pedido.status.replace("_", " ").lower()

    partes = [f"Encontrei o pedido {pedido.numero}. Ele esta com status: {status_formatado}."]

    if pedido.previsao_entrega:
        previsao = pedido.previsao_entrega.strftime("%d/%m/%Y")
        partes.append(f"A previsao de entrega e {previsao}.")

    if pedido.codigo_rastreio:
        partes.append(f"Codigo de rastreio: {pedido.codigo_rastreio}.")

    return " ".join(partes)


def buscar_atendimento(atendimento_id: str, db: Session) -> Atendimento:
    atendimento = db.query(Atendimento).filter(Atendimento.id == atendimento_id).first()

    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado.")

    return atendimento


def buscar_atendimento_cliente(atendimento_id: str, token: uuid.UUID, db: Session) -> Atendimento:
    atendimento = buscar_atendimento(atendimento_id, db)
    token_atendimento = str(atendimento.acesso_cliente_token)

    if not secrets.compare_digest(token_atendimento, str(token)):
        raise HTTPException(status_code=404, detail="Conversa nao encontrada.")

    return atendimento


def salvar_mensagem(atendimento: Atendimento, origem: str, conteudo: str, db: Session) -> Mensagem:
    mensagem = Mensagem(atendimento_id=atendimento.id, origem=origem, conteudo=conteudo)

    db.add(mensagem)
    db.flush()

    atendimento.atualizado_em = datetime.now(timezone.utc)

    if origem == "ATENDENTE" and atendimento.status == "FILA_HUMANA":
        atendimento.status = "EM_ATENDIMENTO"

    if origem == "CLIENTE" and not atendimento.precisa_humano and atendimento.status not in ["FILA_HUMANA", "EM_ATENDIMENTO", "RESOLVIDO"]:
        historico = db.query(Mensagem).filter(Mensagem.atendimento_id == atendimento.id).order_by(Mensagem.criado_em.asc()).all()
        pedido = localizar_pedido_no_historico(historico, db)
        resposta_ia = None

        if pedido:
            cliente_pedido = db.query(Cliente).filter(Cliente.id == pedido.cliente_id).first()

            if cliente_pedido and pedido_foi_validado_no_atendimento(historico, cliente_pedido):
                resposta_ia = montar_resposta_pedido(pedido)
            elif parece_identificacao(conteudo):
                resposta_ia = f"Os dados informados nao correspondem ao cadastro do pedido {pedido.numero}. Confira o CPF ou e-mail e tente novamente."

        if not resposta_ia:
            resposta_ia = gerar_resposta_com_historico(historico)

        mensagem_ia = Mensagem(atendimento_id=atendimento.id, origem="IA", conteudo=resposta_ia)
        db.add(mensagem_ia)
        atendimento.status = "RESPONDIDO_IA"

    db.commit()
    db.refresh(mensagem)

    return mensagem


@router.post("/atendimentos", response_model=AtendimentoCreateResponse)
def criar_atendimento(payload: AtendimentoCreate, db: Session = Depends(get_db)):
    classificacao = classificar_mensagem(payload.mensagem)
    cliente = None

    if payload.cliente.email:
        email_normalizado = payload.cliente.email.strip().lower()
        cliente = db.query(Cliente).filter(func.lower(Cliente.email) == email_normalizado).first()

    if cliente:
        cliente.nome = payload.cliente.nome

        if payload.cliente.telefone:
            cliente.telefone = payload.cliente.telefone

        if payload.cliente.cpf:
            cliente.cpf = payload.cliente.cpf
    else:
        cliente = Cliente(
            nome=payload.cliente.nome,
            email=payload.cliente.email,
            telefone=payload.cliente.telefone,
            cpf=payload.cliente.cpf,
        )
        db.add(cliente)
        db.flush()

    atendimento = Atendimento(
        cliente_id=cliente.id,
        categoria=classificacao["categoria"],
        prioridade=classificacao["prioridade"],
        sentimento=classificacao["sentimento"],
        status="FILA_HUMANA" if classificacao["precisa_humano"] else "CLASSIFICADO",
        precisa_humano=classificacao["precisa_humano"],
        confianca_ia=classificacao["confianca"],
        resumo_ia=classificacao["resumo"],
    )

    db.add(atendimento)
    db.flush()

    mensagem_cliente = Mensagem(atendimento_id=atendimento.id, origem="CLIENTE", conteudo=payload.mensagem)
    db.add(mensagem_cliente)

    if not classificacao["precisa_humano"]:
        resposta_ia = gerar_resposta_automatica(payload.mensagem, classificacao)
        mensagem_ia = Mensagem(atendimento_id=atendimento.id, origem="IA", conteudo=resposta_ia)
        db.add(mensagem_ia)
        atendimento.status = "RESPONDIDO_IA"

    db.commit()
    db.refresh(atendimento)

    return atendimento


@router.get("/atendimentos", response_model=list[AtendimentoResponse])
def listar_atendimentos(
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    query = db.query(Atendimento)

    if status:
        query = query.filter(Atendimento.status == status)

    if prioridade:
        query = query.filter(Atendimento.prioridade == prioridade)

    return query.order_by(Atendimento.criado_em.desc()).all()


@router.get("/atendimentos/{atendimento_id}", response_model=AtendimentoDetalheResponse)
def detalhar_atendimento(
    atendimento_id: str,
    db: Session = Depends(get_db),
    autorizacao: Usuario | None = Depends(exigir_administrador_ou_n8n),
):
    return buscar_atendimento(atendimento_id, db)


@router.get("/atendimentos/{atendimento_id}/cliente", response_model=AtendimentoClienteResponse)
def detalhar_conversa_cliente(atendimento_id: str, token: uuid.UUID, db: Session = Depends(get_db)):
    return buscar_atendimento_cliente(atendimento_id, token, db)


@router.patch("/atendimentos/{atendimento_id}/status", response_model=AtendimentoResponse)
def atualizar_status(
    atendimento_id: str,
    payload: AtendimentoStatusUpdate,
    db: Session = Depends(get_db),
    autorizacao: Usuario | None = Depends(exigir_administrador_ou_n8n),
):
    atendimento = buscar_atendimento(atendimento_id, db)
    atendimento.status = payload.status
    atendimento.atualizado_em = datetime.now(timezone.utc)

    db.commit()
    db.refresh(atendimento)

    return atendimento


@router.post("/atendimentos/{atendimento_id}/mensagens", response_model=MensagemResponse)
def adicionar_mensagem(
    atendimento_id: str,
    payload: MensagemCreate,
    db: Session = Depends(get_db),
    autorizacao: Usuario | None = Depends(exigir_administrador_ou_n8n),
):
    atendimento = buscar_atendimento(atendimento_id, db)
    return salvar_mensagem(atendimento, payload.origem, payload.conteudo, db)


@router.post("/atendimentos/{atendimento_id}/cliente/mensagens", response_model=MensagemResponse)
def adicionar_mensagem_cliente(
    atendimento_id: str,
    payload: MensagemClienteCreate,
    token: uuid.UUID,
    db: Session = Depends(get_db),
):
    atendimento = buscar_atendimento_cliente(atendimento_id, token, db)
    return salvar_mensagem(atendimento, "CLIENTE", payload.conteudo, db)


@router.get("/metricas/resumo", response_model=MetricasResumo)
def obter_metricas(
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    hoje = date.today()

    atendimentos_hoje = db.query(func.count(Atendimento.id)).filter(func.date(Atendimento.criado_em) == hoje).scalar()
    resolvidos_ia = db.query(func.count(Atendimento.id)).filter(Atendimento.status == "RESPONDIDO_IA").scalar()
    aguardando_humano = db.query(func.count(Atendimento.id)).filter(Atendimento.status == "FILA_HUMANA").scalar()
    urgentes = db.query(func.count(Atendimento.id)).filter(Atendimento.prioridade == "URGENTE").scalar()

    return MetricasResumo(
        atendimentos_hoje=atendimentos_hoje or 0,
        resolvidos_ia=resolvidos_ia or 0,
        aguardando_humano=aguardando_humano or 0,
        urgentes=urgentes or 0,
    )
