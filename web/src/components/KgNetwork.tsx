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

function buildKgSummary(nodes: Record<string, unknown>[], edges: Record<string, unknown>[]): string {
  const lembaga = nodes.filter((n) => n.node_type === "lembaga").length;
  const satker = nodes.filter((n) => n.node_type === "satker").length;
  const high = nodes.filter((n) => isHighRisk(n.avg_rpi)).length;
  const low = nodes.length - high;

  const top = [...nodes]
    .filter((n) => n.node_type === "lembaga")
    .sort((a, b) => Number(b.risk_influence ?? 0) - Number(a.risk_influence ?? 0))
    .slice(0, 2)
    .map((n) => formatNodeLabel(n.label, n.node_type))
    .join(" & ");

  return [
    `Graf ini menampilkan ${lembaga} lembaga dan ${satker} satker yang saling terhubung melalui ${edges.length} relasi pengadaan.`,
    `Node oranye (${high}): rata-rata RPI ≥ 30 (prioritas audit). Node biru (${low}): RPI di bawah ambang.`,
    top
      ? `Lembaga dengan pengaruh risiko tertinggi dalam subgraf: ${top}.`
      : "",
    "Arahkan kursor ke node untuk sorot relasi · klik untuk panel detail (keluar ↑ / masuk ↓).",
  ]
    .filter(Boolean)
    .join(" ");
}

export default function KgNetwork({ nodes, edges }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);
  const nodesDsRef = useRef<DataSet<Record<string, unknown>> | null>(null);
  const edgesDsRef = useRef<DataSet<Record<string, unknown>> | null>(null);
  const nodeMapRef = useRef<Map<string, Record<string, unknown>>>(new Map());
  const edgeMetaRef = useRef<EdgeMeta[]>([]);
  const nodeBaseRef = useRef<Map<string, Record<string, unknown>>>(new Map());
  const selectedIdRef = useRef<string | null>(null);
  const { colors } = useTheme();
  const [physicsOn, setPhysicsOn] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    selectedIdRef.current = selectedId;
  }, [selectedId]);

  const summary = useMemo(() => buildKgSummary(nodes, edges), [nodes, edges]);

  const selectedNode = useMemo(
    () => (selectedId ? nodes.find((n) => String(n.node_id) === selectedId) : null),
    [selectedId, nodes]
  );

  const connections = useMemo((): ConnectionRow[] => {
    if (!selectedId || !selectedNode) return [];

    const nodeMap = new Map(nodes.map((n) => [String(n.node_id), n]));

    const rows: ConnectionRow[] = [];
    for (const e of edgeMetaRef.current) {
      if (e.from === selectedId) {
        const peer = nodeMap.get(e.to);
        rows.push({
          direction: "keluar",
          peerLabel: formatNodeLabel(peer?.label, peer?.node_type),
          peerType: nodeTypeLabel(peer?.node_type),
          relation: formatRelation(e.relation),
          weight: e.weight,
        });
      } else if (e.to === selectedId) {
        const peer = nodeMap.get(e.from);
        rows.push({
          direction: "masuk",
          peerLabel: formatNodeLabel(peer?.label, peer?.node_type),
          peerType: nodeTypeLabel(peer?.node_type),
          relation: formatRelation(e.relation),
          weight: e.weight,
        });
      }
    }
    return rows.sort((a, b) => b.weight - a.weight).slice(0, 12);
  }, [selectedId, selectedNode, nodes, edges]);

