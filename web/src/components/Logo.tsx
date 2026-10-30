interface Props {
  showWordmark?: boolean;
  size?: "sm" | "md" | "lg";
}

const iconSizes = {
  sm: "h-9 w-9",
  md: "h-10 w-10",
  lg: "h-12 w-12",
};

const textSizes = {
  sm: "text-sm tracking-[0.18em]",
  md: "text-base tracking-[0.2em] sm:text-lg",
  lg: "text-lg tracking-[0.22em] sm:text-xl",
};

