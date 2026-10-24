import { useState, type ReactNode } from "react";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { Button } from "./Button";

/** Mobile navigation drawer. */
export interface MobileNavProps {
  children: ReactNode;
  className?: string;
}

export function MobileNav({ children, className }: MobileNavProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Mobile nav button — visible only on small screens */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={() => setOpen(!open)}
        aria-label={open ? "Close menu" : "Open menu"}
      >
        {open ? (
          <X className="h-5 w-5" />
        ) : (
          <Menu className="h-5 w-5" />
        )}
      </Button>

      {/* Drawer overlay and content */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/40 z-30 md:hidden"
            onClick={() => setOpen(false)}
            aria-hidden
          />

          {/* Drawer panel */}
          <nav
            className={cn(
              "fixed left-0 top-0 bottom-0 w-56 bg-surface-1 border-r border-border",
              "z-40 overflow-y-auto md:hidden animate-rise-in",
              className,
            )}
          >
            <div className="pt-14"> {/* Offset for top nav */}
              {children}
            </div>
          </nav>
        </>
      )}
    </>
  );
}
