import {
  LayoutDashboard,
  Radar,
  FolderKanban,
  AlertTriangle,
  Boxes,
  Search,
  Database,
  BellRing,
  CheckSquare,
  Briefcase,
  Share2,
  Scale,
  type LucideIcon,
} from "lucide-react";

export interface SubNavItem {
  label: string;
  href: string;
  hint: string;
  icon?: LucideIcon;
}

export interface NavItem {
  label: string;
  href: string;
  hint: string;
  icon: LucideIcon;
  subItems?: SubNavItem[];
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const navGroups: NavGroup[] = [
  {
    label: "Intelligence",
    items: [
      {
        label: "Command Center",
        href: "/command",
        hint: "National threat telemetry",
        icon: LayoutDashboard,
        subItems: [
          { label: "Investigate Threat", href: "/investigate", hint: "Multi-signal correlation bench", icon: Search },
        ],
      },
      { label: "Outbreak Radar", href: "/radar", hint: "Regional velocity spikes", icon: Radar },
      { label: "Campaigns", href: "/campaigns", hint: "Syndicate clusters", icon: FolderKanban },
      { label: "Incidents", href: "/incidents", hint: "Victim reports stream", icon: AlertTriangle },
      {
        label: "Entities",
        href: "/entities",
        hint: "VPA & phone intelligence registry",
        icon: Database,
        subItems: [
          { label: "Graph Topology", href: "/graph", hint: "Interactive cytoscape topology", icon: Share2 },
        ],
      },
      {
        label: "Enforcement Hub",
        href: "/alerts",
        hint: "Threat alerts, review triage & statutory cases",
        icon: Scale,
        subItems: [
          { label: "Alert Center", href: "/alerts", hint: "Real-time velocity spikes", icon: BellRing },
          { label: "Review Queue", href: "/review", hint: "Human-in-the-loop triage", icon: CheckSquare },
          { label: "Investigation Cases", href: "/cases", hint: "Formal statutory FIR & BSA cases", icon: Boxes },
        ],
      },
    ],
  },
  {
    label: "Management",
    items: [
      { label: "Members & Access", href: "/access", hint: "RBAC governance", icon: Database },
      { label: "Audit Log", href: "/audit", hint: "Tamper-evident logs", icon: LayoutDashboard },
    ],
  },
];

export function activeItem(pathname: string): NavItem | SubNavItem | undefined {
  for (const group of navGroups) {
    for (const item of group.items) {
      if (item.subItems) {
        for (const sub of item.subItems) {
          if (pathname === sub.href || (sub.href !== "/" && pathname.startsWith(sub.href))) {
            return sub;
          }
        }
      }
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
