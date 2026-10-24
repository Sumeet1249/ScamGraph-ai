export type MuleNodeType =
  | "origin"       // Victim or funding account
  | "mule_l1"      // Layer 1 Mule (direct recipient)
  | "mule_l2"      // Layer 2 Mule (dispersal)
  | "mule_l3"      // Layer 3 Mule (aggregation)
  | "destination"  // End recipient
  | "cashout"      // ATM / Cash withdrawal point
  | "crypto"       // Crypto exchange / P2P on-ramp
  | "shell"        // Shell entity / Bogus merchant POS
  | "custom";      // User custom box

export type RiskLevel = "critical" | "high" | "medium" | "low" | "verified";

export type BorderStyle = "solid" | "dashed" | "dotted";

export type LineStyle = "solid" | "dashed" | "animated";

export interface MuleNode {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  title: string;
  subtitle: string;
  accountNumber?: string;
  bankName?: string;
  ifsc?: string;
  upiId?: string;
  type: MuleNodeType;
  risk: RiskLevel;
  fillColor: string;
  strokeColor: string;
  strokeWidth: number;
  strokeStyle: BorderStyle;
  textColor?: string;
  glow?: boolean;
  amount?: string;
  notes?: string;
  tags?: string[];
}

export interface MuleEdge {
  id: string;
  sourceId: string;
  targetId: string;
  label: string;
  amount?: string;
  color: string;
  width: number;
  style: LineStyle;
  arrow: boolean;
  notes?: string;
}

export interface MuleGraphData {
  id: string;
  name: string;
  description: string;
  updatedAt: string;
  nodes: MuleNode[];
  edges: MuleEdge[];
  pan?: { x: number; y: number };
  zoom?: number;
}

// Preset color options for Fill and Border
export const COLOR_PALETTE = {
  fills: [
    { name: "Dark Slate", value: "#0F172A" },
    { name: "Deep Navy", value: "#0B132B" },
    { name: "Threat Maroon", value: "#450A0A" },
    { name: "Alert Amber", value: "#451A03" },
    { name: "Cyber Indigo", value: "#1E1B4B" },
    { name: "Emerald Depths", value: "#064E3B" },
    { name: "Purple Void", value: "#3B0764" },
    { name: "Midnight Charcoal", value: "#18181B" },
  ],
  strokes: [
    { name: "Mule Alert Red", value: "#EF4444" },
    { name: "Warning Orange", value: "#F97316" },
    { name: "Investigation Amber", value: "#F59E0B" },
    { name: "Electric Indigo", value: "#6366F1" },
    { name: "Cyber Cyan", value: "#06B6D4" },
    { name: "Neon Violet", value: "#A855F7" },
    { name: "Verified Emerald", value: "#10B981" },
    { name: "Border Slate", value: "#475569" },
  ],
};

export const NODE_TYPE_INFO: Record<
  MuleNodeType,
  { label: string; defaultFill: string; defaultStroke: string; defaultRisk: RiskLevel; badge: string }
> = {
  origin: {
    label: "Victim / Origin",
    defaultFill: "#0B132B",
    defaultStroke: "#06B6D4",
    defaultRisk: "low",
    badge: "ORIGIN",
  },
  mule_l1: {
    label: "Layer 1 Mule (Aggregator)",
    defaultFill: "#450A0A",
    defaultStroke: "#EF4444",
    defaultRisk: "critical",
    badge: "MULE L1",
  },
  mule_l2: {
    label: "Layer 2 Mule (Splitter)",
    defaultFill: "#451A03",
    defaultStroke: "#F97316",
    defaultRisk: "high",
    badge: "MULE L2",
  },
  mule_l3: {
    label: "Layer 3 Mule (Layering)",
    defaultFill: "#3B0764",
    defaultStroke: "#A855F7",
    defaultRisk: "medium",
    badge: "MULE L3",
  },
  destination: {
    label: "Destination Account",
    defaultFill: "#0F172A",
    defaultStroke: "#6366F1",
    defaultRisk: "high",
    badge: "DESTINATION",
  },
  cashout: {
    label: "Cash-out / ATM Point",
    defaultFill: "#18181B",
    defaultStroke: "#EF4444",
    defaultRisk: "critical",
    badge: "ATM CASHOUT",
  },
  crypto: {
    label: "Crypto Exchange / P2P",
    defaultFill: "#1E1B4B",
    defaultStroke: "#8B5CF6",
    defaultRisk: "critical",
    badge: "CRYPTO ON-RAMP",
  },
  shell: {
    label: "Shell Co / Merchant POS",
    defaultFill: "#0F172A",
    defaultStroke: "#EC4899",
    defaultRisk: "high",
    badge: "SHELL CORP",
  },
  custom: {
    label: "Custom Investigation Node",
    defaultFill: "#0F172A",
    defaultStroke: "#64748B",
    defaultRisk: "low",
    badge: "CUSTOM",
  },
};

