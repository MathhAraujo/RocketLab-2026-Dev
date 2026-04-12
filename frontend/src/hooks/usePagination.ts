import { useState } from "react";
import { DEFAULT_PAGE_SIZE } from "../utils/constants";

export function usePagination(initialPage = 1, initialPerPage = DEFAULT_PAGE_SIZE) {
  const [page, setPage] = useState(initialPage);
  const perPage = initialPerPage;

  const goToPage = (p: number) => setPage(p);
  const reset = () => setPage(1);

  return { page, perPage, goToPage, reset };
}
