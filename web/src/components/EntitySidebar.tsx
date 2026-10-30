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

