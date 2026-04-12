# Sistema de Gerenciamento de E-Commerce

Aplicacao fullstack desenvolvida para o Rocket Lab 2026. O sistema permite que gerentes de loja visualizem o catalogo de produtos, consultem estatisticas de vendas, leiam e respondam avaliacoes de consumidores, e gerenciem o cadastro de produtos com controle de acesso por perfil.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Vite + React + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| Banco de dados | SQLite via SQLAlchemy 2.0 |
| Migrations | Alembic |
| Autenticacao | JWT (Bearer token, 7 dias) |
| Cache | fastapi-cache2 (InMemory, TTL 60 s) |
| Testes | pytest + httpx |

## Funcionalidades

**Requisitos obrigatorios**
- Catalogo paginado de produtos com informacoes detalhadas (nome, categoria, dimensoes, peso)
- Busca por nome e/ou categoria com debounce no frontend
- Pagina de detalhes com estatisticas de vendas e avaliacoes dos consumidores
- Media de avaliacoes com distribuicao por estrelas
- Criacao, edicao e remocao de produtos (restrito a administradores)

**Funcionalidades extras**
- Autenticacao com JWT; perfis `admin` e `viewer`
- Paginacao via backend com controle de pagina e itens por pagina
- Filtros de busca por categoria e ordenacao por nome, preco, avaliacoes ou vendas
- Cache de consultas no backend (invalida automaticamente em operacoes de escrita)
- Resposta e exclusao de resposta a avaliacoes de consumidores (restrito a administradores)
- Responsividade para dispositivos moveis
- Testes automatizados (autenticacao, CRUD de produtos, respostas a avaliacoes)
- Documentacao interativa via Swagger UI (`/docs`) e ReDoc (`/redoc`)
- Containerizacao com Docker e Docker Compose (backend e frontend prontos para producao)

## Estrutura do projeto

```
.
├── backend/
│   ├── alembic/          # Migrations do banco de dados
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── routers/      # Endpoints FastAPI (auth, produtos)
│   │   ├── schemas/      # Schemas Pydantic
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── main.py
│   │   └── security.py
│   ├── data/             # Arquivos CSV para popular o banco
│   ├── tests/            # Suite de testes pytest
│   ├── seed.py           # Script de populacao do banco
│   ├── entrypoint.sh     # Script de inicializacao do container
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # Clientes HTTP (axios)
│   │   ├── components/   # Componentes React reutilizaveis
│   │   ├── contexts/     # Contextos de autenticacao e tema
│   │   ├── hooks/        # Hooks customizados
│   │   ├── pages/        # Paginas da aplicacao
│   │   ├── types/        # Tipos TypeScript
│   │   └── utils/
│   └── vite.config.ts
└── docker-compose.yml
```

## Executando com Docker

### Pre-requisitos

- Docker e Docker Compose instalados

### Passos

```bash
# 1. Clone o repositorio
git clone <url-do-repositorio>
cd RocketLab-2026-Dev

# 2. Suba os containers
docker compose up --build
```

O container do backend executa automaticamente as migrations (`alembic upgrade head`) e popula o banco com os dados dos arquivos CSV antes de iniciar o servidor.

| Servico | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

Para parar os containers:

```bash
docker compose down
```

## Executando sem Docker

### Pre-requisitos

- Python 3.11+
- Node.js 20+

### Backend

```bash
cd backend

# Crie e ative o ambiente virtual
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Instale as dependencias
pip install -r requirements.txt

# Crie o arquivo de variaveis de ambiente
cp .env.example .env

# Execute as migrations
alembic upgrade head

# Popule o banco de dados
python seed.py

# Inicie o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

A API estara disponivel em `http://localhost:8000`.

### Frontend

Em um novo terminal:

```bash
cd frontend

# Instale as dependencias
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```

O frontend estara disponivel em `http://localhost:5173`.

> A variavel de ambiente `VITE_API_URL` define o endereco base da API. O valor padrao e `http://localhost:8000/api` e funciona para uso local. So e necessario alterar se o backend estiver rodando em um host ou porta diferente.

## Primeiro acesso

Ao acessar o sistema pela primeira vez, clique em "Criar uma nova conta" na tela de login. A tela de cadastro permite escolher o tipo de acesso diretamente: **Visualizador** (somente leitura) ou **Administrador** (criacao, edicao, exclusao de produtos e resposta a avaliacoes).

## Variaveis de ambiente

### Backend

