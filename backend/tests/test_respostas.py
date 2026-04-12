import uuid

from tests.conftest import (
    criar_avaliacao,
    criar_consumidor,
    criar_pedido_com_item,
    criar_vendedor,
)


PRODUTO_BASE = {
    "nome_produto": "Tênis de Resposta",
    "categoria_produto": "calcados",
    "peso_produto_gramas": 500.0,
    "comprimento_centimetros": 30.0,
    "altura_centimetros": 15.0,
    "largura_centimetros": 10.0,
}


def criar_produto(client, admin_headers, dados=None):
    return client.post("/api/produtos/", json=dados or PRODUTO_BASE, headers=admin_headers)


def test_responder_avaliacao_sucesso(client, admin_headers, db):
    r = criar_produto(client, admin_headers)
    assert r.status_code == 201
    id_produto = r.json()["id_produto"]

    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=5, titulo="Ótimo", comentario="Excelente")

    payload = {"resposta": "Obrigado pelo feedback!"}
    r2 = client.post(f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", json=payload, headers=admin_headers)
    assert r2.status_code == 200
    body = r2.json()
    assert body["resposta_admin"] == payload["resposta"]
    assert body["autor_resposta"] == "admin"
    assert body["data_resposta"] is not None


def test_responder_avaliacao_nao_encontrada(client, admin_headers):
    payload = {"resposta": "Obrigado"}
    r = client.post("/api/produtos/avaliacoes/invalid_id/resposta", json=payload, headers=admin_headers)
    assert r.status_code == 404


def test_responder_avaliacao_proibido_para_nao_admin(client, db, admin_headers):
    r = criar_produto(client, admin_headers)
    assert r.status_code == 201
    id_produto = r.json()["id_produto"]

    id_consumidor = criar_consumidor(db)
    id_vendedor = criar_vendedor(db)
    id_pedido = criar_pedido_com_item(db, id_produto, id_consumidor, id_vendedor)
    id_avaliacao = criar_avaliacao(db, id_pedido, nota=4)

    # criar usuário não-admin diretamente no DB e gerar token
    from app.models.usuario import Usuario
    from app.security import create_access_token, get_password_hash

    username = f"user_{uuid.uuid4().hex[:8]}"
    user = Usuario(id_usuario=uuid.uuid4().hex, username=username, hashed_password=get_password_hash("1234"), is_admin=False)
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.username})
    user_headers = {"Authorization": f"Bearer {token}"}

    payload = {"resposta": "Tentativa indevida"}
    r2 = client.post(f"/api/produtos/avaliacoes/{id_avaliacao}/resposta", json=payload, headers=user_headers)
    assert r2.status_code == 403
