import uuid
from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.schemas.produto import (
    AvaliacaoStats,
    ItemAvaliacao,
    PaginatedProdutos,
    ProdutoCreate,
    ProdutoDetalhe,
    ProdutoListItem,
    ProdutoUpdate,
    VendaStats,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _subq_vendas(db: Session):
    return (
        db.query(
            ItemPedido.id_produto,
            func.count(ItemPedido.id_item).label("total_vendas"),
            func.avg(ItemPedido.preco_BRL).label("preco_medio"),
        )
        .group_by(ItemPedido.id_produto)
        .subquery()
    )


def _subq_avaliacoes(db: Session):
    return (
        db.query(
            ItemPedido.id_produto.label("id_produto_av"),
            func.count(AvaliacaoPedido.id_avaliacao).label("total_avaliacoes"),
            func.avg(AvaliacaoPedido.avaliacao).label("avaliacao_media"),
        )
        .join(Pedido, Pedido.id_pedido == AvaliacaoPedido.id_pedido)
        .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
        .group_by(ItemPedido.id_produto)
        .subquery()
    )


def _linha_para_dict(linha: tuple) -> dict:
    produto_obj, total_vendas, preco_medio, total_avaliacoes, avaliacao_media = linha
    return {
        **{c.name: getattr(produto_obj, c.name) for c in produto_obj.__table__.columns},
        "total_vendas": total_vendas,
        "preco_medio": float(preco_medio) if preco_medio is not None else None,
        "total_avaliacoes": total_avaliacoes,
        "avaliacao_media": float(avaliacao_media) if avaliacao_media is not None else None,
    }


def _buscar_produto_enriquecido(id_produto: str, db: Session) -> Optional[dict]:
    sq_v = _subq_vendas(db)
    sq_a = _subq_avaliacoes(db)
    linha = (
        db.query(
            Produto,
            func.coalesce(sq_v.c.total_vendas, 0).label("total_vendas"),
            func.coalesce(sq_v.c.preco_medio, None).label("preco_medio"),
            func.coalesce(sq_a.c.total_avaliacoes, 0).label("total_avaliacoes"),
            func.coalesce(sq_a.c.avaliacao_media, None).label("avaliacao_media"),
        )
        .outerjoin(sq_v, sq_v.c.id_produto == Produto.id_produto)
        .outerjoin(sq_a, sq_a.c.id_produto_av == Produto.id_produto)
        .filter(Produto.id_produto == id_produto)
        .first()
    )
    return _linha_para_dict(linha) if linha else None


_ORDENACAO = {
    "nome_produto": lambda sv, sa: Produto.nome_produto,
    "categoria_produto": lambda sv, sa: Produto.categoria_produto,
    "preco_medio": lambda sv, sa: sv.c.preco_medio,
    "avaliacao_media": lambda sv, sa: sa.c.avaliacao_media,
    "total_vendas": lambda sv, sa: sv.c.total_vendas,
}


@router.get(
    "/",
    response_model=PaginatedProdutos,
    summary="Listar Produtos",
    description="Lista paginada de produtos com opções de busca, filtro por categoria e cálculo de totais de venda e avaliação média.",
)
def listar_produtos(
    busca: Optional[str] = Query(None, alias="search"),
    categoria: Optional[str] = Query(None),
    pagina: int = Query(1, alias="page", ge=1),
    por_pagina: int = Query(20, alias="per_page", ge=1, le=100),
    ordenar_por: str = Query("nome_produto", alias="sort_by"),
    ordem: str = Query("asc", alias="order"),
    db: Session = Depends(get_db),
):
    sq_v = _subq_vendas(db)
    sq_a = _subq_avaliacoes(db)

    query = (
        db.query(
            Produto,
            func.coalesce(sq_v.c.total_vendas, 0).label("total_vendas"),
            func.coalesce(sq_v.c.preco_medio, None).label("preco_medio"),
            func.coalesce(sq_a.c.total_avaliacoes, 0).label("total_avaliacoes"),
            func.coalesce(sq_a.c.avaliacao_media, None).label("avaliacao_media"),
        )
        .outerjoin(sq_v, sq_v.c.id_produto == Produto.id_produto)
        .outerjoin(sq_a, sq_a.c.id_produto_av == Produto.id_produto)
    )

    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            Produto.nome_produto.ilike(termo) | Produto.categoria_produto.ilike(termo)
        )
    if categoria:
        query = query.filter(Produto.categoria_produto == categoria)

    total = query.count()

    coluna_fn = _ORDENACAO.get(ordenar_por, _ORDENACAO["nome_produto"])
    coluna = coluna_fn(sq_v, sq_a)
    coluna_ordenada = coluna.desc() if ordem == "desc" else coluna.asc()

    skip = (pagina - 1) * por_pagina
    linhas = query.order_by(coluna_ordenada).offset(skip).limit(por_pagina).all()

    return {
        "items": [ProdutoListItem(**_linha_para_dict(l)) for l in linhas],
        "total": total,
        "page": pagina,
        "per_page": por_pagina,
        "pages": ceil(total / por_pagina) if total > 0 else 0,
    }


@router.get(
    "/categorias",
    response_model=List[str],
    summary="Listar Categorias",
    description="Retorna todas as categorias únicas de produtos registradas.",
)
def listar_categorias(db: Session = Depends(get_db)):
    rows = (
        db.query(Produto.categoria_produto)
        .distinct()
        .order_by(Produto.categoria_produto)
        .all()
    )
    return [r[0] for r in rows]


