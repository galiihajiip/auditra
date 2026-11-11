import { Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import RequireAuth from "./components/RequireAuth";
import CasePage from "./pages/CasePage";
import CasesPage from "./pages/CasesPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";
import MethodologyPage from "./pages/MethodologyPage";
import PackagePage from "./pages/PackagePage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="paket/:id" element={<PackagePage />} />
        <Route path="metodologi" element={<MethodologyPage />} />
        <Route path="masuk" element={<LoginPage />} />
        <Route path="kasus" element={<RequireAuth><CasesPage /></RequireAuth>} />
        <Route path="kasus/:id" element={<RequireAuth><CasePage /></RequireAuth>} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
