import { MessageSquareReply, Send, X, Trash2 } from "lucide-react";
import { useState } from "react";
import { responderAvaliacao, deleteRespostaAvaliacao } from "../../api/produtos";
import { useAuth } from "../../hooks/useAuth";
import type { AvaliacaoItem, AvaliacaoStats } from "../../types/avaliacao";
import { formatDate } from "../../utils/formatters";
import { Pagination } from "../ui/Pagination";
import { StarRating } from "../ui/StarRating";

interface AvaliacoesListProps {
  stats: AvaliacaoStats;
  onPageChange: (page: number) => void;
  onRespostaPublicada: (av: AvaliacaoItem) => void;
}

function RespostaInline({
  idAvaliacao,
  onSalvar,
  onCancelar,
}: {
  idAvaliacao: string;
  onSalvar: (av: AvaliacaoItem) => void;
  onCancelar: () => void;
}) {
  const [texto, setTexto] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [erro, setErro] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!texto.trim()) return;
    setIsLoading(true);
    setErro("");
    try {
      const resultado = await responderAvaliacao(idAvaliacao, texto.trim());
      onSalvar(resultado);
    } catch {
      setErro("Erro ao publicar resposta. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-3 pt-3" style={{ borderTop: "1px solid var(--color-border)" }}>
      <textarea
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Escreva sua resposta..."
        rows={2}
        className="w-full resize-none rounded-lg px-3 py-2 text-sm outline-none transition-colors"
        style={{
          background: "var(--color-bg-base)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-primary)",
        }}
        required
      />
      {erro && <p className="mt-1 text-xs text-red-400">{erro}</p>}
      <div className="mt-2 flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancelar}
          className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors hover:bg-zinc-700/50"
          style={{ color: "var(--color-text-secondary)" }}
        >
          <X size={13} />
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading || !texto.trim()}
          className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50"
          style={{
            background: "rgba(99,102,241,0.15)",
            color: "#818cf8",
            border: "1px solid rgba(99,102,241,0.3)",
          }}
        >
          <Send size={13} />
          {isLoading ? "Publicando..." : "Publicar"}
        </button>
      </div>
    </form>
  );
}

export function AvaliacoesList({ stats, onPageChange, onRespostaPublicada }: Readonly<AvaliacoesListProps>) {
  const { user } = useAuth();
  const [respondendoId, setRespondendoId] = useState<string | null>(null);

  if (stats.avaliacoes.length === 0) {
    return (
      <p className="py-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Nenhuma avaliação encontrada.
      </p>
    );
  }

  const handleSalvar = (av: AvaliacaoItem) => {
    setRespondendoId(null);
    onRespostaPublicada(av);
  };

  return (
    <div className="space-y-4">
      {stats.avaliacoes.map((av) => (
        <div
          key={av.id_avaliacao}
          className="rounded-xl border p-4"
          style={{
            background: "var(--color-bg-surface)",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="mb-2 flex items-center justify-between">
            <StarRating rating={av.avaliacao} size={14} />
            <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
              {formatDate(av.data_comentario)}
            </span>
          </div>
          {av.titulo_comentario && av.titulo_comentario !== "Sem titulo" && (
            <p className="mb-1 text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>
              {av.titulo_comentario}
            </p>
          )}
          {av.comentario && av.comentario !== "Sem comentario" && (
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              {av.comentario}
            </p>
          )}

          {/* Resposta existente */}
          {av.resposta_admin && (
            <div
              className="mt-3 rounded-lg p-3 group relative"
              style={{
                background: "rgba(99,102,241,0.07)",
                border: "1px solid rgba(99,102,241,0.2)",
              }}
            >
              <div className="flex justify-between items-start">
                <p className="mb-1 text-xs font-semibold" style={{ color: "#818cf8" }}>
                  {av.autor_resposta} · {formatDate(av.data_resposta)}
                </p>
                {user?.is_admin && (
                  <button
                    onClick={async () => {
                      if (!confirm("Deseja excluir esta resposta?")) return;
                      try {
                        const atualizada = await deleteRespostaAvaliacao(av.id_avaliacao);
                        onRespostaPublicada(atualizada);
                      } catch (e) {
                        alert("Erro ao excluir resposta.");
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-400"
                    style={{ color: "var(--color-text-secondary)" }}
                    title="Excluir resposta"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
              <p className="text-sm" style={{ color: "var(--color-text-primary)" }}>
                {av.resposta_admin}
              </p>
            </div>
          )}

          {/* Formulário inline ou botão de responder */}
          {user?.is_admin && (
            respondendoId === av.id_avaliacao ? (
              <RespostaInline
                idAvaliacao={av.id_avaliacao}
                onSalvar={handleSalvar}
                onCancelar={() => setRespondendoId(null)}
              />
            ) : (
              !av.resposta_admin && (
                <div className="mt-2 flex justify-end">
                  <button
                    onClick={() => setRespondendoId(av.id_avaliacao)}
                    className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors hover:bg-indigo-500/10"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    <MessageSquareReply size={13} />
                    Responder
                  </button>
                </div>
              )
            )
          )}
        </div>
      ))}

      <Pagination
        page={stats.page}
        pages={stats.pages}
        total={stats.total}
        perPage={stats.per_page}
        onPageChange={onPageChange}
      />
    </div>
  );
}
