import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="panel mx-auto max-w-lg text-center">
      <h2 className="text-lg font-bold text-primary">Halaman tidak ditemukan</h2>
      <p className="mt-1 text-sm text-muted">Alamat yang Anda buka tidak ada.</p>
      <Link to="/" className="btn-primary mt-4 inline-block text-sm">Kembali ke dasbor</Link>
    </div>
  );
}
