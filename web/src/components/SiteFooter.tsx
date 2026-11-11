import { Link } from "react-router-dom";

const SIRUP_URL = "https://sirup.inaproc.id/sirup/caripaketctr/index";
const GITHUB_URL = "https://github.com/danisharizka/auditra";

export default function SiteFooter() {
  return (
    <footer className="no-print mt-14 flex flex-col gap-3 border-t border-[var(--border-subtle)] py-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="font-display font-bold text-primary">Auditra</p>
        <p>Prioritas audit pengadaan publik berbasis Knowledge Graph · Tim SD2026020000253</p>
        <p className="text-xs">Universitas Pembangunan Nasional Veteran Jawa Timur · Dani Shofi Nur Izza, Danisha Rizka Hapsari, Galih Aji Pangestu</p>
      </div>
      <div className="flex gap-4">
        <Link className="underline-offset-4 hover:text-primary hover:underline" to="/metodologi">Dasar metodologi</Link>
        <a className="underline-offset-4 hover:text-primary hover:underline" href={SIRUP_URL} target="_blank" rel="noopener noreferrer">Data: SIRUP LKPP</a>
        <a className="underline-offset-4 hover:text-primary hover:underline" href={GITHUB_URL} target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
    </footer>
  );
}
