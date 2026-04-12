import { ShoppingBag, Sun, Moon, ArrowLeft, Shield, Eye } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register } from "../api/auth";
import { useTheme } from "../contexts/ThemeContext";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

export function RegisterPage() {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("As senhas não coincidem");
      return;
    }

    if (password.length < 4) {
      setError("A senha deve conter pelo menos 4 caracteres");
      return;
    }

    setIsLoading(true);
    try {
      await register({ username, password, is_admin: isAdmin });
      navigate("/login", { replace: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Erro ao criar conta";
      setError(msg);
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
      <div
        className="pointer-events-none absolute inset-0 flex items-center justify-center"
        aria-hidden
      >
        <div
          className="h-[500px] w-[500px] rounded-full opacity-10 blur-3xl"
          style={{ background: "radial-gradient(circle, #6366f1, transparent 70%)" }}
        />
      </div>

      <button
        onClick={toggleTheme}
        className="absolute top-4 right-4 rounded-lg p-2 transition-opacity hover:opacity-70 z-10"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <div className="relative z-10 w-full max-w-sm">
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
            Cadastro de nova conta
          </p>
        </div>

        <div
          className="rounded-2xl p-8 shadow-2xl relative"
          style={{
            background: "var(--color-bg-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <button
            onClick={() => navigate("/login")}
            className="absolute top-4 left-4 p-2 transition-colors hover:bg-zinc-800/60 rounded-full"
            style={{ color: "var(--color-text-secondary)" }}
            aria-label="Voltar para login"
          >
            <ArrowLeft size={18} />
          </button>

          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <Input
              id="username"
              label="Nome de Usuário"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="seu_usuario"
              required
            />
            <Input
              id="password"
              label="Senha"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
            <Input
              id="confirmPassword"
              label="Confirmar Senha"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              required
            />

            {/* Tipo de acesso */}
            <div className="pt-1">
              <p className="text-xs font-medium mb-2" style={{ color: "var(--color-text-secondary)" }}>
                Tipo de acesso
              </p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setIsAdmin(false)}
                  className="flex flex-col items-center gap-1.5 rounded-xl border p-3 text-xs font-medium transition-all"
                  style={{
                    borderColor: !isAdmin ? "var(--color-accent)" : "var(--color-border)",
                    background: !isAdmin ? "rgba(99,102,241,0.12)" : "var(--color-bg-elevated)",
                    color: !isAdmin ? "var(--color-accent)" : "var(--color-text-secondary)",
                  }}
                >
                  <Eye size={18} />
                  Visualizador
                </button>
                <button
                  type="button"
                  onClick={() => setIsAdmin(true)}
                  className="flex flex-col items-center gap-1.5 rounded-xl border p-3 text-xs font-medium transition-all"
                  style={{
                    borderColor: isAdmin ? "var(--color-accent-warn)" : "var(--color-border)",
                    background: isAdmin ? "rgba(245,158,11,0.12)" : "var(--color-bg-elevated)",
                    color: isAdmin ? "var(--color-accent-warn)" : "var(--color-text-secondary)",
                  }}
                >
                  <Shield size={18} />
                  Administrador
                </button>
              </div>
            </div>

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
              Criar Conta
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
