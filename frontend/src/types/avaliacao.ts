export interface AvaliacaoItem {
  id_avaliacao: string;
  avaliacao: number;
  titulo_comentario: string | null;
  comentario: string | null;
  data_comentario: string | null;
  resposta_admin: string | null;
  autor_resposta: string | null;
  data_resposta: string | null;
}

export interface AvaliacaoStats {
  avaliacao_media: number | null;
  total_avaliacoes: number;
  distribuicao: Record<number, number>;
  avaliacoes: AvaliacaoItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
