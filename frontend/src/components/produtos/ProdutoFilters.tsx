import { ArrowDown, ArrowUp, SlidersHorizontal } from "lucide-react";
import { formatCategoria } from "../../utils/formatters";
import { SearchBar } from "../ui/SearchBar";
import { Select } from "../ui/Select";

interface ProdutoFiltersProps {
  search: string;
  categoria: string;
  sortBy: string;
  order: "asc" | "desc";
  categorias: string[];
  onSearchChange: (v: string) => void;
  onCategoriaChange: (v: string) => void;
  onSortByChange: (v: string) => void;
  onOrderChange: (v: "asc" | "desc") => void;
}

export function ProdutoFilters({
  search,
  categoria,
  sortBy,
  order,
  categorias,
  onSearchChange,
  onCategoriaChange,
  onSortByChange,
  onOrderChange,
}: Readonly<ProdutoFiltersProps>) {
  const categoriaOptions = categorias.map((c) => ({ value: c, label: formatCategoria(c) }));
  const sortOptions = [
    { value: "vendas", label: "Vendas" },
    { value: "avaliacoes", label: "Avaliações" },
    { value: "nome_produto", label: "Nome" },
    { value: "categoria_produto", label: "Categoria" },
  ];
  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{
        background: "var(--color-bg-surface)",
        borderColor: "var(--color-border)",
      }}
    >
      {/* Search row */}
      <div className="p-3">
        <SearchBar placeholder="Buscar produto..." initialValue={search} onSearch={onSearchChange} />
      </div>

      {/* Divider + filters row */}
      <div
        className="flex items-center gap-3 px-3 py-2.5"
        style={{ borderTop: "1px solid var(--color-border)", background: "var(--color-bg-base)" }}
      >
        <div className="flex items-center gap-1.5 shrink-0" style={{ color: "var(--color-text-muted)" }}>
          <SlidersHorizontal size={13} />
          <span className="text-xs font-medium hidden sm:inline" style={{ color: "var(--color-text-muted)" }}>
            Filtros
          </span>
        </div>

        <div
          className="w-px h-4 shrink-0"
          style={{ background: "var(--color-border)" }}
        />

        <div className="flex flex-wrap gap-2 flex-1">
          <Select
            value={categoria}
            options={categoriaOptions}
            placeholder="Todas as categorias"
            onChange={(e) => onCategoriaChange(e.target.value)}
            className="min-w-[160px] !py-1.5 text-xs"
          />
          <div className="flex items-center gap-1">
            <Select
              value={sortBy}
              options={sortOptions}
              onChange={(e) => onSortByChange(e.target.value)}
              className="min-w-[120px] !py-1.5 text-xs !rounded-r-none"
            />
            <button
              type="button"
              onClick={() => onOrderChange(order === "desc" ? "asc" : "desc")}
              className="flex items-center justify-center rounded-l-none rounded-r-lg border px-2.5 transition-colors hover:border-indigo-500 hover:text-indigo-400"
              style={{
                height: "30px",
                background: "var(--color-bg-elevated)",
                borderColor: "var(--color-border)",
                color: "var(--color-text-primary)",
              }}
            >
              {order === "desc" ? <ArrowDown size={14} /> : <ArrowUp size={14} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
