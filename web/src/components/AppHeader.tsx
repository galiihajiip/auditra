import Logo from "./Logo";

const GITHUB_URL = "https://github.com/danisharizka/auditra";

interface Props {
  isDark: boolean;
  onToggleTheme: () => void;
}

export default function AppHeader({ isDark, onToggleTheme }: Props) {
  return (
    <header className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between sm:py-5">
      <h1 className="m-0 overflow-visible leading-none">
        <Logo size="md" />
      </h1>

      <div className="flex flex-wrap items-center gap-2 sm:justify-end">
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-secondary text-xs"
