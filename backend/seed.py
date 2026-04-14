import csv
import os
import sys
import datetime
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.dialects.sqlite import insert as sqlite_insert  # noqa: E402

from app.database import SessionLocal, engine, Base  # noqa: E402
from app.models.avaliacao_pedido import AvaliacaoPedido  # noqa: E402
from app.models.consumidor import Consumidor  # noqa: E402
from app.models.item_pedido import ItemPedido  # noqa: E402
from app.models.pedido import Pedido  # noqa: E402
from app.models.produto import Produto  # noqa: E402
from app.models.vendedor import Vendedor  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

BATCH_SIZE = 5_000


# ---------------------------------------------------------------------------
# Helpers de conversão
# ---------------------------------------------------------------------------

def _float(val: str) -> float | None:
    s = val.strip()
    return float(s) if s else None


def _str_or_none(val: str) -> str | None:
    s = val.strip()
    return s if s else None


def _datetime(val: str) -> datetime | None:
    s = val.strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _date(val: str) -> date | None:
    dt = _datetime(val)
    return dt.date() if dt else None


def _stream_insert(db, model, path: str, row_fn) -> int:
    """Lê o CSV em streaming e insere em batches, sem carregar tudo na memória."""
    seen: set = set()
    batch = []
    total = 0
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row, key = row_fn(r)
            if key in seen:
                continue
            seen.add(key)
            batch.append(row)
            if len(batch) >= BATCH_SIZE:
                db.execute(sqlite_insert(model).values(batch).on_conflict_do_nothing())
                db.commit()
                total += len(batch)
                batch = []
    if batch:
        db.execute(sqlite_insert(model).values(batch).on_conflict_do_nothing())
        db.commit()
        total += len(batch)
    return total


# ---------------------------------------------------------------------------
# Funções de seed por tabela
# ---------------------------------------------------------------------------

def _seed_consumidores(db) -> None:
    if db.query(Consumidor).count() > 0:
        print("  consumidores: já populado, pulando.")
        return

    def row_fn(r):
        return {
            "id_consumidor": r["id_consumidor"],
            "prefixo_cep": r["prefixo_cep"],
            "nome_consumidor": r["nome_consumidor"],
            "cidade": r["cidade"],
            "estado": r["estado"],
        }, r["id_consumidor"]

    n = _stream_insert(db, Consumidor, os.path.join(DATA_DIR, "dim_consumidores.csv"), row_fn)
    print(f"  consumidores: {n} registros inseridos.")


def _seed_vendedores(db) -> None:
    if db.query(Vendedor).count() > 0:
        print("  vendedores: já populado, pulando.")
        return

    def row_fn(r):
        return {
            "id_vendedor": r["id_vendedor"],
            "nome_vendedor": r["nome_vendedor"],
            "prefixo_cep": r["prefixo_cep"],
            "cidade": r["cidade"],
            "estado": r["estado"],
        }, r["id_vendedor"]

    n = _stream_insert(db, Vendedor, os.path.join(DATA_DIR, "dim_vendedores.csv"), row_fn)
    print(f"  vendedores: {n} registros inseridos.")


def _seed_produtos(db) -> None:
    if db.query(Produto).count() > 0:
        print("  produtos: já populado, pulando.")
        return

    def row_fn(r):
        return {
            "id_produto": r["id_produto"],
            "nome_produto": r["nome_produto"],
            "categoria_produto": r["categoria_produto"],
            "peso_produto_gramas": _float(r["peso_produto_gramas"]),
            "comprimento_centimetros": _float(r["comprimento_centimetros"]),
            "altura_centimetros": _float(r["altura_centimetros"]),
            "largura_centimetros": _float(r["largura_centimetros"]),
        }, r["id_produto"]

    n = _stream_insert(db, Produto, os.path.join(DATA_DIR, "dim_produtos.csv"), row_fn)
    print(f"  produtos: {n} registros inseridos.")


def _seed_pedidos(db) -> None:
    if db.query(Pedido).count() > 0:
        print("  pedidos: já populado, pulando.")
        return

    def row_fn(r):
        return {
            "id_pedido": r["id_pedido"],
            "id_consumidor": r["id_consumidor"],
            "status": r["status"],
            "pedido_compra_timestamp": _datetime(r["pedido_compra_timestamp"]),
            "pedido_entregue_timestamp": _datetime(r["pedido_entregue_timestamp"]),
            "data_estimada_entrega": _date(r["data_estimada_entrega"]),
            "tempo_entrega_dias": _float(r["tempo_entrega_dias"]),
            "tempo_entrega_estimado_dias": _float(r["tempo_entrega_estimado_dias"]),
            "diferenca_entrega_dias": _float(r["diferenca_entrega_dias"]),
            "entrega_no_prazo": _str_or_none(r["entrega_no_prazo"]),
        }, r["id_pedido"]

    n = _stream_insert(db, Pedido, os.path.join(DATA_DIR, "fat_pedidos.csv"), row_fn)
    print(f"  pedidos: {n} registros inseridos.")


