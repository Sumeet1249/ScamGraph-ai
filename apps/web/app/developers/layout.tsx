import type { ReactNode } from "react";
import { DeveloperNav } from "@/components/shell/DeveloperNav";
import { DeveloperFooter } from "@/components/shell/DeveloperFooter";

export default function DevelopersLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-ground text-on-surface">
      <DeveloperNav />
      <main className="flex-1 w-full bg-ground">{children}</main>
      <DeveloperFooter />
    </div>
  );
}
