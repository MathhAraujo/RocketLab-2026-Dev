import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { useAuth } from "./hooks/useAuth";
import { CatalogoPage } from "./pages/CatalogoPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ProdutoDetalhePage } from "./pages/ProdutoDetalhePage";
import { ProdutoFormPage } from "./pages/ProdutoFormPage";

function ProtectedLayout() {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Layout />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<ProtectedLayout />}>
        <Route index element={<Navigate to="/catalogo" replace />} />
        <Route path="catalogo" element={<CatalogoPage />} />
        <Route path="produtos/novo" element={<ProdutoFormPage />} />
        <Route path="produtos/:id" element={<ProdutoDetalhePage />} />
        <Route path="produtos/:id/editar" element={<ProdutoFormPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  );
}
