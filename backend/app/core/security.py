from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.settings import settings


def criar_token(dados: dict) -> str:
    """
    Cria um token de acesso com base nos dados fornecidos.

    Os dados fornecidos devem ser um dicionário com as informações
    a serem incluídas no token. O token terá um campo "exp"
    com a data de expiração do token, calculada com base
    na hora atual mais o tempo de expiração definido
    na configura da aplicação.
    """
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
