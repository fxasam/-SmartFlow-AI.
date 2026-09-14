import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Usuario


CAMINHO_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(CAMINHO_ENV)

ALGORITMO = "HS256"
DURACAO_TOKEN_HORAS = 8

autenticacao_bearer = HTTPBearer(auto_error=False)


def obter_chave_secreta() -> str:
    chave = os.getenv("JWT_SECRET_KEY", "").strip()

    if len(chave) < 32:
        raise RuntimeError(
            "Configure JWT_SECRET_KEY no arquivo .env."
        )

    return chave


def obter_chave_n8n() -> str:
    chave = os.getenv("N8N_WEBHOOK_SECRET", "").strip()

    if len(chave) < 32:
        raise RuntimeError(
            "Configure N8N_WEBHOOK_SECRET no arquivo .env."
        )

    return chave


def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")

    if len(senha_bytes) > 72:
        raise HTTPException(
            status_code=422,
            detail="A senha excede o limite de 72 bytes.",
        )

    hash_bytes = bcrypt.hashpw(
        senha_bytes,
        bcrypt.gensalt(),
    )

    return hash_bytes.decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            senha.encode("utf-8"),
            senha_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def criar_token_acesso(usuario_id: UUID) -> str:
    agora = datetime.now(timezone.utc)

    dados = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(hours=DURACAO_TOKEN_HORAS),
        "tipo": "acesso",
    }

    return jwt.encode(
        dados,
        obter_chave_secreta(),
        algorithm=ALGORITMO,
    )


def erro_autenticacao() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Sessao invalida ou expirada. Faca login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def obter_usuario_por_credenciais(
    credenciais: HTTPAuthorizationCredentials | None,
    db: Session,
) -> Usuario:
    if not credenciais:
        raise erro_autenticacao()

    try:
        dados = jwt.decode(
            credenciais.credentials,
            obter_chave_secreta(),
            algorithms=[ALGORITMO],
            options={"require": ["sub", "iat", "exp", "tipo"]},
        )

        if dados["tipo"] != "acesso":
            raise erro_autenticacao()

        usuario_id = UUID(dados["sub"])

    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise erro_autenticacao()

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise erro_autenticacao()

    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuario inativo.")

    return usuario


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(autenticacao_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    return obter_usuario_por_credenciais(credenciais, db)


def exigir_administrador(
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usuario:
    if usuario.perfil != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Esta operacao exige perfil de administrador.",
        )

    return usuario


def exigir_administrador_ou_n8n(
    chave_n8n: str | None = Header(default=None, alias="X-N8N-Secret"),
    credenciais: HTTPAuthorizationCredentials | None = Depends(autenticacao_bearer),
    db: Session = Depends(get_db),
) -> Usuario | None:
    if chave_n8n:
        if secrets.compare_digest(chave_n8n, obter_chave_n8n()):
            return None

        raise HTTPException(status_code=401, detail="Chave de automacao invalida.")

    usuario = obter_usuario_por_credenciais(credenciais, db)

    if usuario.perfil != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Esta operacao exige perfil de administrador.",
        )

    return usuario
