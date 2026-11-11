import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Icon from "./Icon";
import Logo from "./Logo";

interface Props {
  isDark: boolean;
  onToggleTheme: () => void;
}

const navCls = ({ isActive }: { isActive: boolean }) => `tab-btn ${isActive ? "tab-btn-active" : ""}`;

const initials = (name: string) => name.split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase()).join("");

export default function AppHeader({ isDark, onToggleTheme }: Props) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="no-print sticky top-0 z-40 -mx-3 border-b border-[var(--border-subtle)] bg-[color-mix(in_srgb,var(--bg-page)_82%,transparent)] px-3 backdrop-blur-xl sm:-mx-4 sm:px-4">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2 sm:gap-6">
          <Link to="/" aria-label="Auditra — beranda" className="shrink-0"><Logo size="md" /></Link>
          <nav className="flex gap-1" aria-label="Navigasi utama">
            <NavLink to="/" end className={navCls}><Icon name="radar" size={16} /><span className="hidden sm:inline">Dasbor</span></NavLink>
            <NavLink to="/kasus" className={navCls}><Icon name="board" size={16} /><span className="hidden sm:inline">Penugasan</span></NavLink>
          </nav>
        </div>

        <div className="flex items-center gap-2">
          {user ? (
            <>
              <div className="hidden items-center gap-2 rounded-full border border-[var(--border)] py-1 pl-1 pr-3 sm:flex" title={user.email}>
                <span className="grid h-7 w-7 place-items-center rounded-full bg-[var(--glow)] text-xs font-bold text-[var(--accent-teal)]">{initials(user.name)}</span>
                <span className="text-sm leading-tight">
                  <span className="block font-semibold text-primary">{user.name}</span>
                  <span className="block text-xs capitalize text-muted">{user.role}</span>
                </span>
              </div>
              <button type="button" className="btn-secondary !p-2" aria-label="Keluar" title="Keluar" onClick={() => { signOut(); navigate("/"); }}>
                <Icon name="logout" size={16} />
              </button>
            </>
          ) : (
            <Link to="/masuk" className="btn-primary">Masuk</Link>
          )}
          <button type="button" onClick={onToggleTheme} className="btn-secondary !p-2" aria-label={isDark ? "Mode terang" : "Mode gelap"} title={isDark ? "Mode terang" : "Mode gelap"}>
            <Icon name={isDark ? "sun" : "moon"} size={16} />
          </button>
        </div>
      </div>
    </header>
  );
}