export const RISK_COLORS: Record<RiskLevel, { text: string; bg: string; border: string; glow: string }> = {
  critical: {
    text: "text-red-400",
    bg: "bg-red-950/80",
    border: "border-red-500/50",
    glow: "shadow-[0_0_15px_rgba(239,68,68,0.35)]",
  },
  high: {
    text: "text-orange-400",
    bg: "bg-orange-950/80",
    border: "border-orange-500/50",
    glow: "shadow-[0_0_15px_rgba(249,115,22,0.35)]",
  },
  medium: {
    text: "text-amber-400",
    bg: "bg-amber-950/80",
    border: "border-amber-500/50",
    glow: "shadow-[0_0_15px_rgba(245,158,11,0.35)]",
  },
  low: {
    text: "text-blue-400",
    bg: "bg-blue-950/80",
    border: "border-blue-500/50",
    glow: "shadow-[0_0_15px_rgba(59,130,246,0.35)]",
  },
  verified: {
    text: "text-emerald-400",
    bg: "bg-emerald-950/80",
    border: "border-emerald-500/50",
    glow: "shadow-[0_0_15px_rgba(16,185,129,0.35)]",
  },
};

// ================= PRESET SCENARIOS =================

export const DEFAULT_MULE_SCENARIO: MuleGraphData = {
  id: "rbih-mulehunter-default",
  name: "RBIH MuleHunter Flagship Ring (3-Hop Dispersal)",
  description:
    "Active multi-tier money mule network identified across 4 scheduled commercial banks and digital payment rails, laundering ₹24,50,000.",
  updatedAt: new Date().toISOString(),
  pan: { x: 40, y: 30 },
  zoom: 0.95,
  nodes: [
    {
      id: "node-victim-1",
      x: 60,
      y: 220,
      width: 260,
      height: 140,
      title: "ICICI Bank - Victim Account",
      subtitle: "Phished via Fake SBI Rewards APK",
      bankName: "ICICI Bank",
      accountNumber: "204918204912",
      ifsc: "ICIC0000204",
      upiId: "victim_user@icici",
      type: "origin",
      risk: "verified",
      fillColor: "#0B132B",
      strokeColor: "#06B6D4",
      strokeWidth: 2,
      strokeStyle: "solid",
      amount: "-₹24,50,000",
      notes: "Elderly victim scammed into downloading remote control malware on 18-Oct.",
      glow: true,
      tags: ["Victim", "APK Phish", "High Loss"],
    },
    {
      id: "node-mule-l1-axis",
      x: 390,
      y: 120,
      width: 270,
      height: 145,
      title: "Axis Bank - Mule Hub L1",
      subtitle: "High Velocity Churn (Opened < 14 Days)",
      bankName: "Axis Bank",
      accountNumber: "9180200481923",
      ifsc: "UTIB0001042",
      upiId: "fasttransfer88@axisbank",
      type: "mule_l1",
      risk: "critical",
      fillColor: "#450A0A",
      strokeColor: "#EF4444",
      strokeWidth: 3,
      strokeStyle: "solid",
      amount: "₹14,00,000 IN",
      notes: "Account opened with forged Aadhaar document. Funds dispersed within 3 minutes of arrival.",
      glow: true,
      tags: ["RBI Flagged", "Mule Account", "Rapid Churn"],
    },
    {
      id: "node-mule-l1-kotak",
      x: 390,
      y: 330,
      width: 270,
      height: 145,
      title: "Kotak Mahindra - Mule L1",
      subtitle: "Student KYC Rent Ring",
      bankName: "Kotak Mahindra Bank",
      accountNumber: "441029381920",
      ifsc: "KKBK0000981",
      upiId: "techrent77@kotak",
      type: "mule_l1",
      risk: "critical",
      fillColor: "#450A0A",
      strokeColor: "#EF4444",
      strokeWidth: 3,
      strokeStyle: "solid",
      amount: "₹10,50,000 IN",
      notes: "College student bank account rented for 5% commission via Telegram syndicate.",
      glow: true,
      tags: ["Telegram Ring", "Rented KYC", "Mule L1"],
    },
    {
      id: "node-mule-l2-sbi",
      x: 740,
      y: 40,
      width: 260,
      height: 140,
      title: "SBI - Layer 2 Mule (Dormant)",
      subtitle: "Reactivated Dormant Savings",
      bankName: "State Bank of India",
      accountNumber: "381902847192",
      ifsc: "SBIN0004128",
      upiId: "mulesbi1@sbi",
      type: "mule_l2",
      risk: "high",
      fillColor: "#451A03",
      strokeColor: "#F97316",
      strokeWidth: 2,
      strokeStyle: "dashed",
      amount: "₹7,00,000",
      notes: "Zero balance for 18 months, suddenly received massive inbound funds.",
      glow: false,
      tags: ["Dormant Spike", "Mule L2"],
    },
    {
      id: "node-mule-l2-pnb",
      x: 740,
      y: 200,
      width: 260,
      height: 140,
      title: "PNB - Rural Mule L2",
      subtitle: "Tier-3 Town Account",
      bankName: "Punjab National Bank",
      accountNumber: "110928374910",
      ifsc: "PUNB0192800",
      upiId: "cashfast99@pnb",
      type: "mule_l2",
      risk: "high",
      fillColor: "#451A03",
      strokeColor: "#F97316",
      strokeWidth: 2,
      strokeStyle: "dashed",
      amount: "₹7,00,000",
      notes: "Immediate micro-IMPS outward transfers initiated to multiple destinations.",
      glow: false,
      tags: ["Tier-3 Ring", "Mule L2"],
    },
    {
      id: "node-mule-l2-canara",
      x: 740,
      y: 360,
      width: 260,
      height: 140,
      title: "Canara Bank - Split Mule L2",
      subtitle: "Multiple Micro UPI Out",
      bankName: "Canara Bank",
      accountNumber: "582910284918",
      ifsc: "CNRB0002918",
      upiId: "splitquick@cnrb",
      type: "mule_l2",
      risk: "high",
      fillColor: "#451A03",
      strokeColor: "#F97316",
      strokeWidth: 2,
      strokeStyle: "dashed",
      amount: "₹5,50,000",
      notes: "Splits funds into sub-₹50,000 tranches to avoid AML velocity triggers.",
      glow: false,
      tags: ["AML Evasion", "Micro-Split"],
    },
    {
      id: "node-mule-l2-indusind",
      x: 740,
      y: 520,
      width: 260,
      height: 140,
      title: "IndusInd - Mule L2",
      subtitle: "Corporate Debit Infiltration",
      bankName: "IndusInd Bank",
      accountNumber: "220918471029",
      ifsc: "INDB0000881",
      upiId: "finmove@indus",
      type: "mule_l2",
      risk: "high",
      fillColor: "#451A03",
      strokeColor: "#F97316",
      strokeWidth: 2,
      strokeStyle: "dashed",
      amount: "₹5,00,000",
      notes: "Account opened using fake GST number.",
      glow: false,
      tags: ["Fake GST", "High Velocity"],
    },
    {
      id: "node-endpoint-atm",
      x: 1090,
      y: 60,
      width: 270,
      height: 145,
      title: "ATM Cluster - Bandra West",
      subtitle: "Physical Cash Extraction",
      bankName: "Multi-ATM Fleet",
      accountNumber: "Card: 4128 **** **** 9012",
      type: "cashout",
      risk: "critical",
      fillColor: "#18181B",
      strokeColor: "#EF4444",
      strokeWidth: 3,
      strokeStyle: "solid",
      amount: "₹6,00,000 Cashed",
      notes: "12 consecutive cardless & debit card cash withdrawals between 02:15 AM - 03:00 AM.",
      glow: true,
      tags: ["Physical ATM", "Cardless Cash", "CCTV Alert"],
    },
    {
      id: "node-endpoint-crypto",
      x: 1090,
      y: 250,
      width: 270,
      height: 145,
      title: "USDT P2P Escrow Off-Ramp",
      subtitle: "Offshore Crypto Conversion",
      bankName: "Crypto Exchange P2P Desk",
      accountNumber: "Wallet: 0x71c...b49e",
      type: "crypto",
      risk: "critical",
      fillColor: "#1E1B4B",
      strokeColor: "#8B5CF6",
      strokeWidth: 3,
      strokeStyle: "solid",
      amount: "₹12,00,000 (USDT)",
      notes: "Funds converted to Tether (USDT) on P2P market and sent to unhosted Tron wallet.",
      glow: true,
      tags: ["USDT", "Tron TRC20", "Unhosted Wallet"],
    },
    {
      id: "node-endpoint-shell",
      x: 1090,
      y: 440,
      width: 270,
      height: 145,
      title: "Apex Electronics Shell Co",
      subtitle: "POS Terminal Swipe Laundering",
      bankName: "Merchant Acquiring Bank",
      accountNumber: "MID: POS_99218204",
      type: "shell",
      risk: "high",
      fillColor: "#0F172A",
      strokeColor: "#EC4899",
      strokeWidth: 2,
      strokeStyle: "solid",
      amount: "₹6,50,000 Swiped",
      notes: "Bogus retail invoice generated for dummy luxury electronics.",
      glow: true,
      tags: ["Bogus POS", "Shell Merchant"],
    },
  ],
  edges: [
    // Origin -> L1
    {
      id: "edge-1",
      sourceId: "node-victim-1",
      targetId: "node-mule-l1-axis",
      label: "₹14,00,000 (RTGS)",
      amount: "₹14,00,000",
      color: "#EF4444",
      width: 3,
      style: "animated",
      arrow: true,
      notes: "Unauthorized net banking RTGS at 01:14 AM",
    },
    {
      id: "edge-2",
      sourceId: "node-victim-1",
      targetId: "node-mule-l1-kotak",
      label: "₹10,50,000 (NEFT)",
      amount: "₹10,50,000",
      color: "#EF4444",
      width: 3,
      style: "animated",
      arrow: true,
      notes: "NEFT split initiated 30 seconds later",
    },
    // Axis L1 -> L2 SBI & PNB
    {
      id: "edge-3",
      sourceId: "node-mule-l1-axis",
      targetId: "node-mule-l2-sbi",
      label: "₹7,00,000 (IMPS)",
      amount: "₹7,00,000",
      color: "#F97316",
      width: 2,
      style: "animated",
      arrow: true,
      notes: "Immediate IMPS forward",
    },
    {
      id: "edge-4",
      sourceId: "node-mule-l1-axis",
      targetId: "node-mule-l2-pnb",
      label: "₹7,00,000 (IMPS)",
      amount: "₹7,00,000",
      color: "#F97316",
      width: 2,
      style: "animated",
      arrow: true,
      notes: "Parallel IMPS transfer",
    },
    // Kotak L1 -> L2 Canara & IndusInd
    {
      id: "edge-5",
      sourceId: "node-mule-l1-kotak",
      targetId: "node-mule-l2-canara",
      label: "₹5,50,000 (UPI)",
      amount: "₹5,50,000",
      color: "#F97316",
      width: 2,
      style: "animated",
      arrow: true,
      notes: "Fast UPI push via virtual payment address",
    },
    {
      id: "edge-6",
      sourceId: "node-mule-l1-kotak",
      targetId: "node-mule-l2-indusind",
      label: "₹5,00,000 (IMPS)",
      amount: "₹5,00,000",
      color: "#F97316",
      width: 2,
      style: "animated",
      arrow: true,
      notes: "IMPS to commercial current account",
    },
    // L2 -> Endpoints
    {
      id: "edge-7",
      sourceId: "node-mule-l2-sbi",
      targetId: "node-endpoint-atm",
      label: "₹6,00,000 (Cash)",
      amount: "₹6,00,000",
      color: "#EF4444",
      width: 3,
      style: "animated",
      arrow: true,
      notes: "Cash withdrawal in Bandra",
    },
    {
      id: "edge-8",
      sourceId: "node-mule-l2-pnb",
      targetId: "node-endpoint-crypto",
      label: "₹6,50,000 (P2P USDT)",
      amount: "₹6,50,000",
      color: "#8B5CF6",
      width: 3,
      style: "animated",
      arrow: true,
      notes: "USDT buyer verified on platform",
    },
    {
      id: "edge-9",
      sourceId: "node-mule-l2-canara",
      targetId: "node-endpoint-crypto",
      label: "₹5,50,000 (P2P USDT)",
      amount: "₹5,50,000",
      color: "#8B5CF6",
      width: 2,
      style: "animated",
      arrow: true,
      notes: "Aggregated crypto purchase",
    },
    {
      id: "edge-10",
      sourceId: "node-mule-l2-indusind",
      targetId: "node-endpoint-shell",
      label: "₹5,00,000 (POS)",
      amount: "₹5,00,000",
      color: "#EC4899",
      width: 2,
      style: "animated",
      arrow: true,
      notes: "Fabricated sales receipt for consumer electronics",
    },
  ],
};

