import { LayoutDashboard, LayoutGrid, PackagePlus, Sun, Moon, LogOut, X } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../contexts/ThemeContext";

interface SidebarProps {
  isOpen: boolean;
  isExpanded: boolean;
  onClose: () => void;
  onExpandChange: (expanded: boolean) => void;
}

const navItems = [
  { to: "/catalogo", icon: LayoutGrid, label: "Catálogo", adminOnly: false },
  { to: "/produtos/novo", icon: PackagePlus, label: "Novo Produto", adminOnly: true },
];

export function Sidebar({ isOpen, isExpanded, onClose, onExpandChange }: Readonly<SidebarProps>) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div
        className="flex h-14 items-center overflow-hidden shrink-0"
        style={{ borderBottom: "1px solid var(--color-border)" }}
      >
        <div className="flex w-14 shrink-0 items-center justify-center">
          <LayoutDashboard size={20} className="text-indigo-500" />
        </div>
        {isExpanded && (
          <span
            className="whitespace-nowrap text-base font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: "var(--color-text-primary)" }}
          >
            Mercadão
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 p-2 flex-1 overflow-hidden">
        {/* Dashboard — disabled placeholder */}
        <div
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 cursor-not-allowed opacity-40"
          title={isExpanded ? undefined : "Dashboard (Em breve)"}
        >
          <LayoutDashboard size={18} className="shrink-0" style={{ color: "var(--color-text-secondary)" }} />
          {isExpanded && (
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm font-medium truncate" style={{ color: "var(--color-text-secondary)" }}>
                Dashboard
              </span>
              <span className="rounded px-1 py-0.5 text-[10px] font-medium bg-zinc-700 text-zinc-400 shrink-0">
                Em breve
              </span>
            </div>
          )}
        </div>

        {navItems.filter(item => !item.adminOnly || user?.is_admin).map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            title={isExpanded ? undefined : label}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors
              ${isActive
                ? "border-l-2 border-indigo-500 text-indigo-400 pl-[10px]"
                : "border-l-2 border-transparent hover:bg-zinc-800/60"
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? "rgba(99,102,241,0.12)" : undefined,
              color: isActive ? "#818cf8" : "var(--color-text-secondary)",
            })}
          >
            <Icon size={18} className="shrink-0" />
            {isExpanded && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div
        className="flex flex-col gap-1 p-2 shrink-0"
        style={{ borderTop: "1px solid var(--color-border)" }}
      >
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          title={theme === "dark" ? "Modo claro" : "Modo escuro"}
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors hover:bg-zinc-800/60"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {theme === "dark"
            ? <Sun size={18} className="shrink-0" />
            : <Moon size={18} className="shrink-0" />
          }
          {isExpanded && (
            <span className="truncate">
              {theme === "dark" ? "Modo claro" : "Modo escuro"}
            </span>
          )}
        </button>

        {/* User + logout */}
        {user && (
          <button
            onClick={handleLogout}
            title={isExpanded ? undefined : `Sair (${user.username})`}
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors hover:bg-rose-500/10 hover:text-rose-400"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <LogOut size={18} className="shrink-0" />
            {isExpanded && (
              <span className="truncate">{user.username}</span>
            )}
          </button>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          role="presentation"
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={onClose}
          onKeyDown={(e) => e.key === "Escape" && onClose()}
        />
      )}

      {/* Mobile drawer */}
      <aside
        className={`fixed top-0 left-0 z-30 h-full w-[220px] lg:hidden transition-transform duration-200
          ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
        style={{
          background: "var(--color-bg-surface)",
          borderRight: "1px solid var(--color-border)",
        }}
      >
        <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: "1px solid var(--color-border)" }}>
          <span
            className="text-base font-bold"
            style={{ fontFamily: "'Outfit', sans-serif", color: "var(--color-text-primary)" }}
          >
            Mercadão
          </span>
          <button onClick={onClose} style={{ color: "var(--color-text-secondary)" }}>
            <X size={18} />
          </button>
        </div>
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside
        className={`hidden lg:flex fixed top-0 left-0 z-20 h-full flex-col transition-all duration-200
          ${isExpanded ? "w-[220px]" : "w-14"}`}
        style={{
          background: "var(--color-bg-surface)",
          borderRight: "1px solid var(--color-border)",
        }}
        onMouseEnter={() => onExpandChange(true)}
        onMouseLeave={() => onExpandChange(false)}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
