import { ShoppingBag, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { ProdutoListItem } from "../../types/produto";
import { formatCategoria, formatCurrency, formatNumber } from "../../utils/formatters";
import { CATEGORIA_IMAGENS } from "../../utils/constants";
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { StarRating } from "../ui/StarRating";

interface ProdutoCardProps {
  produto: ProdutoListItem;
}

export function ProdutoCard({ produto }: Readonly<ProdutoCardProps>) {
  const navigate = useNavigate();
  const imagemCategoria = CATEGORIA_IMAGENS[produto.categoria_produto];

  return (
    <Card onClick={() => navigate(`/produtos/${produto.id_produto}`)}>
      {/* Image */}
      <div
        className="relative overflow-hidden rounded-t-xl card-image-responsive"
        style={{ background: "var(--color-bg-elevated)" }}
      >
        {imagemCategoria ? (
          <img
            src={imagemCategoria}
            alt={produto.categoria_produto}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <ShoppingBag size={28} className="text-indigo-400 opacity-50" />
          </div>
        )}
        <div
          className="absolute inset-0"
          style={{
            background: "linear-gradient(to bottom, transparent 40%, var(--color-bg-surface) 100%)",
          }}
        />
      </div>

      {/* Content */}
      <div className="p-3 md:p-4 space-y-3">
        <Badge category={produto.categoria_produto}>
          {formatCategoria(produto.categoria_produto)}
        </Badge>

        <h3
          className="line-clamp-2 text-sm md:text-base font-semibold leading-snug"
          style={{ color: "var(--color-text-primary)" }}
        >
          {produto.nome_produto}
        </h3>

        {/* Rating row */}
        <div className="flex items-center justify-between">
          <StarRating rating={produto.avaliacao_media} size={13} showValue />
          <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
            {formatNumber(produto.total_avaliacoes)} aval.
          </span>
        </div>

        {/* Price + sales row */}
        <div className="flex items-center justify-between">
          <span
            className="text-lg font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: "#34d399" }}
          >
            {formatCurrency(produto.preco_medio)}
          </span>
          <span className="flex items-center gap-1 text-xs" style={{ color: "var(--color-text-secondary)" }}>
            <TrendingUp size={12} />
            {formatNumber(produto.total_vendas)}
          </span>
        </div>
      </div>
    </Card>
  );
}
