import { useEffect, useMemo, useState } from "react";
import { formatPaguCompact } from "../utils/formatPagu";
import type { RankRow } from "../types";

type SortKey = "rpi" | "pagu";

const INITIAL_VISIBLE = 8;
const EXPANDED_MAX_HEIGHT = 360;

interface Props {
  data: RankRow[];
  selectedLembaga?: string;
  onSelect: (lembaga: string) => void;
}

export default function EntitySidebar({ data, selectedLembaga, onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortKey>("rpi");
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    setExpanded(false);
  }, [query, sortBy]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let rows = q
      ? data.filter((r) => (r.lembaga || "").toLowerCase().includes(q))
      : [...data];

    rows.sort((a, b) => {
      if (sortBy === "pagu") {
        return (b.total_pagu_miliar ?? 0) - (a.total_pagu_miliar ?? 0);
      }
      return b.avg_rpi - a.avg_rpi;
    });
    return rows;
  }, [data, query, sortBy]);

  const visibleRows = expanded ? filtered : filtered.slice(0, INITIAL_VISIBLE);
  const hiddenCount = Math.max(0, filtered.length - INITIAL_VISIBLE);

  return (
    <div className="flex flex-col">
      <div className="mb-2 flex gap-2">
        <button
          type="button"
          className={`tab-btn ${sortBy === "rpi" ? "tab-btn-active" : ""}`}
          onClick={() => setSortBy("rpi")}
        >
          By RPI
        </button>
        <button
          type="button"
          className={`tab-btn ${sortBy === "pagu" ? "tab-btn-active" : ""}`}
          onClick={() => setSortBy("pagu")}
        >
          By Pagu
        </button>
        <span className="ml-auto self-center text-[10px] text-muted">
          {filtered.length} lembaga
        </span>
      </div>

      <div className="relative mb-2">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs text-muted">
          🔍
        </span>
        <input
          type="search"
          className="input-select pl-8"
          placeholder="Cari lembaga…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      <div
        className={`entity-list pr-1 ${expanded ? "entity-list-expanded" : ""}`}
        style={expanded ? { maxHeight: EXPANDED_MAX_HEIGHT } : undefined}
      >
        {filtered.length === 0 && (
