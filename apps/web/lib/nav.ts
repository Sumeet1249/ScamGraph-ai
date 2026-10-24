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
    ],
  },
  {
    label: "Investigations",
    items: [
      { label: "Campaigns", href: "/campaigns", hint: "Syndicate clusters", icon: FolderKanban },
      { label: "Incidents", href: "/incidents", hint: "Victim reports stream", icon: AlertTriangle },
      { label: "Knowledge Graph", href: "/graph", hint: "Interactive cytoscape canvas", icon: GitFork },
      { label: "MuleHunter", href: "/mulehunter", hint: "Multi-hop mule tracking", icon: Boxes },
    ],
  },
  {
    label: "Operations & Lab",
    items: [
      { label: "Investigate", href: "/investigate", hint: "Multi-signal correlation", icon: Search },
      { label: "Simulator Lab", href: "/lab", hint: "Synthetic outbreak simulator", icon: FlaskConical },
      { label: "Registry", href: "/registry", hint: "Mule & entity registry", icon: Database },
    ],
  },
];

export function activeItem(pathname: string): NavItem | undefined {
  for (const group of navGroups) {
    for (const item of group.items) {
      if (pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))) {
        return item;
      }
    }
  }
  return undefined;
}
