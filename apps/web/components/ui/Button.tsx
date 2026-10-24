import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils/cn";

type Variant = "primary" | "secondary" | "outline" | "ghost" | "danger" | "success";
type Size = "sm" | "md" | "lg" | "icon";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  /** Shows a spinner and disables interaction. */
  loading?: boolean;
  /** Leading icon (after loading spinner if loading). */
  leadingIcon?: ReactNode;
  /** Trailing icon. */
  trailingIcon?: ReactNode;
}

const variantMap: Record<Variant, string> = {
  primary: "sg-btn--primary",
  secondary: "sg-btn--secondary",
  outline: "sg-btn--secondary",
  ghost: "sg-btn--ghost",
  danger: "sg-btn--danger",
  success: "sg-btn--primary bg-success text-on-brand hover:brightness-110",
};

const sizeMap: Record<Size, string> = {
  sm: "sg-btn--sm",
  md: "",
  lg: "sg-btn--lg",
  icon: "sg-btn--icon",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = "secondary",
    size = "md",
    loading = false,
    leadingIcon,
    trailingIcon,
    className,
    type = "button",
    disabled,
    children,
    ...props
  },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      aria-busy={loading ? "true" : undefined}
      className={cn(
        "sg-btn rounded-full btn-pop",
        variantMap[variant],
        sizeMap[size],
        loading && "is-loading",
        className,
      )}
      {...props}
    >
      {leadingIcon}
      {size !== "icon" && <span>{children}</span>}
      {size !== "icon" && trailingIcon}
    </button>
  );
});
