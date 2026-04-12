import { Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCategorias } from "../api/produtos";
import { ProdutoCard } from "../components/produtos/ProdutoCard";
import { ProdutoFilters } from "../components/produtos/ProdutoFilters";
import { EmptyState } from "../components/ui/EmptyState";
import { SkeletonCard } from "../components/ui/Loading";
import { Pagination } from "../components/ui/Pagination";
import { Button } from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";
import { useDebounce } from "../hooks/useDebounce";
import { usePagination } from "../hooks/usePagination";
import { useProdutos } from "../hooks/useProdutos";

export function CatalogoPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { page, perPage, goToPage, reset } = usePagination();

  const [searchInput, setSearchInput] = useState("");
  const [categoria, setCategoria] = useState("");
  const [sortBy, setSortBy] = useState("vendas");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [categorias, setCategorias] = useState<string[]>([]);

  const search = useDebounce(searchInput, 400);

  const { data, isLoading, error } = useProdutos({
    page,
    per_page: perPage,
    search: search || undefined,
    categoria: categoria || undefined,
    sort_by: sortBy,
    order,
  });

  useEffect(() => {
    getCategorias().then(setCategorias).catch(() => {});
  }, []);

  const handleSearchChange = (v: string) => {
    setSearchInput(v);
    reset();
  };
  const handleCategoriaChange = (v: string) => {
    setCategoria(v);
    reset();
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }, (_, i) => (
            <SkeletonCard key={`skeleton-${i}`} />
          ))}
        </div>
      );
    }
    if (data?.items.length === 0) {
      return <EmptyState />;
    }
    return (
      <>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {data?.items.map((produto) => (
            <ProdutoCard key={produto.id_produto} produto={produto} />
          ))}
        </div>
        {data && (
          <Pagination
            page={data.page}
            pages={data.pages}
            total={data.total}
            perPage={data.per_page}
            onPageChange={goToPage}
          />
        )}
      </>
    );
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: "var(--color-text-primary)" }}
          >
            Catálogo
          </h1>
          {data && (
            <p className="text-sm mt-0.5" style={{ color: "var(--color-text-secondary)" }}>
              {data.total.toLocaleString("pt-BR")} produto
              {data.total === 1 ? "" : "s"}
            </p>
          )}
        </div>
        {user?.is_admin && (
          <Button onClick={() => navigate("/produtos/novo")}>
            <Plus size={16} />
            Novo Produto
          </Button>
        )}
      </div>

      <ProdutoFilters
        search={searchInput}
        categoria={categoria}
        sortBy={sortBy}
        order={order}
        categorias={categorias}
        onSearchChange={handleSearchChange}
        onCategoriaChange={handleCategoriaChange}
        onSortByChange={(v) => { setSortBy(v); reset(); }}
        onOrderChange={(v) => { setOrder(v); reset(); }}
      />

      {error && (
        <p className="text-center text-sm text-red-400">{error}</p>
      )}

      {renderContent()}
    </div>
  );
}
