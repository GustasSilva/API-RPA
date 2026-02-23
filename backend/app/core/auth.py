from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import criar_token
from app.core.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if (
        form_data.username != settings.admin_username
        or form_data.password != settings.admin_password
    ):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({"sub": form_data.username})

    return {
        "access_token": token,
        "token_type": "bearer",
    }
