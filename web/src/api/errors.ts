import axios from "axios";

const configuredApiUrl = import.meta.env.VITE_API_URL as string | undefined;

export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === "ECONNABORTED") {
      return "Permintaan ke API habis waktu (query berat). Tunggu sebentar lalu muat ulang halaman.";
    }
    if (error.response?.status === 503) {
      const detail = error.response.data?.detail;
      if (typeof detail === "string") return detail;
    }
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      return typeof detail === "string" ? detail : JSON.stringify(detail);
    }
