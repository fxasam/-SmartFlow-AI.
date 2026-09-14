from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import DURACAO_TOKEN_HORAS, criar_token_acesso, exigir_administrador, gerar_hash_senha, obter_usuario_atual, verificar_senha
from app.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse


router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    administrador: Usuario = Depends(exigir_administrador),
):
    email_normalizado = str(dados.email).strip().lower()

    usuario_existente = db.query(Usuario).filter(func.lower(Usuario.email) == email_normalizado).first()

    if usuario_existente:
        raise HTTPException(status_code=409, detail="Ja existe um usuario com este e-mail.")

    novo_usuario = Usuario(
        nome=dados.nome,
        email=email_normalizado,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=dados.perfil,
    )

    db.add(novo_usuario)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Nao foi possivel cadastrar o usuario. Verifique se o e-mail ja esta em uso.")

    db.refresh(novo_usuario)
    return novo_usuario


@router.post("/login")
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    email_normalizado = str(dados.email).strip().lower()
    usuario = db.query(Usuario).filter(func.lower(Usuario.email) == email_normalizado).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha invalidos.", headers={"WWW-Authenticate": "Bearer"})

    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuario inativo.")

    token = criar_token_acesso(usuario.id)

    return {
        "mensagem": "Login realizado com sucesso.",
        "access_token": token,
        "token_type": "bearer",
        "expires_in": DURACAO_TOKEN_HORAS * 3600,
        "usuario": {
            "id": str(usuario.id),
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil,
        },
    }


@router.get("/me", response_model=UsuarioResponse)
def consultar_usuario_logado(usuario: Usuario = Depends(obter_usuario_atual)):
    return usuario
