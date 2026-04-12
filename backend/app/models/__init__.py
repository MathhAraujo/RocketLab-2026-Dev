# Importa todos os models para que o SQLAlchemy e o Alembic os registrem
from app.models.consumidor import Consumidor
from app.models.produto import Produto
from app.models.vendedor import Vendedor
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.usuario import Usuario

__all__ = [
    "Consumidor",
    "Produto",
    "Vendedor",
    "Pedido",
    "ItemPedido",
    "AvaliacaoPedido",
    "Usuario",
]
