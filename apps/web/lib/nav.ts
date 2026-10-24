import {
  LayoutDashboard,
  Radar,
  FolderKanban,
  AlertTriangle,
  GitFork,
  Boxes,
  Search,
  FlaskConical,
  Database,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  hint: string;
  icon: LucideIcon;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const navGroups: NavGroup[] = [
  {
    label: "Intelligence",
    items: [
      { label: "Command Center", href: "/command", hint: "National threat telemetry", icon: LayoutDashboard },
      { label: "Outbreak Radar", href: "/radar", hint: "Regional velocity spikes", icon: Radar },
      { label: "Campaigns", href: "/campaigns", hint: "Syndicate clusters", icon: FolderKanban },
      { label: "Incidents", href: "/incidents", hint: "Victim reports stream", icon: AlertTriangle },
      { label: "Investigate", href: "/investigate", hint: "Multi-signal correlation bench", icon: Search },
      { label: "Knowledge Graph", href: "/graph", hint: "Interactive cytoscape canvas", icon: GitFork },
      { label: "Entities", href: "/entities", hint: "VPA & phone intelligence registry", icon: Database },
    ],
  },
  {
    label: "Operations & Enforcement",
    items: [
      { label: "Alert Center", href: "/alerts", hint: "Real-time velocity spikes", icon: AlertTriangle },
      { label: "Review Queue", href: "/review", hint: "Human-in-the-loop triage", icon: FolderKanban },
      { label: "Cases", href: "/cases", hint: "Formal statutory FIR & BSA cases", icon: Boxes },
      { label: "MuleHunter", href: "/mulehunter", hint: "Multi-hop mule tracking", icon: GitFork },
    ],
  },
  {
    label: "Management & Governance",
    items: [
      { label: "Global Search", href: "/search", hint: "1.4M node search", icon: Search },
      { label: "Saved Views", href: "/saved", hint: "Bookmarked monitors", icon: FolderKanban },
      { label: "Members & Access", href: "/access", hint: "RBAC governance", icon: Database },
      { label: "Audit Log", href: "/audit", hint: "Tamper-evident logs", icon: LayoutDashboard },
    ],
  },
];

export function activeItem(pathname: string): NavItem | undefined {
  for (const group of navGroups) {
    for (const item of group.items) {
      if (
        pathname === item.href ||
        (item.href !== "/" && pathname.startsWith(item.href)) ||
        (pathname.startsWith("/analyst") && pathname.replace(/^\/analyst/, "") === item.href)
      ) {
        return item;
      }
    }
  }
  return undefined;
}
