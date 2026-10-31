import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { DataSet } from "vis-data";
import { Network } from "vis-network";
import ColorLegend from "./ColorLegend";
import { useTheme } from "../theme/ThemeContext";
import { formatNodeLabel, formatRelation, isHighRisk, nodeTypeLabel } from "../utils/kgLabels";

interface Props {
  nodes: Record<string, unknown>[];
  edges: Record<string, unknown>[];
}

interface EdgeMeta {
  id: number;
  from: string;
  to: string;
  relation: string;
  weight: number;
}

interface ConnectionRow {
  direction: "keluar" | "masuk";
  peerLabel: string;
  peerType: string;
  relation: string;
  weight: number;
}

const HIGH_COLOR = "#f97316";
const LOW_COLOR = "#3b82f6";
const DIM_NODE_OPACITY = 0.1;
const DIM_EDGE_OPACITY = 0.05;

function edgeColors(colors: { kgEdge: string; kgEdgeHover: string }) {
  return {
    color: colors.kgEdge,
    opacity: 0.85,
    hover: colors.kgEdgeHover,
    highlight: colors.kgEdgeHover,
  };
}

function dimNodeStyle(base: Record<string, unknown>, colors: { kgLabel: string }) {
  const high = Boolean(base._high);
  return {
    id: base.id,
    color: {
      background: high ? "rgba(249,115,22,0.18)" : "rgba(59,130,246,0.18)",
      border: high ? "rgba(194,65,12,0.22)" : "rgba(29,78,216,0.22)",
    },
    font: {
      ...(base.font as object),
      color: colors.kgLabel,
      strokeWidth: 2,
      background: "transparent",
    },
    borderWidth: 1,
    size: Math.max(10, Number(base.size) * 0.82),
    opacity: DIM_NODE_OPACITY,
  };
}

