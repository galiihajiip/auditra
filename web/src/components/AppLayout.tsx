import { useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { useTheme } from "../theme/ThemeContext";
import AppHeader from "./AppHeader";
import SiteFooter from "./SiteFooter";

export default function AppLayout() {
  const { toggle, isDark } = useTheme();
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo({ top: 0 }); }, [pathname]);
  return (
    <div className="app-shell pb-10">
      <div className="mx-auto max-w-[1400px] px-3 sm:px-4">
        <AppHeader isDark={isDark} onToggleTheme={toggle} />
        <main className="pt-6"><Outlet /></main>
        <SiteFooter />
      </div>
    </div>
  );
}
