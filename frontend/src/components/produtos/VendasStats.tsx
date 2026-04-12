import type { VendaStats } from "../../types/venda";
import { formatCurrency, formatNumber } from "../../utils/formatters";

interface VendasStatsProps {
  stats: VendaStats;
}

const STATUS_COLORS: Record<string, string> = {
  entregue: "bg-green-500",
  enviado: "bg-blue-500",
  aprovado: "bg-violet-500",
  processando: "bg-yellow-500",
  cancelado: "bg-red-500",
};

export function VendasStats({ stats }: Readonly<VendasStatsProps>) {
  const totalStatus = Object.values(stats.vendas_por_status).reduce(
    (a, b) => a + b,
    0
  );

  const metricCards = [
    { label: "Total de Vendas", value: formatNumber(stats.total_vendas) },
    { label: "Receita Total", value: formatCurrency(stats.receita_total) },
    { label: "Preço Médio", value: formatCurrency(stats.preco_medio) },
    { label: "Preço Mínimo", value: formatCurrency(stats.preco_minimo) },
    { label: "Preço Máximo", value: formatCurrency(stats.preco_maximo) },
    { label: "Pedidos", value: formatNumber(stats.total_pedidos) },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {metricCards.map(({ label, value }) => (
          <div
            key={label}
            className="rounded-xl border p-4 text-center"
            style={{
              background: "var(--color-bg-surface)",
              borderColor: "var(--color-border)",
            }}
          >
            <p className="mb-1 text-xs" style={{ color: "var(--color-text-secondary)" }}>
              {label}
            </p>
            <p className="text-sm font-bold" style={{ color: "var(--color-accent)" }}>
              {value}
            </p>
          </div>
        ))}
      </div>

      <div>
        <p className="mb-3 text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
          Vendas por status
        </p>
        <div className="space-y-2">
          {Object.keys(STATUS_COLORS).map((status) => {
            const qty = stats.vendas_por_status[status] || 0;
            const pct = totalStatus > 0 ? (qty / totalStatus) * 100 : 0;
            return (
              <div key={status} className="flex items-center gap-3 text-sm">
                <span
                  className="w-28 capitalize shrink-0"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {status}
                </span>
                <div
                  className="flex-1 rounded-full h-2 overflow-hidden"
                  style={{ background: "var(--color-bg-elevated)" }}
                >
                  <div
                    className={`h-full rounded-full transition-all ${STATUS_COLORS[status] ?? "bg-zinc-500"}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span
                  className="w-8 text-right shrink-0"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {formatNumber(qty)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
