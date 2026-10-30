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