@router.get(
    "/{id_produto}",
    response_model=ProdutoDetalhe,
    summary="Obter Produto",
    description="Retorna detalhes completos de um produto específico com base no seu ID.",
)
def obter_produto(id_produto: str, db: Session = Depends(get_db)):
    produto = _buscar_produto_enriquecido(id_produto, db)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post(
    "/",
    response_model=ProdutoDetalhe,
    status_code=201,
    summary="Criar Produto",
    description="Registra um novo produto.",
)
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    novo = Produto(id_produto=uuid.uuid4().hex, **payload.model_dump())
    db.add(novo)
    db.commit()
    return _buscar_produto_enriquecido(novo.id_produto, db)


@router.put(
    "/{id_produto}",
    response_model=ProdutoDetalhe,
    summary="Atualizar Produto",
    description="Altera as propriedades de um produto existente com base em seu ID.",
)
def atualizar_produto(
    id_produto: str, payload: ProdutoUpdate, db: Session = Depends(get_db)
):
    campos = payload.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=422, detail="Nenhum campo para atualizar")

    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for campo, valor in campos.items():
        setattr(produto, campo, valor)
    db.commit()
    return _buscar_produto_enriquecido(id_produto, db)


@router.delete(
    "/{id_produto}",
    status_code=204,
    summary="Deletar Produto",
    description="Deleta um produto de forma definitiva.",
)
def deletar_produto(id_produto: str, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()


@router.get(
    "/{id_produto}/vendas",
    response_model=VendaStats,
    summary="Obter Vendas do Produto",
    description="Calcula e retorna estatísticas consolidadas de venda de um produto.",
)
def obter_vendas_produto(id_produto: str, db: Session = Depends(get_db)):
    if not db.query(Produto).filter(Produto.id_produto == id_produto).first():
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    stats = (
        db.query(
            func.count(ItemPedido.id_item).label("total_vendas"),
            func.coalesce(func.sum(ItemPedido.preco_BRL), 0.0).label("receita_total"),
            func.avg(ItemPedido.preco_BRL).label("preco_medio"),
            func.min(ItemPedido.preco_BRL).label("preco_minimo"),
            func.max(ItemPedido.preco_BRL).label("preco_maximo"),
            func.count(func.distinct(ItemPedido.id_pedido)).label("total_pedidos"),
        )
        .filter(ItemPedido.id_produto == id_produto)
        .one()
    )

    status_rows = (
        db.query(Pedido.status, func.count(Pedido.id_pedido).label("qtd"))
        .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
        .filter(ItemPedido.id_produto == id_produto)
        .group_by(Pedido.status)
        .all()
    )

    return VendaStats(
        total_vendas=stats.total_vendas,
        receita_total=float(stats.receita_total),
        preco_medio=float(stats.preco_medio) if stats.preco_medio is not None else None,
        preco_minimo=float(stats.preco_minimo) if stats.preco_minimo is not None else None,
        preco_maximo=float(stats.preco_maximo) if stats.preco_maximo is not None else None,
        total_pedidos=stats.total_pedidos,
        vendas_por_status={row.status: row.qtd for row in status_rows},
    )


@router.get(
    "/{id_produto}/avaliacoes",
    response_model=AvaliacaoStats,
    summary="Listar Avaliações do Produto",
    description="Recupera de maneira paginada as avaliações de consumidores atreladas a este produto.",
)
def listar_avaliacoes_produto(
    id_produto: str,
    pagina: int = Query(1, alias="page", ge=1),
    por_pagina: int = Query(10, alias="per_page", ge=1, le=100),
    db: Session = Depends(get_db),
):
    if not db.query(Produto).filter(Produto.id_produto == id_produto).first():
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    sq_pedidos = (
        db.query(ItemPedido.id_pedido)
        .filter(ItemPedido.id_produto == id_produto)
        .distinct()
    )

    query_base = db.query(AvaliacaoPedido).filter(
        AvaliacaoPedido.id_pedido.in_(sq_pedidos)
    )

    total = query_base.count()

    stats = (
        db.query(
            func.avg(AvaliacaoPedido.avaliacao).label("avaliacao_media"),
            func.count(AvaliacaoPedido.id_avaliacao).label("total_avaliacoes"),
        )
        .filter(AvaliacaoPedido.id_pedido.in_(sq_pedidos))
        .one()
    )

    dist_rows = (
        db.query(AvaliacaoPedido.avaliacao, func.count().label("qtd"))
        .filter(AvaliacaoPedido.id_pedido.in_(sq_pedidos))
        .group_by(AvaliacaoPedido.avaliacao)
        .all()
    )

    skip = (pagina - 1) * por_pagina
    avaliacoes = (
        query_base
        .order_by(AvaliacaoPedido.data_comentario.desc())
        .offset(skip)
        .limit(por_pagina)
        .all()
    )

    return AvaliacaoStats(
        avaliacao_media=(
            float(stats.avaliacao_media) if stats.avaliacao_media is not None else None
        ),
        total_avaliacoes=stats.total_avaliacoes,
        distribuicao={row.avaliacao: row.qtd for row in dist_rows},
        avaliacoes=[
            ItemAvaliacao(
                id_avaliacao=av.id_avaliacao,
                avaliacao=av.avaliacao,
                titulo_comentario=av.titulo_comentario,
                comentario=av.comentario,
                data_comentario=(
                    av.data_comentario.isoformat() if av.data_comentario else None
                ),
            )
            for av in avaliacoes
        ],
        total=total,
        page=pagina,
        per_page=por_pagina,
        pages=ceil(total / por_pagina) if total > 0 else 0,
    )
