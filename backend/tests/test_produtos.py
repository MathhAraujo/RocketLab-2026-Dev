from tests.conftest import (
    criar_avaliacao,
    criar_consumidor,
    criar_pedido_com_item,
    criar_vendedor,
)

PRODUTO_BASE = {
    "nome_produto": "Tênis de Teste",
    "categoria_produto": "calcados",
    "peso_produto_gramas": 500.0,
    "comprimento_centimetros": 30.0,
    "altura_centimetros": 15.0,
    "largura_centimetros": 10.0,
}


def criar(client, dados=None):
    return client.post("/api/produtos/", json=dados or PRODUTO_BASE)


def test_listar_vazio(client):
    r = client.get("/api/produtos/")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["page"] == 1
    assert body["pages"] == 0


def test_criar_produto(client):
    r = criar(client)
    assert r.status_code == 201
    body = r.json()
    assert body["nome_produto"] == PRODUTO_BASE["nome_produto"]
    assert "id_produto" in body


def test_listar_retorna_produto_criado(client):
    criar(client)
    r = client.get("/api/produtos/")
    assert r.json()["total"] == 1


def test_listagem_inclui_campos_calculados(client):
    criar(client)
    r = client.get("/api/produtos/")
    item = r.json()["items"][0]
    assert "preco_medio" in item
    assert "avaliacao_media" in item
    assert "total_avaliacoes" in item
    assert "total_vendas" in item
    assert item["total_vendas"] == 0
    assert item["total_avaliacoes"] == 0
    assert item["preco_medio"] is None
    assert item["avaliacao_media"] is None


def test_busca_por_nome(client):
    criar(client)
    r = client.get("/api/produtos/?search=Tênis")
    assert r.json()["total"] == 1
    r = client.get("/api/produtos/?search=inexistente")
    assert r.json()["total"] == 0


def test_filtro_por_categoria(client):
    criar(client)
    r = client.get("/api/produtos/?categoria=calcados")
    assert r.json()["total"] == 1
    r = client.get("/api/produtos/?categoria=outra")
    assert r.json()["total"] == 0


