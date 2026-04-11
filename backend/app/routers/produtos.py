import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.schemas.produto import (
    AvaliacaoResumo,
    ProdutoCreate,
    ProdutoDetalhes,
    ProdutoResponse,
    ProdutoUpdate,
    VendaResumo,
    PaginatedProdutos,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=PaginatedProdutos)
def listar_produtos(
    busca: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Produto)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            Produto.nome_produto.ilike(termo) | Produto.categoria_produto.ilike(termo)
        )
        if categoria:
            query = query.filter(Produto.categoria_produto == categoria)
    total = query.count()
    items = query.order_by(Produto.nome_produto).offset(skip).limit(limit).all()
            
    return {"total": total, "items": items}

@router.get("/{id_produto}", response_model=ProdutoDetalhes)
def obter_produto(id_produto: str, db: Session = Depends(get_db)):
    """Retorna um produto com resumo de vendas e avaliações."""
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Resumo de vendas: soma de itens_pedidos para este produto
    vendas_row = (
        db.query(
            func.count(ItemPedido.id_item).label("total_vendas"),
            func.coalesce(func.sum(ItemPedido.preco_BRL), 0.0).label("receita_total"),
        )
        .filter(ItemPedido.id_produto == id_produto)
        .one()
    )

    # Resumo de avaliações: via itens_pedidos → pedidos → avaliacoes_pedidos
    avaliacoes_row = (
        db.query(
            func.count(AvaliacaoPedido.id_avaliacao).label("total_avaliacoes"),
            func.coalesce(func.avg(AvaliacaoPedido.avaliacao), 0.0).label("media_avaliacao"),
        )
        .join(Pedido, Pedido.id_pedido == AvaliacaoPedido.id_pedido)
        .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
        .filter(ItemPedido.id_produto == id_produto)
        .one()
    )

    return ProdutoDetalhes(
        **{c.name: getattr(produto, c.name) for c in produto.__table__.columns},
        vendas=VendaResumo(
            total_vendas=vendas_row.total_vendas,
            receita_total=float(vendas_row.receita_total),
        ),
        avaliacoes=AvaliacaoResumo(
            total_avaliacoes=avaliacoes_row.total_avaliacoes,
            media_avaliacao=float(avaliacoes_row.media_avaliacao),
        ),
    )


@router.post("/", response_model=ProdutoResponse, status_code=201)
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto com ID gerado automaticamente."""
    novo = Produto(id_produto=uuid.uuid4().hex, **payload.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{id_produto}", response_model=ProdutoResponse)
def atualizar_produto(
    id_produto: str, payload: ProdutoUpdate, db: Session = Depends(get_db)
):
    """Atualiza campos de um produto existente (somente campos enviados são alterados)."""
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{id_produto}", status_code=204)
def deletar_produto(id_produto: str, db: Session = Depends(get_db)):
    """Remove um produto pelo ID."""
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
