from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UsuarioAutenticado(BaseModel):
    username: str
    is_admin: bool
