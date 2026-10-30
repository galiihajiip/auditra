import {
  createContext,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type ThemeMode = "dark" | "light";

export interface ThemeColors {
  bgPage: string;
  bgPanel: string;
  bgPanel2: string;
  border: string;
  textPrimary: string;
  textMuted: string;
  accentBlue: string;
  accentOrange: string;
  kgCanvas: string;
  kgLabel: string;
  kgLabelBg: string;
  kgLabelStroke: string;
  kgEdge: string;
  kgEdgeHover: string;
  chartText: string;
  chartGrid: string;
  chartBg: string;
  selectBg: string;
}

