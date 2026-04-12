import { ChevronRight, Edit, Trash2, DollarSign, ShoppingCart, Star, MessageSquare, ShoppingBag, ZoomIn, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteProduto, getAvaliacoes, getProduto, getVendas } from "../api/produtos";
import { AvaliacaoDistribuicao } from "../components/produtos/AvaliacaoDistribuicao";
import { AvaliacoesList } from "../components/produtos/AvaliacoesList";
import { VendasStats } from "../components/produtos/VendasStats";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Loading } from "../components/ui/Loading";
import { Modal } from "../components/ui/Modal";
import { StatCard } from "../components/ui/StatCard";
import { StarRating } from "../components/ui/StarRating";
import type { AvaliacaoStats } from "../types/avaliacao";
import type { Produto } from "../types/produto";
import type { VendaStats } from "../types/venda";
import { formatCategoria, formatCurrency, formatNumber, formatRating } from "../utils/formatters";
import { CATEGORIA_IMAGENS, REVIEWS_PAGE_SIZE } from "../utils/constants";

export function ProdutoDetalhePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [produto, setProduto] = useState<Produto | null>(null);
  const [vendas, setVendas] = useState<VendaStats | null>(null);
  const [avaliacoes, setAvaliacoes] = useState<AvaliacaoStats | null>(null);
  const [avaliacoesPage, setAvaliacoesPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showImageLightbox, setShowImageLightbox] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    Promise.all([getProduto(id), getVendas(id)])
      .then(([p, v]) => {
        setProduto(p);
        setVendas(v);
      })
      .catch(() => navigate("/catalogo"))
      .finally(() => setIsLoading(false));
  }, [id, navigate]);

  useEffect(() => {
    if (!id) return;
    getAvaliacoes(id, { page: avaliacoesPage, per_page: REVIEWS_PAGE_SIZE }).then(setAvaliacoes);
  }, [id, avaliacoesPage]);

  useEffect(() => {
    if (!showImageLightbox) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setShowImageLightbox(false); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [showImageLightbox]);

  const handleDelete = async () => {
    if (!id) return;
    setIsDeleting(true);
    setDeleteError("");
    try {
      await deleteProduto(id);
      navigate("/catalogo");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Erro ao remover produto";
      setDeleteError(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) return <Loading />;
  if (!produto) return null;

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm" style={{ color: "var(--color-text-secondary)" }}>
        <Link
          to="/catalogo"
          className="transition-colors hover:text-indigo-400"
          style={{ color: "var(--color-text-secondary)" }}
        >
          Catálogo
        </Link>
        <ChevronRight size={14} />
        <span style={{ color: "var(--color-text-primary)" }} className="truncate">
          {produto.nome_produto}
        </span>
      </nav>

      {/* Imagem da categoria */}
      {(() => {
        const imagem = CATEGORIA_IMAGENS[produto.categoria_produto];
        return (
          <div
            className={`relative h-56 w-full overflow-hidden rounded-2xl group${imagem ? " cursor-zoom-in" : ""}`}
            style={{ background: "var(--color-bg-elevated)" }}
            role={imagem ? "button" : undefined}
            tabIndex={imagem ? 0 : undefined}
            onClick={imagem ? () => setShowImageLightbox(true) : undefined}
            onKeyDown={imagem ? (e) => { if (e.key === "Enter") setShowImageLightbox(true); } : undefined}
          >
            {imagem ? (
              <img
                src={imagem}
                alt={produto.categoria_produto}
                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full items-center justify-center">
                <ShoppingBag size={40} className="text-indigo-400 opacity-40" />
              </div>
            )}
            <div
              className="absolute inset-0"
              style={{
                background: "linear-gradient(to bottom, transparent 50%, var(--color-bg-base) 100%)",
              }}
            />
            {imagem && (
              <div className="absolute top-3 right-3 rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ background: "rgba(0,0,0,0.45)" }}>
                <ZoomIn size={16} className="text-white" />
              </div>
            )}
          </div>
        );
      })()}

      {/* Hero */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <Badge category={produto.categoria_produto}>
            {formatCategoria(produto.categoria_produto)}
          </Badge>
          <h1
            className="text-3xl font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: "var(--color-text-primary)" }}
          >
            {produto.nome_produto}
          </h1>
          <div className="flex items-center gap-3">
            <StarRating rating={produto.avaliacao_media} size={18} showValue />
            <span className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              ({formatNumber(produto.total_avaliacoes)} avaliações)
            </span>
          </div>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button variant="secondary" onClick={() => navigate(`/produtos/${id}/editar`)}>
            <Edit size={15} />
            Editar
          </Button>
          <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
            <Trash2 size={15} />
            Excluir
          </Button>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          icon={DollarSign}
          label="Preço Médio"
          value={formatCurrency(produto.preco_medio)}
          iconColor="text-emerald-400"
        />
        <StatCard
          icon={ShoppingCart}
          label="Total Vendas"
          value={formatNumber(produto.total_vendas)}
          iconColor="text-indigo-400"
        />
        <StatCard
          icon={Star}
          label="Avaliação"
          value={formatRating(produto.avaliacao_media)}
          iconColor="text-amber-400"
        />
        <StatCard
          icon={MessageSquare}
          label="Avaliações"
          value={formatNumber(produto.total_avaliacoes)}
          iconColor="text-zinc-400"
        />
      </div>

      {/* Dimensões */}
      {(produto.peso_produto_gramas != null || produto.comprimento_centimetros != null) && (
        <section>
          <h2
            className="mb-3 text-sm font-semibold uppercase tracking-wide"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Dimensões
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { label: "Peso", value: produto.peso_produto_gramas, unit: "g" },
              { label: "Comprimento", value: produto.comprimento_centimetros, unit: "cm" },
              { label: "Altura", value: produto.altura_centimetros, unit: "cm" },
              { label: "Largura", value: produto.largura_centimetros, unit: "cm" },
            ].map(({ label, value, unit }) => (
              <div
                key={label}
                className="rounded-xl border p-3 text-center"
                style={{
                  background: "var(--color-bg-surface)",
                  borderColor: "var(--color-border)",
                }}
              >
                <p className="text-xs" style={{ color: "var(--color-text-secondary)" }}>{label}</p>
                <p className="text-sm font-semibold mt-1" style={{ color: "var(--color-text-primary)" }}>
                  {value == null ? "—" : `${value} ${unit}`}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Vendas */}
      {vendas && (
        <section>
          <h2
            className="mb-3 text-sm font-semibold uppercase tracking-wide"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Estatísticas de Vendas
          </h2>
          <VendasStats stats={vendas} />
        </section>
      )}

      {/* Avaliações */}
      {avaliacoes && (
        <section>
          <h2
            className="mb-4 text-sm font-semibold uppercase tracking-wide"
            style={{ color: "var(--color-text-secondary)" }}
          >
            Avaliações
          </h2>
          <div
            className="rounded-xl border p-5 mb-4"
            style={{
              background: "var(--color-bg-surface)",
              borderColor: "var(--color-border)",
            }}
          >
            <AvaliacaoDistribuicao stats={avaliacoes} />
          </div>
          <AvaliacoesList stats={avaliacoes} onPageChange={setAvaliacoesPage} />
        </section>
      )}

      {/* Lightbox imagem */}
      {showImageLightbox && (() => {
        const imagem = CATEGORIA_IMAGENS[produto.categoria_produto];
        return imagem ? (
          <div
            role="presentation"
            className="fixed inset-0 z-50 flex items-center justify-center p-6 backdrop-blur-sm"
            style={{ background: "rgba(0,0,0,0.85)" }}
            onClick={() => setShowImageLightbox(false)}
            onKeyDown={(e) => { if (e.key === "Escape") setShowImageLightbox(false); }}
          >
            <button
              className="absolute top-4 right-4 rounded-full p-2 transition-colors hover:bg-white/10"
              style={{ color: "white" }}
              onClick={() => setShowImageLightbox(false)}
            >
              <X size={22} />
            </button>
            <div role="presentation" onClick={(e) => e.stopPropagation()}>
              <img
                src={imagem}
                alt={produto.categoria_produto}
                className="max-h-full max-w-full rounded-xl object-contain shadow-2xl"
              />
            </div>
          </div>
        ) : null;
      })()}

      {/* Modal exclusão */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Confirmar exclusão"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
              Cancelar
            </Button>
            <Button variant="danger" isLoading={isDeleting} onClick={handleDelete}>
              Excluir
            </Button>
          </>
        }
      >
        <p>
          Tem certeza que deseja excluir{" "}
          <strong style={{ color: "var(--color-text-primary)" }}>{produto.nome_produto}</strong>?
          Esta ação não pode ser desfeita.
        </p>
        {deleteError && (
          <p className="mt-3 text-sm text-rose-400">{deleteError}</p>
        )}
      </Modal>
    </div>
  );
}
