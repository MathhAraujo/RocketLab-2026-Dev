import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # garante registro de todos os modelos no Base
from app.database import Base, get_db
from app.main import app
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.consumidor import Consumidor
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.vendedor import Vendedor


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sessao = Session()
    yield sessao
    sessao.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def criar_consumidor(db) -> str:
    id_consumidor = uuid.uuid4().hex
    db.add(Consumidor(
        id_consumidor=id_consumidor,
        nome_consumidor="Consumidor Teste",
        prefixo_cep="01310",
        cidade="São Paulo",
        estado="SP",
    ))
    db.commit()
    return id_consumidor


def criar_vendedor(db) -> str:
    id_vendedor = uuid.uuid4().hex
    db.add(Vendedor(
        id_vendedor=id_vendedor,
        nome_vendedor="Vendedor Teste",
        prefixo_cep="01310",
        cidade="São Paulo",
        estado="SP",
    ))
    db.commit()
    return id_vendedor


def criar_pedido_com_item(
    db,
    id_produto: str,
    id_consumidor: str,
    id_vendedor: str,
    preco: float = 100.0,
    status: str = "entregue",
) -> str:
    id_pedido = uuid.uuid4().hex
    db.add(Pedido(
        id_pedido=id_pedido,
        id_consumidor=id_consumidor,
        status=status,
    ))
    db.add(ItemPedido(
        id_pedido=id_pedido,
        id_item=1,
        id_produto=id_produto,
        id_vendedor=id_vendedor,
        preco_BRL=preco,
        preco_frete=10.0,
    ))
    db.commit()
    return id_pedido


def criar_avaliacao(
    db,
    id_pedido: str,
    nota: int,
    titulo: str = None,
    comentario: str = None,
) -> str:
    id_avaliacao = uuid.uuid4().hex
    db.add(AvaliacaoPedido(
        id_avaliacao=id_avaliacao,
        id_pedido=id_pedido,
        avaliacao=nota,
        titulo_comentario=titulo,
        comentario=comentario,
        data_comentario=datetime.now(),
    ))
    db.commit()
    return id_avaliacao