def test_paginacao(client):
    for i in range(5):
        criar(client, {**PRODUTO_BASE, "nome_produto": f"Produto {i}"})
    r = client.get("/api/produtos/?page=1&per_page=2")
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["pages"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 2


def test_paginacao_segunda_pagina(client):
    for i in range(5):
        criar(client, {**PRODUTO_BASE, "nome_produto": f"Produto {i}"})
    r = client.get("/api/produtos/?page=2&per_page=2")
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2
    assert body["page"] == 2


def test_ordenacao_por_nome_asc(client):
    criar(client, {**PRODUTO_BASE, "nome_produto": "Zebra"})
    criar(client, {**PRODUTO_BASE, "nome_produto": "Abacaxi"})
    r = client.get("/api/produtos/?sort_by=nome_produto&order=asc")
    items = r.json()["items"]
    assert items[0]["nome_produto"] == "Abacaxi"
    assert items[1]["nome_produto"] == "Zebra"


def test_ordenacao_por_nome_desc(client):
    criar(client, {**PRODUTO_BASE, "nome_produto": "Zebra"})
    criar(client, {**PRODUTO_BASE, "nome_produto": "Abacaxi"})
    r = client.get("/api/produtos/?sort_by=nome_produto&order=desc")
    items = r.json()["items"]
    assert items[0]["nome_produto"] == "Zebra"
    assert items[1]["nome_produto"] == "Abacaxi"


def test_ordenacao_por_categoria(client):
    criar(client, {**PRODUTO_BASE, "nome_produto": "P1", "categoria_produto": "roupas"})
    criar(client, {**PRODUTO_BASE, "nome_produto": "P2", "categoria_produto": "calcados"})
    r = client.get("/api/produtos/?sort_by=categoria_produto&order=asc")
    items = r.json()["items"]
    assert items[0]["categoria_produto"] == "calcados"
    assert items[1]["categoria_produto"] == "roupas"


def test_obter_produto(client):
    id_ = criar(client).json()["id_produto"]
    r = client.get(f"/api/produtos/{id_}")
    assert r.status_code == 200
    body = r.json()
    assert body["id_produto"] == id_
    assert "total_vendas" in body
    assert "preco_medio" in body
    # resposta deve ser flat — sem dicionários aninhados de vendas/avaliacoes
    assert "vendas" not in body
    assert "avaliacoes" not in body


def test_obter_produto_inexistente(client):
    r = client.get("/api/produtos/id-que-nao-existe")
    assert r.status_code == 404


def test_atualizar_produto(client):
    id_ = criar(client).json()["id_produto"]
    r = client.put(f"/api/produtos/{id_}", json={"nome_produto": "Novo Nome"})
    assert r.status_code == 200
    assert r.json()["nome_produto"] == "Novo Nome"


def test_atualizar_body_vazio_retorna_422(client):
    id_ = criar(client).json()["id_produto"]
    r = client.put(f"/api/produtos/{id_}", json={})
    assert r.status_code == 422


def test_deletar_produto(client):
    id_ = criar(client).json()["id_produto"]
    r = client.delete(f"/api/produtos/{id_}")
    assert r.status_code == 204
    r = client.get(f"/api/produtos/{id_}")
    assert r.status_code == 404


def test_listar_categorias(client):
    criar(client)
    r = client.get("/api/produtos/categorias")
    assert r.status_code == 200
    assert "calcados" in r.json()


def test_vendas_produto_sem_dados(client):
    id_ = criar(client).json()["id_produto"]
    r = client.get(f"/api/produtos/{id_}/vendas")
    assert r.status_code == 200
    body = r.json()
    assert body["total_vendas"] == 0
    assert body["receita_total"] == 0.0
    assert body["preco_medio"] is None
    assert body["preco_minimo"] is None
    assert body["preco_maximo"] is None
    assert body["total_pedidos"] == 0
    assert body["vendas_por_status"] == {}


def test_vendas_produto_com_dados(client, db):
    id_produto = criar(client).json()["id_produto"]
    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor, preco=100.0)
    criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor, preco=200.0)

    r = client.get(f"/api/produtos/{id_produto}/vendas")
    assert r.status_code == 200
    body = r.json()
    assert body["total_vendas"] == 2
    assert body["receita_total"] == 300.0
    assert body["preco_medio"] == 150.0
    assert body["preco_minimo"] == 100.0
    assert body["preco_maximo"] == 200.0
    assert body["total_pedidos"] == 2
    assert "entregue" in body["vendas_por_status"]
    assert body["vendas_por_status"]["entregue"] == 2


def test_vendas_produto_inexistente(client):
    r = client.get("/api/produtos/id-inexistente/vendas")
    assert r.status_code == 404


def test_avaliacoes_produto_sem_dados(client):
    id_ = criar(client).json()["id_produto"]
    r = client.get(f"/api/produtos/{id_}/avaliacoes")
    assert r.status_code == 200
    body = r.json()
    assert body["total_avaliacoes"] == 0
    assert body["avaliacao_media"] is None
    assert body["distribuicao"] == {}
    assert body["avaliacoes"] == []
    assert body["total"] == 0


def test_avaliacoes_produto_com_dados(client, db):
    id_produto = criar(client).json()["id_produto"]
    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido1 = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_pedido2 = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    criar_avaliacao(db, id_pedido1, nota=5, titulo="Ótimo", comentario="Excelente produto")
    criar_avaliacao(db, id_pedido2, nota=3)

    r = client.get(f"/api/produtos/{id_produto}/avaliacoes")
    assert r.status_code == 200
    body = r.json()
    assert body["total_avaliacoes"] == 2
    assert body["avaliacao_media"] == 4.0
    assert body["distribuicao"]["5"] == 1
    assert body["distribuicao"]["3"] == 1
    assert len(body["avaliacoes"]) == 2
    assert body["total"] == 2


def test_avaliacoes_paginacao(client, db):
    id_produto = criar(client).json()["id_produto"]
    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    for nota in range(1, 6):
        id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
        criar_avaliacao(db, id_pedido, nota=nota)

    r = client.get(f"/api/produtos/{id_produto}/avaliacoes?page=1&per_page=2")
    assert r.status_code == 200
    body = r.json()
    assert len(body["avaliacoes"]) == 2
    assert body["total"] == 5
    assert body["pages"] == 3
    assert body["page"] == 1
    assert body["per_page"] == 2


def test_avaliacoes_produto_inexistente(client):
    r = client.get("/api/produtos/id-inexistente/avaliacoes")
    assert r.status_code == 404
