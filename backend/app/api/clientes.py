from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import exigir_administrador
from app.database import get_db
from app.models.models import Cliente, Usuario


router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("")
def listar_clientes(
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    clientes = db.query(Cliente).order_by(Cliente.criado_em.desc()).all()

    return [
        {
            "id": str(cliente.id),
            "nome": cliente.nome,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "criado_em": cliente.criado_em,
            "total_atendimentos": len(cliente.atendimentos),
        }
        for cliente in clientes
    ]