def _seed_itens_pedidos(db) -> None:
    if db.query(ItemPedido).count() > 0:
        print("  itens_pedidos: já populado, pulando.")
        return

    def row_fn(r):
        return {
            "id_pedido": r["id_pedido"],
            "id_item": int(r["id_item"]),
            "id_produto": r["id_produto"],
            "id_vendedor": r["id_vendedor"],
            "preco_BRL": float(r["preco_BRL"]),
            "preco_frete": float(r["preco_frete"]),
        }, (r["id_pedido"], r["id_item"])

    n = _stream_insert(db, ItemPedido, os.path.join(DATA_DIR, "fat_itens_pedidos.csv"), row_fn)
    print(f"  itens_pedidos: {n} registros inseridos.")


def _seed_avaliacoes(db) -> None:
    if db.query(AvaliacaoPedido).count() > 0:
        print("  avaliacoes_pedidos: já populado, pulando.")
        return

    def row_fn(r):
        return {
            "id_avaliacao": r["id_avaliacao"],
            "id_pedido": r["id_pedido"],
            "avaliacao": int(r["avaliacao"]),
            "titulo_comentario": _str_or_none(r["titulo_comentario"]),
            "comentario": _str_or_none(r["comentario"]),
            "data_comentario": _datetime(r["data_comentario"]),
            "data_resposta": _datetime(r["data_resposta"]),
        }, r["id_avaliacao"]

    n = _stream_insert(db, AvaliacaoPedido, os.path.join(DATA_DIR, "fat_avaliacoes_pedidos.csv"), row_fn)
    print(f"  avaliacoes_pedidos: {n} registros inseridos.")


def _atualizar_agregados_produtos(db) -> None:
    """Calcula total_vendas, preco_medio, total_avaliacoes e avaliacao_media para cada produto."""
    from sqlalchemy import func

    # Vendas: total e preço médio por produto
    vendas_stats = (
        db.query(
            ItemPedido.id_produto,
            func.count(ItemPedido.id_item).label("total_vendas"),
            func.avg(ItemPedido.preco_BRL).label("preco_medio"),
        )
        .group_by(ItemPedido.id_produto)
        .all()
    )

    for row in vendas_stats:
        db.query(Produto).filter(Produto.id_produto == row.id_produto).update({
            Produto.total_vendas: row.total_vendas,
            Produto.preco_medio: round(float(row.preco_medio), 2) if row.preco_medio else None,
        })

    # Avaliações: total e média por produto (via pedidos)
    aval_stats = (
        db.query(
            ItemPedido.id_produto,
            func.count(AvaliacaoPedido.id_avaliacao).label("total_avaliacoes"),
            func.avg(AvaliacaoPedido.avaliacao).label("avaliacao_media"),
        )
        .join(AvaliacaoPedido, AvaliacaoPedido.id_pedido == ItemPedido.id_pedido)
        .group_by(ItemPedido.id_produto)
        .all()
    )

    for row in aval_stats:
        db.query(Produto).filter(Produto.id_produto == row.id_produto).update({
            Produto.total_avaliacoes: row.total_avaliacoes,
            Produto.avaliacao_media: round(float(row.avaliacao_media), 2) if row.avaliacao_media else None,
        })

    db.commit()
    print("  agregados atualizados.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def seed_all() -> None:
    print("Garantindo que as tabelas existem...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Populando consumidores...")
        _seed_consumidores(db)

        print("Populando vendedores...")
        _seed_vendedores(db)

        print("Populando produtos...")
        _seed_produtos(db)

        print("Populando pedidos...")
        _seed_pedidos(db)

        print("Populando itens de pedidos...")
        _seed_itens_pedidos(db)

        print("Populando avaliações...")
        _seed_avaliacoes(db)

        print("Atualizando agregados dos produtos...")
        _atualizar_agregados_produtos(db)

        print("Banco de dados populado com sucesso!")
    except Exception as exc:
        db.rollback()
        print(f"Erro: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
