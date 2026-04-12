import { ShoppingBag, Sun, Moon } from "lucide-react";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../contexts/ThemeContext";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

export function LoginPage() {
  const { user, login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (user) return <Navigate to="/catalogo" replace />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await login({ username, password });
      navigate("/catalogo", { replace: true });
    } catch {
      setError("Usuário ou senha inválidos");
      setPassword("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="relative flex min-h-screen items-center justify-center p-4"
      style={{
        background: "var(--color-bg-base)",
        backgroundImage: `
          linear-gradient(var(--color-border) 1px, transparent 1px),
          linear-gradient(90deg, var(--color-border) 1px, transparent 1px)
        `,
        backgroundSize: "32px 32px",
      }}
    >
      {/* Glow central */}
      <div
        className="pointer-events-none absolute inset-0 flex items-center justify-center"
        aria-hidden
      >
        <div
          className="h-[500px] w-[500px] rounded-full opacity-10 blur-3xl"
          style={{ background: "radial-gradient(circle, #6366f1, transparent 70%)" }}
        />
      </div>

      {/* Theme toggle */}
      <button
        onClick={toggleTheme}
        className="absolute top-4 right-4 rounded-lg p-2 transition-colors hover:bg-zinc-800/60 z-10"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <div className="relative z-10 w-full max-w-sm">
        {/* Brand */}
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="rounded-2xl bg-indigo-500/15 p-4">
            <ShoppingBag size={40} className="text-indigo-400" />
          </div>
          <h1
            className="text-3xl font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: "var(--color-text-primary)" }}
          >
            Mercadão
          </h1>
          <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
            Painel administrativo
          </p>
        </div>

        {/* Card */}
        <div
          className="rounded-2xl p-8 shadow-2xl"
          style={{
            background: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              id="username"
              label="Usuário"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              autoComplete="username"
              required
            />
            <Input
              id="password"
              label="Senha"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
            {error && (
              <p
                className="rounded-lg px-3 py-2 text-sm"
                style={{
                  background: "rgba(244,63,94,0.1)",
                  border: "1px solid rgba(244,63,94,0.3)",
                  color: "#f43f5e",
                }}
              >
                {error}
              </p>
            )}
            <Button type="submit" isLoading={isLoading} className="w-full mt-2">
              Entrar
            </Button>
            <div className="mt-4 flex flex-col items-center gap-2 text-sm pt-2" style={{ color: "var(--color-text-secondary)" }}>
              <p>Ainda não tem uma conta?</p>
              <button
                type="button"
                onClick={() => navigate("/register")}
                className="font-medium text-indigo-400 transition-colors hover:text-indigo-300 hover:underline"
              >
                Criar uma nova conta
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
