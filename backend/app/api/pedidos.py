from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.security import exigir_administrador
from app.database import get_db
from app.models.models import Cliente, Pedido, Usuario
from app.schemas.schemas import PedidoCreate, PedidoResponse, PedidoUpdate


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoResponse, status_code=201)
def criar_pedido(
    payload: PedidoCreate,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    cliente = db.query(Cliente).filter(Cliente.id == payload.cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado.")

    numero = payload.numero.strip()
    pedido_existente = db.query(Pedido).filter(Pedido.numero == numero).first()

    if pedido_existente:
        raise HTTPException(status_code=409, detail="Ja existe um pedido com este numero.")

    pedido = Pedido(
        numero=numero,
        cliente_id=payload.cliente_id,
        status=payload.status.strip().upper(),
        previsao_entrega=payload.previsao_entrega,
        codigo_rastreio=payload.codigo_rastreio,
    )

    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    return pedido


@router.get("", response_model=list[PedidoResponse])
def listar_pedidos(
    cliente_id: UUID | None = None,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    query = db.query(Pedido)

    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)

    return query.order_by(Pedido.criado_em.desc()).all()


@router.get("/{pedido_id}", response_model=PedidoResponse)
def detalhar_pedido(
    pedido_id: UUID,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")

    return pedido


@router.patch("/{pedido_id}", response_model=PedidoResponse)
def atualizar_pedido(
    pedido_id: UUID,
    payload: PedidoUpdate,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")

    dados = payload.model_dump(exclude_unset=True)

    if "numero" in dados:
        numero = dados["numero"].strip()
        pedido_com_mesmo_numero = db.query(Pedido).filter(Pedido.numero == numero, Pedido.id != pedido.id).first()

        if pedido_com_mesmo_numero:
            raise HTTPException(status_code=409, detail="Ja existe outro pedido com este numero.")

        pedido.numero = numero

    if "status" in dados:
        pedido.status = dados["status"].strip().upper()

    if "previsao_entrega" in dados:
        pedido.previsao_entrega = dados["previsao_entrega"]

    if "codigo_rastreio" in dados:
        pedido.codigo_rastreio = dados["codigo_rastreio"]

    db.commit()
    db.refresh(pedido)

    return pedido
