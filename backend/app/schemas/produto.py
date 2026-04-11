from typing import Optional, List

from pydantic import BaseModel


class ProdutoBase(BaseModel):
    nome_produto: str
    categoria_produto: str
    peso_produto_gramas: Optional[float] = None
    comprimento_centimetros: Optional[float] = None
    altura_centimetros: Optional[float] = None
    largura_centimetros: Optional[float] = None

class PaginatedProdutos(BaseModel):
    total: int
    items: List[ProdutoResponse]

class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    """Todos os campos são opcionais para suportar atualizações parciais."""
    nome_produto: Optional[str] = None
    categoria_produto: Optional[str] = None
    peso_produto_gramas: Optional[float] = None
    comprimento_centimetros: Optional[float] = None
    altura_centimetros: Optional[float] = None
    largura_centimetros: Optional[float] = None


class ProdutoResponse(ProdutoBase):
    id_produto: str

    model_config = {"from_attributes": True}


class AvaliacaoResumo(BaseModel):
    total_avaliacoes: int
    media_avaliacao: float


class VendaResumo(BaseModel):
    total_vendas: int
    receita_total: float


class ProdutoDetalhes(ProdutoResponse):
    avaliacoes: AvaliacaoResumo
    vendas: VendaResumo
