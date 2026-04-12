from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, produtos

app = FastAPI(
    title="Sistema de Compras Online",
    description="API para gerenciamento de pedidos, produtos, consumidores e vendedores.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(produtos.router, prefix="/api")


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Verifica o status da API e se está rodando corretamente.",
)
def health():
    return {"status": "ok", "message": "API rodando com sucesso!"}
