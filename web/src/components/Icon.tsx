import type { SVGProps } from "react";

const P: Record<string, string> = {
  search: "M21 21l-4.3-4.3M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z",
  shield: "M12 3l8 3v6c0 4.5-3.2 8.2-8 9-4.8-.8-8-4.5-8-9V6l8-3zM9 12l2 2 4-4",
  radar: "M12 3v9l6 3M12 21a9 9 0 110-18 9 9 0 010 18zM12 17a5 5 0 110-10 5 5 0 010 10z",
  file: "M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8l-5-5zM14 3v5h5M9 13h6M9 17h6",
  upload: "M12 16V4m0 0l-4 4m4-4l4 4M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3",
  check: "M5 12.5l4.5 4.5L19 7.5",
  checkCircle: "M12 21a9 9 0 110-18 9 9 0 010 18zM8.5 12.5l2.5 2.5 4.5-5",
  x: "M6 6l12 12M18 6L6 18",
  arrowRight: "M5 12h14m-6-6l6 6-6 6",
  arrowLeft: "M19 12H5m6-6l-6 6 6 6",
  alert: "M12 9v4m0 4h.01M10.3 3.9L2.4 18a2 2 0 001.7 3h15.8a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z",
  clock: "M12 21a9 9 0 110-18 9 9 0 010 18zM12 7v5l3 2",
  user: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 21a8 8 0 0116 0",
  map: "M9 4L3 6.5v13L9 17m0-13l6 2.5M9 4v13m6-10.5L21 4v13l-6 2.5m0-13v13",
  graph: "M6 7a2 2 0 100-4 2 2 0 000 4zM18 9a2 2 0 100-4 2 2 0 000 4zM12 21a2 2 0 100-4 2 2 0 000 4zM7.5 6.5l3.8 11M16.5 8.5l-3.8 8.5M8 5h8",
  chart: "M4 20V10m6 10V4m6 16v-7m4 7H2",
  list: "M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01",
  board: "M4 5h4v14H4zM10 5h4v9h-4zM16 5h4v6h-4z",
  link: "M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1M14 10a4 4 0 00-5.7 0l-3 3A4 4 0 0011 18.7l1-1",
  sun: "M12 17a5 5 0 100-10 5 5 0 000 10zM12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4l1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4",
  moon: "M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z",
  refresh: "M20 11a8 8 0 00-14.9-3M4 5v4h4M4 13a8 8 0 0014.9 3M20 19v-4h-4",
  external: "M14 4h6v6m0-6L10 14M18 14v5a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h5",
  logout: "M15 17l5-5-5-5M20 12H9M12 4H6a1 1 0 00-1 1v14a1 1 0 001 1h6",
  spark: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z",
  filter: "M3 5h18l-7 8v6l-4-2v-4L3 5z",
  layers: "M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5",
  play: "M8 5v14l11-7L8 5z",
  inbox: "M3 13l3-8h12l3 8v6H3v-6zM3 13h5l1 3h6l1-3h5",
  eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 15a3 3 0 100-6 3 3 0 000 6z",
  download: "M12 4v12m0 0l-4-4m4 4l4-4M4 20h16",
  print: "M7 8V4h10v4M7 17H5a1 1 0 01-1-1v-6a1 1 0 011-1h14a1 1 0 011 1v6a1 1 0 01-1 1h-2M7 14h10v6H7v-6z",
  database: "M12 8c4.4 0 8-1.3 8-3s-3.6-3-8-3-8 1.3-8 3 3.6 3 8 3zM4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
};

export type IconName = keyof typeof P;

export default function Icon({ name, size = 18, ...rest }: { name: IconName; size?: number } & SVGProps<SVGSVGElement>) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...rest}
    >
      <path d={P[name]} />
    </svg>
  );
}
