import axios from "axios";
import type {
  DashboardBundle,
  FilterOptions,
  Filters,
  MetaResponse,
  PaginatedPackages,
} from "../types";

/** Dev: Vite proxy `/api` → localhost:8000. Prod: set VITE_API_URL di Vercel. */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 120_000,
});

const dashboardApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 300_000,
});

async function withWarmupRetry<T>(fn: () => Promise<T>, attempts = 40): Promise<T> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (axios.isAxiosError(e) && e.response?.status === 503) {
        await new Promise((r) => setTimeout(r, 3000));
        continue;
      }
      if (axios.isAxiosError(e) && e.response?.status === 502 && i < attempts - 1) {
        await new Promise((r) => setTimeout(r, 5000));
        continue;
      }
      throw e;
    }
  }
  throw lastError;
}

