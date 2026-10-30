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

