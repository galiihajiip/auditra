import ReactECharts from "echarts-for-react";
import { useTheme } from "../theme/ThemeContext";

const RISK_COLORS: Record<string, string> = {
  KRITIS: "#ef4444",
  TINGGI: "#f97316",
  SEDANG: "#eab308",
  RENDAH: "#3b82f6",
};

export function RiskDonut({ data }: { data: { risk_label: string; count: number }[] }) {
  const { colors, mode } = useTheme();
  const order = ["KRITIS", "TINGGI", "SEDANG", "RENDAH"];
  const sorted = [...data].sort(
    (a, b) => order.indexOf(a.risk_label) - order.indexOf(b.risk_label)
  );

  const option = {
    backgroundColor: colors.chartBg,
    tooltip: { trigger: "item", backgroundColor: colors.bgPanel, textStyle: { color: colors.textPrimary } },
    series: [
      {
        type: "pie",
        radius: ["55%", "75%"],
        label: { color: colors.textPrimary, formatter: "{b}\n{d}%" },
        data: sorted.map((d) => ({
          name: d.risk_label,
          value: d.count,
          itemStyle: { color: RISK_COLORS[d.risk_label] || "#64748b" },
        })),
      },
    ],
  };

  return <ReactECharts key={mode} option={option} style={{ height: 240, background: colors.chartBg }} notMerge />;
}

