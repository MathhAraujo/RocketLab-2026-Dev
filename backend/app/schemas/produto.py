from typing import Dict, List, Optional

from pydantic import BaseModel


class ProdutoBase(BaseModel):
    nome_produto: str
    categoria_produto: str
    peso_produto_gramas: Optional[float] = None
    comprimento_centimetros: Optional[float] = None
    altura_centimetros: Optional[float] = None
    largura_centimetros: Optional[float] = None


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome_produto: Optional[str] = None
    categoria_produto: Optional[str] = None
    peso_produto_gramas: Optional[float] = None
    comprimento_centimetros: Optional[float] = None
    altura_centimetros: Optional[float] = None
    largura_centimetros: Optional[float] = None


class ProdutoListItem(BaseModel):
    id_produto: str
    nome_produto: str
    categoria_produto: str
    preco_medio: Optional[float] = None
    avaliacao_media: Optional[float] = None
    total_avaliacoes: int = 0
    total_vendas: int = 0

    model_config = {"from_attributes": True}


class ProdutoDetalhe(ProdutoListItem):
    peso_produto_gramas: Optional[float] = None
    comprimento_centimetros: Optional[float] = None
    altura_centimetros: Optional[float] = None
    largura_centimetros: Optional[float] = None


class PaginatedProdutos(BaseModel):
    items: List[ProdutoListItem]
    total: int
    page: int
    per_page: int
    pages: int


class VendaStats(BaseModel):
    total_vendas: int
    receita_total: float
    preco_medio: Optional[float] = None
    preco_minimo: Optional[float] = None
    preco_maximo: Optional[float] = None
    total_pedidos: int
    vendas_por_status: Dict[str, int]


class ItemAvaliacao(BaseModel):
    id_avaliacao: str
    avaliacao: int
    titulo_comentario: Optional[str] = None
    comentario: Optional[str] = None
    data_comentario: Optional[str] = None
    resposta_admin: Optional[str] = None
    autor_resposta: Optional[str] = None
    data_resposta: Optional[str] = None


class AvaliacaoStats(BaseModel):
    avaliacao_media: Optional[float] = None
    total_avaliacoes: int
    distribuicao: Dict[int, int]
    avaliacoes: List[ItemAvaliacao]
    total: int
    page: int
    per_page: int
    pages: int


class RespostaRequest(BaseModel):
    resposta: str
