import type { AvaliacaoItem, AvaliacaoStats } from "../types/avaliacao";
import type { PaginatedResponse } from "../types/pagination";
import type {
  Produto,
  ProdutoCreate,
  ProdutoListItem,
  ProdutoUpdate,
} from "../types/produto";
import type { VendaStats } from "../types/venda";
import api from "./client";

export interface ProdutosParams {
  page?: number;
  per_page?: number;
  search?: string;
  categoria?: string;
  sort_by?: string;
  order?: "asc" | "desc";
}

export async function getProdutos(
  params: ProdutosParams = {}
): Promise<PaginatedResponse<ProdutoListItem>> {
  const response = await api.get<PaginatedResponse<ProdutoListItem>>(
    "/produtos",
    { params }
  );
  return response.data;
}

export async function getProduto(id: string): Promise<Produto> {
  const response = await api.get<Produto>(`/produtos/${id}`);
  return response.data;
}

export async function getVendas(id: string): Promise<VendaStats> {
  const response = await api.get<VendaStats>(`/produtos/${id}/vendas`);
  return response.data;
}

export async function getAvaliacoes(
  id: string,
  params: { page?: number; per_page?: number } = {}
): Promise<AvaliacaoStats> {
  const response = await api.get<AvaliacaoStats>(
    `/produtos/${id}/avaliacoes`,
    { params }
  );
  return response.data;
}

export async function getCategorias(): Promise<string[]> {
  const response = await api.get<string[]>("/produtos/categorias");
  return response.data;
}

export async function createProduto(data: ProdutoCreate): Promise<Produto> {
  const response = await api.post<Produto>("/produtos", data);
  return response.data;
}

export async function updateProduto(
  id: string,
  data: ProdutoUpdate
): Promise<Produto> {
  const response = await api.put<Produto>(`/produtos/${id}`, data);
  return response.data;
}

export async function deleteProduto(id: string): Promise<void> {
  await api.delete(`/produtos/${id}`);
}

export async function responderAvaliacao(
  idAvaliacao: string,
  resposta: string
): Promise<AvaliacaoItem> {
  const response = await api.post<AvaliacaoItem>(
    `/produtos/avaliacoes/${idAvaliacao}/resposta`,
    { resposta }
  );
  return response.data;
}

export async function deleteRespostaAvaliacao(
  idAvaliacao: string
): Promise<AvaliacaoItem> {
  const response = await api.delete<AvaliacaoItem>(
    `/produtos/avaliacoes/${idAvaliacao}/resposta`
  );
  return response.data;
}
