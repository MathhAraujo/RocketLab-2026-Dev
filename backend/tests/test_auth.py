def test_login_admin_retorna_token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_senha_errada_retorna_401(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "errada"})
    assert r.status_code == 401
    assert "detail" in r.json()


def test_login_usuario_inexistente_retorna_401(client):
    r = client.post("/api/auth/login", json={"username": "fantasma", "password": "qualquer"})
    assert r.status_code == 401


def test_login_sem_body_retorna_422(client):
    r = client.post("/api/auth/login", json={})
    assert r.status_code == 422


def test_login_campos_obrigatorios(client):
    r = client.post("/api/auth/login", json={"username": "admin"})
    assert r.status_code == 422
    r = client.post("/api/auth/login", json={"password": "admin"})
    assert r.status_code == 422


def test_register_cria_usuario_com_sucesso(client):
    r = client.post("/api/auth/register", json={"username": "novo_user", "password": "1234"})
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "novo_user"
    assert body["is_admin"] is False


def test_register_usuario_ja_existente_retorna_400(client):
    client.post("/api/auth/register", json={"username": "duplicado", "password": "1234"})
    r = client.post("/api/auth/register", json={"username": "duplicado", "password": "abcd"})
    assert r.status_code == 400
    assert "já existe" in r.json()["detail"]


def test_register_senha_muito_curta_retorna_400(client):
    r = client.post("/api/auth/register", json={"username": "novo", "password": "123"})
    assert r.status_code == 400
    assert "4 caracteres" in r.json()["detail"]


def test_register_senha_exatamente_4_chars_aceita(client):
    r = client.post("/api/auth/register", json={"username": "novo4", "password": "1234"})
    assert r.status_code == 201


def test_register_usuario_pode_logar_apos_criacao(client):
    client.post("/api/auth/register", json={"username": "novo_login", "password": "senha123"})
    r = client.post("/api/auth/login", json={"username": "novo_login", "password": "senha123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_register_nao_cria_admin(client):
    r = client.post("/api/auth/register", json={"username": "user_comum", "password": "1234"})
    assert r.json()["is_admin"] is False


def test_me_com_token_admin_retorna_dados(client, admin_headers):
    r = client.get("/api/auth/me", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "admin"
    assert body["is_admin"] is True


def test_me_com_token_usuario_comum(user_client, user_headers):
    r = user_client.get("/api/auth/me", headers=user_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "visitante"
    assert body["is_admin"] is False


def test_me_sem_token_retorna_401(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_com_token_invalido_retorna_401(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert r.status_code == 401


def test_me_com_token_malformado_retorna_401(client):
    r = client.get("/api/auth/me", headers={"Authorization": "tokensembearer"})
    assert r.status_code == 401


def test_listagem_produtos_requer_autenticacao(client):
    r = client.get("/api/produtos/")
    assert r.status_code == 401


def test_listagem_produtos_aceita_usuario_comum(user_client, user_headers):
    r = user_client.get("/api/produtos/", headers=user_headers)
    assert r.status_code == 200


def test_criar_produto_bloqueado_para_usuario_comum(user_client, user_headers):
    r = user_client.post(
        "/api/produtos/",
        json={
            "nome_produto": "Produto Bloqueado",
            "categoria_produto": "calcados",
            "peso_produto_gramas": 200.0,
            "comprimento_centimetros": 10.0,
            "altura_centimetros": 5.0,
            "largura_centimetros": 5.0,
        },
        headers=user_headers,
    )
    assert r.status_code == 403


def test_criar_produto_permitido_para_admin(client, admin_headers):
    r = client.post(
        "/api/produtos/",
        json={
            "nome_produto": "Produto Admin",
            "categoria_produto": "calcados",
            "peso_produto_gramas": 200.0,
            "comprimento_centimetros": 10.0,
            "altura_centimetros": 5.0,
            "largura_centimetros": 5.0,
        },
        headers=admin_headers,
    )
    assert r.status_code == 201


def test_deletar_produto_bloqueado_para_usuario_comum(user_client, user_headers):
    r_login = user_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    admin_h = {"Authorization": f"Bearer {r_login.json()['access_token']}"}

    r_create = user_client.post(
        "/api/produtos/",
        json={
            "nome_produto": "Para Deletar",
            "categoria_produto": "calcados",
            "peso_produto_gramas": 200.0,
            "comprimento_centimetros": 10.0,
            "altura_centimetros": 5.0,
            "largura_centimetros": 5.0,
        },
        headers=admin_h,
    )
    id_ = r_create.json()["id_produto"]
    r_del = user_client.delete(f"/api/produtos/{id_}", headers=user_headers)
    assert r_del.status_code == 403
