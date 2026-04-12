from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UsuarioAutenticado
from app.models.usuario import Usuario
from app.security import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

MIN_PASSWORD_LENGTH = 4


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description=(
        "Autentica um usuário existente com `username` e `password`. "
        "Retorna um **Bearer JWT** para ser usado no header `Authorization` das demais requisições. "
        "O token tem validade de **7 dias**."
    ),
    response_description="Token JWT de acesso e tipo do token.",
    responses={
        401: {"description": "Credenciais inválidas — usuário não encontrado ou senha incorreta."},
        422: {"description": "Corpo da requisição inválido — campos obrigatórios ausentes."},
    },
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )
    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post(
    "/register",
    response_model=UsuarioAutenticado,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova conta",
    description=(
        "Registra um novo usuário no sistema. "
        "Contas criadas por este endpoint possuem acesso **somente leitura** (`is_admin=false`): "
        "podem consultar produtos, vendas e avaliações, mas não criar, editar ou excluir dados. "
        "\n\n**Regras de senha:** mínimo de 4 caracteres."
    ),
    response_description="Dados do usuário recém-criado, incluindo flag de administrador.",
    responses={
        400: {"description": "Username já em uso, ou senha muito curta (menos de 4 caracteres)."},
        422: {"description": "Corpo da requisição inválido."},
    },
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if len(payload.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"A senha deve conter pelo menos {MIN_PASSWORD_LENGTH} caracteres.")
    user = db.query(Usuario).filter(Usuario.username == payload.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Nome de usuário já existe.")
    novo = Usuario(
        id_usuario=uuid.uuid4().hex,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return UsuarioAutenticado(username=novo.username, is_admin=novo.is_admin)


@router.get(
    "/me",
    response_model=UsuarioAutenticado,
    summary="Perfil do usuário autenticado",
    description=(
        "Retorna os dados do usuário atualmente autenticado com base no **Bearer JWT** "
        "fornecido no header `Authorization`. "
        "Use este endpoint para verificar se o token ainda é válido e identificar o role do usuário."
    ),
    response_description="Username e flag de administrador do usuário autenticado.",
    responses={
        401: {"description": "Token ausente, inválido ou expirado."},
    },
)
def me(current_user: Usuario = Depends(get_current_user)):
    return UsuarioAutenticado(username=current_user.username, is_admin=current_user.is_admin)