export const FAST_UPI_SCENARIO: MuleGraphData = {
  id: "fast-upi-mule-ring",
  name: "UPI Fast-Churn Fraud Syndicate",
  description: "Rapid multi-victim phishing ring aggregating into single UPI mule aggregator with ATM cashout.",
  updatedAt: new Date().toISOString(),
  pan: { x: 50, y: 50 },
  zoom: 1,
  nodes: [
    {
      id: "upi-vic-1",
      x: 80,
      y: 80,
      width: 240,
      height: 120,
      title: "Victim #1 (Electricity Bill Phish)",
      subtitle: "UPI: user1@paytm",
      bankName: "Paytm Payments Bank",
      type: "origin",
      risk: "verified",
      fillColor: "#0B132B",
      strokeColor: "#06B6D4",
      strokeWidth: 2,
      strokeStyle: "solid",
      amount: "-₹85,000",
      notes: "SMS phish: electricity disconnect threat.",
    },
    {
      id: "upi-vic-2",
      x: 80,
      y: 230,
      width: 240,
      height: 120,
      title: "Victim #2 (KYC Update Phish)",
      subtitle: "UPI: user2@okaxis",
      bankName: "Axis Bank",
      type: "origin",
      risk: "verified",
      fillColor: "#0B132B",
      strokeColor: "#06B6D4",
      strokeWidth: 2,
      strokeStyle: "solid",
      amount: "-₹1,20,000",
      notes: "Fake bank APK credential harvest.",
    },
    {
      id: "upi-vic-3",
      x: 80,
      y: 380,
      width: 240,
      height: 120,
      title: "Victim #3 (Lottery / Job Scam)",
      subtitle: "UPI: user3@okhdfcbank",
      bankName: "HDFC Bank",
      type: "origin",
      risk: "verified",
      fillColor: "#0B132B",
      strokeColor: "#06B6D4",
      strokeWidth: 2,
      strokeStyle: "solid",
      amount: "-₹95,000",
      notes: "Telegram part-time job deposit lure.",
    },
    {
      id: "upi-mule-aggregator",
      x: 440,
      y: 200,
      width: 280,
      height: 150,
      title: "Central UPI Mule Collector",
      subtitle: "VPA: fastcashpay88@ybl",
      bankName: "Yes Bank / PhonePe",
      accountNumber: "00189201948",
      type: "mule_l1",
      risk: "critical",
      fillColor: "#450A0A",
      strokeColor: "#EF4444",
      strokeWidth: 3,
      strokeStyle: "solid",
      amount: "₹3,00,000 IN",
      notes: "Consolidates micro UPI inflows, instant sweep to cashout agent.",
      glow: true,
    },
    {
      id: "upi-cashout",
      x: 840,
      y: 200,
      width: 260,
      height: 140,
      title: "QR Code / P2P Cashout",
      subtitle: "Mobile Kirana POS Cashout",
      bankName: "Merchant QR",
      type: "cashout",
      risk: "critical",
      fillColor: "#18181B",
      strokeColor: "#EF4444",
      strokeWidth: 2,
      strokeStyle: "solid",
      amount: "₹3,00,000 Cashed",
      notes: "Cash given out over counter with 8% cut deducted.",
    },
  ],
  edges: [
    {
      id: "upi-e1",
      sourceId: "upi-vic-1",
      targetId: "upi-mule-aggregator",
      label: "₹85,000 (UPI)",
      color: "#EF4444",
      width: 2,
      style: "animated",
      arrow: true,
    },
    {
      id: "upi-e2",
      sourceId: "upi-vic-2",
      targetId: "upi-mule-aggregator",
      label: "₹1,20,000 (UPI)",
      color: "#EF4444",
      width: 2,
      style: "animated",
      arrow: true,
    },
    {
      id: "upi-e3",
      sourceId: "upi-vic-3",
      targetId: "upi-mule-aggregator",
      label: "₹95,000 (UPI)",
      color: "#EF4444",
      width: 2,
      style: "animated",
      arrow: true,
    },
    {
      id: "upi-e4",
      sourceId: "upi-mule-aggregator",
      targetId: "upi-cashout",
      label: "₹3,00,000 (Instant QR Sweep)",
      color: "#EF4444",
      width: 3,
      style: "animated",
      arrow: true,
    },
  ],
};

export const BLANK_SCENARIO: MuleGraphData = {
  id: "new-investigation",
  name: "New MuleHunter Investigation",
  description: "Add bank accounts, mules, and financial edges to map out money laundering chains.",
  updatedAt: new Date().toISOString(),
  pan: { x: 0, y: 0 },
  zoom: 1,
  nodes: [],
  edges: [],
};
