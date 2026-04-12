from fastapi import APIRouter

from app.schemas.auth import LoginRequest, TokenResponse, UsuarioAutenticado

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Autentica o usuário e retorna um token de acesso. Atualmente aceita qualquer credencial (implementação mock).",
    response_description="Token de acesso e tipo do token.",
)
def login(payload: LoginRequest):
    return TokenResponse(access_token="mock-token", token_type="bearer")


@router.get(
    "/me",
    response_model=UsuarioAutenticado,
    summary="Usuário autenticado",
    description="Retorna os dados do usuário atualmente autenticado. Atualmente retorna dados mockados.",
    response_description="Dados do usuário autenticado.",
)
def me():
    return UsuarioAutenticado(username="admin")