| Variavel | Padrao | Descricao |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./database.db` | URL de conexao com o banco SQLite |
| `JWT_SECRET` | *(gerado automaticamente)* | Chave secreta para assinatura dos tokens JWT |
| `ALLOWED_ORIGINS` | `["http://localhost:5173","http://127.0.0.1:5173"]` | Origens permitidas pelo CORS |

Em producao, defina `JWT_SECRET` com um valor longo, aleatorio e unico. Sem um arquivo `.env` contendo `JWT_SECRET`, uma chave aleatoria e gerada a cada reinicio do servidor, invalidando todos os tokens existentes. Um arquivo `backend/.env.example` com valores de referencia esta disponivel no repositorio.

### Frontend

| Variavel | Padrao | Descricao |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000/api` | Endereco base da API do backend |

## Acesso pelo celular na mesma rede

Para acessar a aplicacao de um dispositivo movel conectado ao mesmo Wi-Fi da maquina host, siga os passos abaixo.

> O cliente HTTP do frontend detecta automaticamente o hostname pelo qual a pagina foi carregada e substitui `localhost` pelo IP real da maquina em todas as requisicoes. Nao e necessario configurar `VITE_API_URL` para acesso na rede local.

### 1. Descubra o IP local da maquina

**Windows**
```bash
ipconfig
# Procure por "Endereco IPv4" na interface Wi-Fi ou Ethernet. Exemplo: 192.168.1.100
```

**Linux / macOS**
```bash
ip addr show   # ou: hostname -I
```

### 2. Libere o CORS no backend

Adicione a origem do celular na variavel `ALLOWED_ORIGINS` do arquivo `backend/.env`. Substitua `192.168.1.100` pelo IP real da sua maquina:

```dotenv
ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://192.168.1.100:5173"]
```

### 3. Inicie os servicos

**Com Docker**

O `docker-compose.yml` padrao vincula as portas apenas ao `127.0.0.1`, bloqueando o acesso pela rede local. Para liberar, edite o arquivo e troque o bind das portas:

```yaml
services:
  backend:
    ports:
      - "8000:8000"   # era: "127.0.0.1:8000:8000"
  frontend:
    ports:
      - "5173:5173"   # era: "127.0.0.1:5173:5173"
```

Em seguida, reconstrua e suba os containers:

```bash
docker compose up --build
```

**Sem Docker**

O backend ja escuta em `0.0.0.0` e o Vite ja esta configurado com `host: true`, portanto nenhuma alteracao adicional e necessaria. Basta iniciar os servicos normalmente conforme descrito na secao "Executando sem Docker".

### 4. Acesse pelo celular

Com os servicos rodando, abra o navegador do celular e acesse:

```
http://192.168.1.100:5173
```

> Se a pagina nao carregar, verifique se o firewall do sistema operacional permite conexoes nas portas 5173 e 8000. No Windows, isso pode ser ajustado em "Firewall do Windows Defender > Regras de Entrada".

## Executando os testes

```bash
cd backend

# Com o ambiente virtual ativado
pytest tests/ -v
```

Os testes utilizam um banco SQLite em memoria isolado e cobrem autenticacao (login, registro, protecao de rotas), CRUD completo de produtos e operacoes de resposta a avaliacoes.

## Endpoints principais

| Metodo | Rota | Descricao | Perfil |
|---|---|---|---|
| `POST` | `/api/auth/login` | Autenticar usuario | Publico |
| `POST` | `/api/auth/register` | Criar nova conta | Publico |
| `GET` | `/api/auth/me` | Dados do usuario autenticado | Autenticado |
| `GET` | `/api/produtos/` | Listar produtos (paginado, filtravel) | Autenticado |
| `GET` | `/api/produtos/categorias` | Listar categorias disponiveis | Autenticado |
| `GET` | `/api/produtos/{id}` | Detalhe do produto | Autenticado |
| `POST` | `/api/produtos/` | Criar produto | Admin |
| `PUT` | `/api/produtos/{id}` | Atualizar produto | Admin |
| `DELETE` | `/api/produtos/{id}` | Remover produto | Admin |
| `GET` | `/api/produtos/{id}/vendas` | Estatisticas de vendas | Autenticado |
| `GET` | `/api/produtos/{id}/avaliacoes` | Avaliacoes paginadas + media | Autenticado |
| `POST` | `/api/produtos/avaliacoes/{id}/resposta` | Responder avaliacao | Admin |
| `DELETE` | `/api/produtos/avaliacoes/{id}/resposta` | Remover resposta | Admin |
