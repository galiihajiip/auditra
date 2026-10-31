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

  const resetGraphVisuals = useCallback(() => {
    const nodesDs = nodesDsRef.current;
    const edgesDs = edgesDsRef.current;
    if (!nodesDs || !edgesDs) return;

    nodeBaseRef.current.forEach((base) => {
      nodesDs.update(base);
    });
    edgeMetaRef.current.forEach((e) => {
      edgesDs.update({
        id: e.id,
        color: edgeColors(colors),
        width: Math.min(4, Math.max(2, Math.log(e.weight + 1))),
      });
    });
    networkRef.current?.unselectAll();
  }, [colors]);

  const applyNodeFocus = useCallback(
    (nodeId: string | null, mode: "hover" | "select") => {
      const network = networkRef.current;
      const nodesDs = nodesDsRef.current;
      const edgesDs = edgesDsRef.current;
      if (!nodesDs || !edgesDs) return;

      if (!nodeId) {
        resetGraphVisuals();
        return;
      }

      const connectedEdges = (network?.getConnectedEdges(nodeId) ?? []) as number[];
      const focusNodes = new Set<string>([
        nodeId,
        ...((network?.getConnectedNodes(nodeId) ?? []) as string[]),
      ]);
      const focusEdgeSet = new Set(connectedEdges);
      const accentEdge = mode === "select" ? HIGH_COLOR : colors.kgEdgeHover;

      nodeBaseRef.current.forEach((base, id) => {
        if (focusNodes.has(id)) {
          const isCenter = id === nodeId;
          nodesDs.update({
            ...base,
            opacity: 1,
            borderWidth: isCenter ? 3 : 2,
            size: isCenter ? Number(base.size) * 1.1 : base.size,
          });
        } else {
          nodesDs.update(dimNodeStyle(base, colors));
        }
      });

      edgeMetaRef.current.forEach((e) => {
        if (focusEdgeSet.has(e.id)) {
          edgesDs.update({
            id: e.id,
            color: { color: accentEdge, opacity: 1, hover: accentEdge, highlight: accentEdge },
            width: mode === "select" ? 4 : 3,
          });
        } else {
          edgesDs.update({
            id: e.id,
            color: {
              color: colors.kgEdge,
              opacity: DIM_EDGE_OPACITY,
              hover: colors.kgEdgeHover,
              highlight: colors.kgEdgeHover,
            },
            width: 1,
          });
        }
      });

      if (mode === "select") {
        network?.selectNodes([nodeId]);
        network?.selectEdges(connectedEdges);
      } else {
        network?.unselectAll();
      }
    },
    [colors, resetGraphVisuals]
  );

  useEffect(() => {
    if (!ref.current || nodes.length === 0) return;

    setPhysicsOn(true);
    setSelectedId(null);
