import {
  ShieldCheck,
  Search,
  Radio,
  Layers,
  GitFork,
  Network,
  Database,
  Activity,
  FlaskConical,
  AlertOctagon,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  hint?: string;
  icon: LucideIcon;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const navGroups: NavGroup[] = [
  {
    label: "Detection & Shield",
    items: [
      {
        href: "/shield",
        label: "Shield Hub",
        hint: "Unified multi-modal protection center",
        icon: ShieldCheck,
      },
      {
        href: "/investigate",
        label: "Investigate",
        hint: "Analyze messages, URLs, calls, and UPI QR",
        icon: Search,
      },
      {
        href: "/radar",
        label: "Campaign Radar",
        hint: "Early outbreak & emerging cluster radar",
        icon: Radio,
      },
    ],
  },
  {
    label: "Intelligence & Graph",
    items: [
      {
        href: "/incidents",
        label: "Incidents",
        hint: "Reconstructed scam journeys and triaged cases",
        icon: AlertOctagon,
      },
      {
        href: "/campaigns",
        label: "Campaigns",
        hint: "Correlated threat campaigns and clusters",
        icon: Layers,
      },
      {
        href: "/graph",
        label: "Graph Explorer",
        hint: "Multi-hop graph paths and circular flow detection",
        icon: GitFork,
      },
    ],
  },
  {
    label: "Mule & Compliance",
    items: [
      {
        href: "/mulehunter",
        label: "Mule Hunter",
        hint: "RBIH MuleHunter behavioral profiling and network canvas",
        icon: Network,
      },
      {
        href: "/registry",
        label: "Smart Registry",
        hint: "RBIH DPIP keyed fraud registry & audit trail",
        icon: Database,
      },
      {
        href: "/command",
        label: "Command Center",
        hint: "Operational readiness & live telemetry",
        icon: Activity,
      },
      {
        href: "/lab",
        label: "Simulation Lab",
        hint: "Adversarial benchmark scenarios and test runners",
        icon: FlaskConical,
      },
    ],
  },
];

export function activeItem(pathname: string): NavItem | undefined {
  const all = navGroups.flatMap((g) => g.items);
  if (pathname === "/") return all[0];
  return (
    all.find((item) => item.href === pathname) ||
    all.find((item) => item.href !== "/" && pathname.startsWith(item.href))
  );
}
