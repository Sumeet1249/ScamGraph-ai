"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Search,
  Copy,
  Eye,
  EyeOff,
  Building,
  Landmark,
  Share2,
  Lock,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Gavel,
  Layers,
  FileText,
  TrendingUp,
  ArrowUpRight,
  ExternalLink,
  ChevronRight,
  Phone,
  Globe,
  CreditCard,
  Coins,
  Download,
  Filter,
  CheckCheck,
  XCircle,
  FileCode,
  History,
  Scale,
  Sparkles,
  GitMerge,
  ShieldCheck,
  Hash,
  Activity,
  FileDown,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

interface EntityData {
  id: string;
  type: string;
  identifier: string;
  psp: string;
  ifsc: string;
  branch: string;
  holder_mask: string;
  holder_real?: string;
  risk_state: string;
  risk_score: number;
  confidence: number;
  status_rule: string;
  first_observed: string;
  last_observed: string;
  corroborated_cases: number;
  syndicate_id: string;
  syndicate_name: string;
  avg_ticket: number;
  total_ingress: number;
  egress_velocity: string;
  lien_placed: number;
  cfr_ref: string;
  direct_edges: {
    type: string;
    identifier: string;
    label: string;
    status: string;
  }[];
}

const CANONICAL_ENTITY: EntityData = {
  id: "ENT-UPI-AXIS-84920",
  type: "UPI Virtual Payment Address (VPA)",
  identifier: "util-power-84920@okaxis",
  psp: "Axis Bank Ltd",
  ifsc: "UTIB0000849",
  branch: "Koramangala 4th Block, Bengaluru, KA",
  holder_mask: "**H** D*****",
  holder_real: "ROHIT DASGUPTA",
  risk_state: "High Risk Mule Destination",
  risk_score: 98,
  confidence: 98.4,
  status_rule: "Correlated Mule Destination in Ongoing Syndicate Investigation (Zero-PII Rule §4.11)",
  first_observed: "2026-10-21T09:15:00Z",
  last_observed: "2026-10-24T20:46:00Z",
  corroborated_cases: 14,
  syndicate_id: "#UTL-8490",
  syndicate_name: "State Electricity Instant Cutoff Syndicate",
  avg_ticket: 10850,
  total_ingress: 148200,
  egress_velocity: "18 mins to P2P USDT Counterparty",
  lien_placed: 24350,
  cfr_ref: "CFC-2026-94810",
  direct_edges: [
    { type: "Telephony Anchor", identifier: "+91 98******10", label: "14 Co-occurrences", status: "Primary SIM Pool" },
    { type: "Domain Infrastructure", identifier: "bescom-bill-renew.in", label: "14 Referrals", status: "DNS Sinkholed" },
    { type: "Exit Counterparty", identifier: "crypto-p2p-gateway@binance", label: "3 IMPS Sweeps", status: "High Velocity" },
  ],
};

// 18 Chronological Forensic Timeline Events
const TIMELINE_EVENTS = [
  { id: "EVT-01", timestamp: "2026-10-21T09:15:00Z", category: "INTAKE", title: "Airtel GSM SIM Activated with Fake KYC", description: "MSISDN +91 98******10 registered at Kolkata south dealer using forged voter ID. Immediate IMEI association with Poco C51.", source: "DoT TAFCOP Telemetry", badge: "Airtel Kolkata", badgeTone: "neutral" },
  { id: "EVT-02", timestamp: "2026-10-21T11:42:00Z", category: "TELEMETRY", title: "Corridor Tower Roaming Ping in Bengaluru", description: "Handset latched to BTS Cell ID 404-45-1092 in Koramangala, Bengaluru without prior transit telemetry (BTS hop anomaly).", source: "Cellular Tower LAC Monitor", badge: "BTS LAC 404-45", badgeTone: "warning" },
  { id: "EVT-03", timestamp: "2026-10-21T13:20:00Z", category: "INFRASTRUCTURE", title: "Rogue APK Dropper Server Registered", description: "Domain bescom-bill-renew.in configured on Bulletproof Offshore ASN 185.220.101.5 with Fast-Flux DNS entries.", source: "Shadowserver DNS Feed", badge: "DNS Rogue", badgeTone: "danger" },
  { id: "EVT-04", timestamp: "2026-10-21T14:30:00Z", category: "BANKING", title: "Axis Bank Account Bound to UPI App", description: "Account 9210100******84 opened online; VPA util-power-84920@okaxis bound through Axis Bank UPI Switch.", source: "NPCI UPI Ingress Log", badge: "VPA Bound", badgeTone: "info" },
  { id: "EVT-05", timestamp: "2026-10-21T16:05:00Z", category: "TRANSACTION", title: "Test Ingress Micro-Auth ₹10.00", description: "Decoy micro-authorization executed from compromised test phone to confirm routing and avoid initial velocity alarms.", source: "Axis Core Banking Switch", quantum: 10, badge: "Decoy Probe", badgeTone: "neutral" },
  { id: "EVT-06", timestamp: "2026-10-22T08:15:00Z", category: "INTAKE", title: "SMS Outbreak Blast Initiated (2,400 Targets)", description: "SMS header BW-BESCOM transmitted mass threat template: 'Electricity overdue tonight disconnect at 21:30'.", source: "Telecom DLT Filter", badge: "2,400 SMS", badgeTone: "danger" },
  { id: "EVT-07", timestamp: "2026-10-22T10:14:00Z", category: "TRANSACTION", title: "First Victim Mandate Drain ₹11,450.00", description: "Citizen G. S. Rao duped via fake quick-pay page; parameter tampered from ₹10 bill to ₹11,450 debit.", source: "NPCI RRN 429810482910", quantum: 11450, badge: "Mandate Drain", badgeTone: "danger" },
  { id: "EVT-08", timestamp: "2026-10-22T10:32:00Z", category: "TRANSACTION", title: "Immediate Layer-2 IMPS Egress ₹11,000.00", description: "Siphoned funds transferred within 18 minutes via IMPS to Yes Bank intermediary mule power-settle-blr@ybl.", source: "IMPS Outbound Rail", quantum: 11000, badge: "IMPS Dispersal", badgeTone: "warning" },
  { id: "EVT-09", timestamp: "2026-10-22T14:50:00Z", category: "TRANSACTION", title: "Second Siphoning Batch ₹9,800.00", description: "Victim #SG-84915 in Indiranagar defrauded under emergency disconnection threat.", source: "NPCI RRN 429810483401", quantum: 9800, badge: "Victim Debit", badgeTone: "danger" },
  { id: "EVT-10", timestamp: "2026-10-22T18:20:00Z", category: "TELEMETRY", title: "Call Recording Intercept Logged", description: "Citizen recorded telephone threat from +91 98******10 impersonating BESCOM Executive Engineer 'K. Nayak'.", source: "Citizen Voice Intake", badge: "Voice Evidence", badgeTone: "info" },
  { id: "EVT-11", timestamp: "2026-10-23T09:10:00Z", category: "TRANSACTION", title: "Aggregated Ingress Influx ₹38,600.00", description: "Four simultaneous citizen transactions settled into util-power-84920@okaxis in 22 minutes.", source: "Axis Core Banking Switch", quantum: 38600, badge: "Velocity Surge", badgeTone: "danger" },
  { id: "EVT-12", timestamp: "2026-10-23T09:35:00Z", category: "TRANSACTION", title: "P2P Crypto Exit via Binance IMPS ₹45,000.00", description: "IMPS remittance to verified P2P escrow agent merchant on Binance (USDT rate ₹91.20/dollar).", source: "CFCFRMS Rail Telemetry", quantum: 45000, badge: "Crypto Egress", badgeTone: "danger" },
  { id: "EVT-13", timestamp: "2026-10-23T14:40:00Z", category: "INTELLIGENCE", title: "Corridor Match with Syndicate #UTL-8490", description: "ScamGraph graph reasoning engine matched VPA, telephony anchor, and offshore host to ongoing syndicate.", source: "ScamGraph Graph Engine", badge: "Graph Match", badgeTone: "info" },
  { id: "EVT-14", timestamp: "2026-10-24T09:20:00Z", category: "LEGAL", title: "FIR 0142/2026 Formally Registered", description: "Bengaluru City Cyber Crime PS registered formal FIR under §66D IT Act and §318(4) Bharatiya Nyaya Sanhita.", source: "Bengaluru Cyber Crime PS", badge: "FIR Registered", badgeTone: "info" },
  { id: "EVT-15", timestamp: "2026-10-24T12:30:00Z", category: "ENFORCEMENT", title: "Section 102 CrPC Lien Order Dispatched", description: "Statutory freezing order served to Axis Bank Nodal Officer demanding total freeze on Account 9210100******84.", source: "Investigating Officer Raghavendra M.", badge: "§102 Lien Notice", badgeTone: "danger" },
  { id: "EVT-16", timestamp: "2026-10-24T14:10:00Z", category: "BANKING", title: "Axis Bank Lien Executed (₹24,350 Frozen)", description: "Bank nodal desk verified order; freeze placed on remaining ledger balance ₹24,350. Outbound transactions halted.", source: "Axis Bank Compliance Desk", quantum: 24350, badge: "Lien Placed", badgeTone: "success" },
  { id: "EVT-17", timestamp: "2026-10-24T16:45:00Z", category: "INFRASTRUCTURE", title: "NCIIPC / CERT-In DNS Sinkhole Active", description: "Domain bescom-bill-renew.in sinkholed by National Cyber Coordination Centre. Traffic diverted to forensics server.", source: "CERT-In Threat Advisory", badge: "Sinkholed", badgeTone: "success" },
  { id: "EVT-18", timestamp: "2026-10-24T20:46:00Z", category: "DISPUTE", title: "Account Holder Lodged Online Grievance", description: "Account holder Rohit Dasgupta claimed identity theft via compromised mobile banking app; hearing pending.", source: "Axis Online Banking Grievance", badge: "Dispute Lodged", badgeTone: "warning" },
];

// 12 Direct Relationships Data
const DIRECT_RELATIONSHIPS = [
  { id: "REL-01", category: "TELEPHONY", target_id: "+91 98******10", target_name: "Primary Caller GSM (+91 98765 43210)", relationship_type: "Calling Anchor & OTP Sink", flow_direction: "BIDIRECTIONAL", volume: "14 Calls / 6 SMS", confidence: 99.2, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "24 Oct 2026", status: "Active Anchor", icon: Phone },
  { id: "REL-02", category: "TELEPHONY", target_id: "+91 98******09", target_name: "Secondary Roaming SIM (+91 98234 11209)", relationship_type: "SIM Corridor Co-presence", flow_direction: "INBOUND", volume: "8 Tower Handshakes", confidence: 94.5, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "24 Oct 2026", status: "Kolkata Roaming", icon: Phone },
  { id: "REL-03", category: "TELEPHONY", target_id: "BW-BESCOM-DLT", target_name: "Header BW-BESCOM (Bulk SMS Injector)", relationship_type: "Campaign Blast Conduit", flow_direction: "OUTBOUND", volume: "2,400 Dispatches", confidence: 97.0, hop_distance: 1, first_seen: "22 Oct 2026", last_seen: "23 Oct 2026", status: "Header Revoked", icon: Phone },
  { id: "REL-04", category: "TELEPHONY", target_id: "CELL-404-45-1092", target_name: "Tower LAC 404-45 (Bengaluru Koramangala)", relationship_type: "Physical Tower Triangulation", flow_direction: "BIDIRECTIONAL", volume: "42 Registrations", confidence: 98.8, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "24 Oct 2026", status: "Triangulated", icon: Globe },
  { id: "REL-05", category: "BANKING", target_id: "ENT-BANK-AXIS-9210", target_name: "Axis Bank Core Account (9210100******84)", relationship_type: "Primary Settling Account", flow_direction: "BIDIRECTIONAL", volume: "₹1,48,200 Ingress", confidence: 100.0, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "24 Oct 2026", status: "Lien Frozen", icon: Landmark },
  { id: "REL-06", category: "BANKING", target_id: "ENT-UPI-YBL-POWER", target_name: "power-settle-blr@ybl (Yes Bank)", relationship_type: "Layer-2 Dispersal Mule", flow_direction: "OUTBOUND", volume: "₹48,500 Split Sweep", confidence: 96.4, hop_distance: 1, first_seen: "22 Oct 2026", last_seen: "23 Oct 2026", status: "Under Freeze Order", icon: CreditCard },
  { id: "REL-07", category: "BANKING", target_id: "ENT-UPI-PAYTM-REFUND", target_name: "discom-refund-mule@paytm", relationship_type: "Layer-3 Cash-Out Mule", flow_direction: "OUTBOUND", volume: "₹32,000 ATM Withdrawals", confidence: 93.1, hop_distance: 2, first_seen: "22 Oct 2026", last_seen: "24 Oct 2026", status: "Watchlisted", icon: CreditCard },
  { id: "REL-08", category: "INFRASTRUCTURE", target_id: "bescom-bill-renew.in", target_name: "bescom-bill-renew.in (Phishing Host)", relationship_type: "Payment Redirection Source", flow_direction: "INBOUND", volume: "14 Victim Referrals", confidence: 99.6, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "24 Oct 2026", status: "DNS Sinkholed", icon: Globe },
  { id: "REL-09", category: "INFRASTRUCTURE", target_id: "bescom-quickpay.apk", target_name: "bescom-quickpay.apk (Malicious Package)", relationship_type: "Accessibility RAT Dropper", flow_direction: "BIDIRECTIONAL", volume: "SHA256: 7f8a...31b9", confidence: 99.1, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "23 Oct 2026", status: "Malware Flagged", icon: FileCode },
  { id: "REL-10", category: "CRYPTO_EXIT", target_id: "crypto-p2p-gateway@binance", target_name: "crypto-p2p-gateway@binance (IMPS Escrow)", relationship_type: "P2P Crypto Exit Siphon", flow_direction: "OUTBOUND", volume: "₹45,000 (USDT Swap)", confidence: 97.8, hop_distance: 1, first_seen: "23 Oct 2026", last_seen: "24 Oct 2026", status: "Binance Alerted", icon: Coins },
  { id: "REL-11", category: "CRYPTO_EXIT", target_id: "TRC20-TXYZ99B2", target_name: "Tron Wallet (TXYZ...99b2)", relationship_type: "Laundered USDT Cold Vault", flow_direction: "OUTBOUND", volume: "4,820 USDT Balance", confidence: 92.4, hop_distance: 2, first_seen: "23 Oct 2026", last_seen: "24 Oct 2026", status: "Chainalysis Tagged", icon: Coins },
  { id: "REL-12", category: "TEMPLATE", target_id: "TPL-PWR-CUTOFF-V2", target_name: "Script: Power Cutoff Urgency Template", relationship_type: "Coercion Phrasing Matrix", flow_direction: "INBOUND", volume: "98.4% NLP Match", confidence: 98.4, hop_distance: 1, first_seen: "21 Oct 2026", last_seen: "24 Oct 2026", status: "Attributed", icon: FileText },
];

// 2 Correlated Campaigns
const CORRELATED_CAMPAIGNS = [
  {
    id: "camp-power-urgent",
    code: "#UTL-8490",
    title: "State Electricity Instant Cutoff Syndicate",
    status: "CRITICAL OUTBREAK",
    confidence: 98.4,
    overlap_score: 99.2,
    victims_count: 142,
    total_loss: 18450000,
    lien_recovered: 4280000,
    lead_officer: "Inspector Raghavendra M.",
    jurisdictions: ["Bengaluru City", "West Bengal Corridor", "Mumbai Metro"],
    first_seen: "2026-10-21T09:15:00Z",
    last_seen: "2026-10-24T20:46:00Z",
    shared_iocs: ["util-power-84920@okaxis", "+91 98******10", "bescom-bill-renew.in", "ASN 185.220.101.5", "Poco C51 IMEI 8642..."],
    description: "Multi-jurisdiction extortion ring threatening immediate domestic electrical disconnection within 1 hour unless victims authorize ₹10 bill update via rogue portal, which siphons between ₹9,800 to ₹14,200 into mule layers.",
  },
  {
    id: "camp-power-discom-w2",
    code: "#UTL-8488",
    title: "Urgent Discom Evening Disconnection Wave",
    status: "SURGE CLUSTER",
    confidence: 91.0,
    overlap_score: 88.6,
    victims_count: 48,
    total_loss: 6420000,
    lien_recovered: 1540000,
    lead_officer: "ACP Sneha Patil",
    jurisdictions: ["Maharashtra", "Telangana", "Karnataka"],
    first_seen: "2026-10-18T14:20:00Z",
    last_seen: "2026-10-23T18:00:00Z",
    shared_iocs: ["bescom-bill-renew.in", "Tower LAC 404-45", "power-settle-blr@ybl"],
    description: "Overlapping sister campaign utilizing identical APK dropper and telephony roaming infrastructure targeting commercial shops and small restaurants during peak evening billing hours.",
  },
];

// 14 Forensic Evidence & Banking Receipts
const FORENSIC_EVIDENCE = [
  { id: "EVD-01", type: "NPCI_RRN", title: "NPCI UPI Switch Transaction Callback", ref: "RRN-2026-1024-84920-01", format: "JSON Log", size: "4.2 KB", hash: "9f8a...c31b", timestamp: "2026-10-24T19:46:00Z", status: "Tamper Verified" },
  { id: "EVD-02", type: "NPCI_RRN", title: "NPCI Parameter Tampering Flag Record", ref: "RRN-2026-1022-84910-04", format: "JSON Log", size: "3.8 KB", hash: "4d7e...912a", timestamp: "2026-10-22T10:14:00Z", status: "Tamper Verified" },
  { id: "EVD-03", type: "POLICE_FIR", title: "Cyber Crime Police Station Formal FIR Copy", ref: "FIR-0142-2026-BCP", format: "PDF Bundle", size: "1.4 MB", hash: "e2b1...78f0", timestamp: "2026-10-24T09:20:00Z", status: "Court Certified" },
  { id: "EVD-04", type: "BANK_STATEMENT", title: "Axis Bank Koramangala Ledger Statement", ref: "AXIS-STMT-9210-OCT26", format: "PDF Statement", size: "840 KB", hash: "81c4...6702", timestamp: "2026-10-24T14:10:00Z", status: "Bank Sealed" },
  { id: "EVD-05", type: "TELECOM_CDR", title: "Bharti Airtel Call Detail Record & BTS LAC Triangulation", ref: "CDR-AT-9876543210-01", format: "CSV Table", size: "128 KB", hash: "7a22...f901", timestamp: "2026-10-24T11:00:00Z", status: "LE Custody" },
  { id: "EVD-06", type: "MALWARE_APK", title: "Decompiled APK Manifest & Static Smali Disassembly", ref: "APK-BESCOM-QKPAY-V1", format: "ZIP Archive", size: "8.9 MB", hash: "331d...b844", timestamp: "2026-10-21T16:00:00Z", status: "Sandbox Executed" },
  { id: "EVD-07", type: "SMS_DLT", title: "DLT Gateway SMS Delivery Header BW-BESCOM", ref: "DLT-LOG-2026-1022-01", format: "XML Log", size: "48 KB", hash: "bb90...a112", timestamp: "2026-10-22T08:15:00Z", status: "Carrier Signed" },
  { id: "EVD-08", type: "IMPS_WIRE", title: "IMPS Remittance Advice to Binance Escrow Desk", ref: "IMPS-AXIS-20261023-991", format: "PDF Advice", size: "320 KB", hash: "64ef...190c", timestamp: "2026-10-23T09:35:00Z", status: "Bank Cleared" },
  { id: "EVD-09", type: "WHOIS_DNS", title: "Offshore Bulletproof Host Traceroute & BGP ASN Log", ref: "DNS-WHOIS-BESCOM-01", format: "TXT Log", size: "14 KB", hash: "1852...2015", timestamp: "2026-10-21T13:20:00Z", status: "Sinkholed" },
  { id: "EVD-10", type: "SSL_CERT", title: "Rogue Let's Encrypt Certificate Fingerprint", ref: "SSL-SHA256-BESCOM-REN", format: "PEM Cert", size: "2.1 KB", hash: "a099...f44b", timestamp: "2026-10-21T14:00:00Z", status: "Revoked" },
  { id: "EVD-11", type: "AUDIO_STT", title: "Citizen Call Recording Audio & STT Transcript", ref: "STT-CALL-REC-2026-09", format: "WAV + JSON", size: "3.2 MB", hash: "c18f...4e99", timestamp: "2026-10-22T18:20:00Z", status: "Transcribed" },
  { id: "EVD-12", type: "MERKLE_PROOF", title: "Victim Handset Screen Recording Merkle Tree", ref: "MRK-PROOF-SG84920", format: "JSON Proof", size: "64 KB", hash: "e3b0...c44b", timestamp: "2026-10-24T19:50:00Z", status: "Cryptographic §65B" },
  { id: "EVD-13", type: "POS_CALLBACK", title: "Disputed Merchant POS Terminal Settlement Slip", ref: "POS-SLIP-42981048", format: "PDF Slip", size: "180 KB", hash: "55ba...8900", timestamp: "2026-10-24T17:20:00Z", status: "Verified POS" },
  { id: "EVD-14", type: "CFCFRMS", title: "CFCFRMS Citizen Financial Cyber Fraud Synchronized Slip", ref: "CFC-2026-94810-SYNC", format: "PDF Slip", size: "420 KB", hash: "9812...01fe", timestamp: "2026-10-24T20:15:00Z", status: "National Portal" },
];

export default function EntityDetailPage({ params }: { params: { id: string } }) {
  const [entity, setEntity] = useState<EntityData>(CANONICAL_ENTITY);
  const [isRevealed, setIsRevealed] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [copied, setCopied] = useState(false);
  const [timelineCategory, setTimelineCategory] = useState<string>("ALL");
  const [relationshipCategory, setRelationshipCategory] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const handleCopy = () => {
    navigator.clipboard.writeText(entity.identifier);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredTimeline = useMemo(() => {
    return TIMELINE_EVENTS.filter((evt) => {
      if (timelineCategory !== "ALL" && evt.category !== timelineCategory) return false;
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        evt.title.toLowerCase().includes(q) ||
        evt.description.toLowerCase().includes(q) ||
        evt.source.toLowerCase().includes(q) ||
        evt.id.toLowerCase().includes(q)
      );
    });
  }, [timelineCategory, searchQuery]);

  const filteredRelationships = useMemo(() => {
    return DIRECT_RELATIONSHIPS.filter((rel) => {
      if (relationshipCategory !== "ALL" && rel.category !== relationshipCategory) return false;
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        rel.target_name.toLowerCase().includes(q) ||
        rel.target_id.toLowerCase().includes(q) ||
        rel.relationship_type.toLowerCase().includes(q)
      );
    });
  }, [relationshipCategory, searchQuery]);

  return (
    <div className="w-full space-y-4 text-viz-text">
      <div className="space-y-4 w-full">
        {/* Breadcrumb Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border-divider font-mono font-semibold uppercase text-viz-neutral">
              Entity Dossier
            </span>
            <span className="text-viz-neutral">/</span>
            <Link href="/entities" className="text-viz-neutral hover:text-viz-primary font-medium">
              Entities
            </Link>
            <span className="text-viz-neutral">/</span>
            <span className="font-mono font-bold text-viz-text">{params?.id || entity.id}</span>
            <span className="ml-2 px-2 py-0.5 rounded-full bg-tone-danger-strong-bg text-tone-danger-strong-text font-bold inline-flex items-center gap-1">
              <ShieldAlert className="w-3.5 h-3.5 text-error" />
              State 6: High Risk Mule Node
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-2.5 py-1 rounded bg-surface border border-border-divider text-viz-neutral flex items-center gap-1.5 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
              <span>Real-Time Intelligence: Active</span>
            </span>
          </div>
        </div>

        {/* Primary Entity Header Card */}
        <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
            <div className="flex items-start gap-3.5 min-w-0">
              <div className="w-12 h-12 rounded-xl bg-[#0B6256]/10 text-viz-primary flex items-center justify-center shrink-0">
                <Landmark className="w-6 h-6" />
              </div>
              <div className="flex flex-col min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs uppercase tracking-wider font-semibold text-viz-neutral">
                    {entity.type}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle text-[11px] text-viz-neutral">
                    PSP: {entity.psp}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-[#E7EDF4] text-[#1A446C] text-[11px] font-medium">
                    §4.11 Zero-PII Enforced
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2 mt-1">
                  <h1 className="text-2xl font-bold font-mono tracking-tight text-viz-text">
                    {isRevealed ? entity.identifier : entity.identifier}
                  </h1>
                  <button
                    onClick={handleCopy}
                    className="p-1 rounded hover:bg-surface-subtle text-viz-neutral hover:text-viz-text transition-colors"
                    title="Copy identifier"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  {copied && <span className="text-xs text-viz-primary font-medium">Copied!</span>}

                  <button
                    onClick={() => setIsRevealed(!isRevealed)}
                    className="px-2 h-7 rounded bg-surface-subtle hover:bg-surface-container-high text-xs font-medium text-viz-text flex items-center gap-1 border border-border-divider transition-colors"
                  >
                    {isRevealed ? <EyeOff className="w-3.5 h-3.5 text-viz-neutral" /> : <Eye className="w-3.5 h-3.5 text-viz-neutral" />}
                    <span>{isRevealed ? "Hide PII" : "Audit Reveal"}</span>
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-viz-neutral">
                  <span className="flex items-center gap-1 text-viz-text font-medium">
                    <Building className="w-3.5 h-3.5 text-viz-primary" />
                    {entity.branch}
                  </span>
                  <span>•</span>
                  <span>IFSC: {entity.ifsc}</span>
                  <span>•</span>
                  <span>
                    Holder: <strong className="text-viz-text font-mono">{isRevealed ? entity.holder_real : entity.holder_mask}</strong>
                  </span>
                </div>

                <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded bg-surface-subtle border border-border-divider text-xs">
                  <span className="w-2 h-2 rounded-full bg-viz-warning shrink-0" />
                  <span className="font-semibold text-[#4A3306]">Observed Classification:</span>
                  <span className="text-viz-neutral">{entity.status_rule}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex flex-wrap lg:flex-col xl:flex-row items-stretch lg:items-end gap-2 shrink-0">
              <Link
                href="/investigate"
                className="px-3 h-8 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-xs"
              >
                <Search className="w-3.5 h-3.5" />
                <span>Investigate (A07)</span>
              </Link>
              <Link
                href="/graph"
                className="px-3 h-8 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors"
              >
                <Share2 className="w-3.5 h-3.5 text-viz-neutral" />
                <span>Graph Topology (A08)</span>
              </Link>
              <button className="px-3 h-8 rounded bg-tone-danger-bg hover:bg-tone-danger-strong-bg text-tone-danger-text text-xs font-bold flex items-center justify-center gap-1.5 transition-colors">
                <Gavel className="w-3.5 h-3.5 text-error" />
                <span>Section 102 CrPC Lien Notice</span>
              </button>
            </div>
          </div>

          {/* Observation Metric Chips */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4 pt-3 border-t border-border-divider text-xs">
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">First Observed</span>
              <span className="font-semibold text-viz-text mt-0.5 block">{formatDateTime(entity.first_observed)}</span>
              <span className="text-[10px] text-viz-neutral">Via BESCOM Smish Pool</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Last Activity</span>
              <span className="font-semibold text-error mt-0.5 block">{formatDateTime(entity.last_observed)}</span>
              <span className="text-[10px] text-error font-medium">Active Egress Window</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Corroborated Incidents</span>
              <span className="font-semibold text-viz-text mt-0.5 block">{entity.corroborated_cases} Cases Validated</span>
              <span className="text-[10px] text-viz-primary">100% telemetry match</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Syndicate Cluster</span>
              <Link href={`/campaigns/camp-power-urgent`} className="font-semibold text-viz-primary mt-0.5 block hover:underline">
                {entity.syndicate_id}
              </Link>
              <span className="text-[10px] text-viz-neutral truncate block">{entity.syndicate_name}</span>
            </div>
            <div>
              <span className="text-[11px] text-viz-neutral uppercase block font-semibold">Active Lien Status</span>
              <span className="font-semibold font-mono text-viz-primary mt-0.5 block">
                ₹{entity.lien_placed.toLocaleString("en-IN")}
              </span>
              <span className="text-[10px] text-viz-neutral">Served to Axis Bank</span>
            </div>
          </div>
        </div>

        {/* 7 Canonical Entity Tabs */}
        <div className="bg-surface rounded-lg p-1 border border-border-divider flex items-center gap-1 overflow-x-auto text-xs">
          {[
            { key: "overview", label: "1. Overview" },
            { key: "timeline", label: "2. Forensic Timeline (18)" },
            { key: "relationships", label: "3. Direct Relationships (12)" },
            { key: "campaigns", label: "4. Correlated Campaigns (2)" },
            { key: "evidence", label: "5. Evidence & Banking Receipts (14)" },
            { key: "resolution", label: "6. Resolution & Merge History" },
            { key: "disputes", label: "7. Disputes & Legal Notices" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-1.5 rounded-md font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.key
                  ? "bg-viz-primary text-white font-semibold shadow-xs"
                  : "text-viz-neutral hover:text-viz-text hover:bg-surface-subtle"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ========================================================================= */}
        {/* TAB 1: OVERVIEW */}
        {/* ========================================================================= */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Left Column (7 cols): Behavioral Pattern & Financial Rail */}
            <div className="lg:col-span-7 space-y-4">
              {/* Pattern Card */}
              <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-viz-primary" />
                    <h2 className="text-sm font-bold text-viz-text">Behavioral Pattern &amp; Role Vector</h2>
                  </div>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-mono font-medium">
                    Model: TTP-FLOW-v4
                  </span>
                </div>

                <div className="p-3 rounded bg-surface-subtle border border-border-divider flex items-start gap-3">
                  <div className="w-8 h-8 rounded bg-tone-danger-bg text-tone-danger-text flex items-center justify-center shrink-0 font-bold">
                    <ShieldAlert className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-viz-text">Hypothesis: Primary Cash-Out / Mule Aggregator</span>
                      <span className="font-bold text-error font-mono">Confidence: {entity.confidence}%</span>
                    </div>
                    <p className="text-xs text-viz-neutral mt-1 leading-relaxed">
                      Node exhibits classic high-velocity funneling topology. Rapid ₹10 decoy micro-authorizations trigger secondary consumer mandates, siphoning rounded ticket values into secondary layer accounts within minutes.
                    </p>
                  </div>
                </div>

                {/* Metrics Strip */}
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded bg-surface-subtle border border-border-divider">
                    <span className="text-[10px] uppercase font-bold text-viz-neutral block">Average Ingress Ticket</span>
                    <div className="text-base font-bold font-mono text-viz-text mt-0.5">₹{entity.avg_ticket.toLocaleString("en-IN")}</div>
                    <span className="text-[10px] text-viz-neutral">Range: ₹9,800 – ₹14,200</span>
                  </div>
                  <div className="p-3 rounded bg-surface-subtle border border-border-divider">
                    <span className="text-[10px] uppercase font-bold text-viz-neutral block">Total Corroborated Ingress</span>
                    <div className="text-base font-bold font-mono text-viz-primary mt-0.5">₹{entity.total_ingress.toLocaleString("en-IN")}</div>
                    <span className="text-[10px] text-viz-neutral">14 settled consumer debits</span>
                  </div>
                  <div className="p-3 rounded bg-surface-subtle border border-border-divider">
                    <span className="text-[10px] uppercase font-bold text-viz-neutral block">Egress Velocity</span>
                    <div className="text-base font-bold font-mono text-error mt-0.5">18 mins</div>
                    <span className="text-[10px] text-error font-medium">To P2P USDT Counterparty</span>
                  </div>
                </div>
              </div>

              {/* Financial Rail & Account Artifacts */}
              <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <Landmark className="w-4 h-4 text-viz-primary" />
                    <h2 className="text-sm font-bold text-viz-text">Financial Rail &amp; Account Artifacts</h2>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text font-bold text-xs">
                    Notice Form 1930 Active
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded bg-surface-subtle border border-border-divider space-y-2">
                    <span className="text-[11px] font-bold uppercase text-viz-neutral block">Bank Node Specifications</span>
                    <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                      <span className="text-viz-neutral">Acquiring PSP:</span>
                      <span className="font-semibold text-viz-text">{entity.psp}</span>
                    </div>
                    <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                      <span className="text-viz-neutral">Target VPA:</span>
                      <code className="font-mono text-viz-text font-semibold">{entity.identifier}</code>
                    </div>
                    <div className="flex justify-between items-center py-1">
                      <span className="text-viz-neutral">IFSC &amp; Branch:</span>
                      <span className="font-medium text-viz-text">{entity.ifsc}</span>
                    </div>
                  </div>

                  <div className="p-3 rounded bg-surface-subtle border border-border-divider space-y-2">
                    <span className="text-[11px] font-bold uppercase text-viz-neutral block">Regulatory Restraint &amp; Status</span>
                    <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                      <span className="text-viz-neutral">Freezing Order:</span>
                      <span className="font-bold text-error">Served (14m ago)</span>
                    </div>
                    <div className="flex justify-between items-center py-1 border-b border-border-divider/50">
                      <span className="text-viz-neutral">Lien Placed:</span>
                      <span className="font-mono font-bold text-viz-primary">₹{entity.lien_placed.toLocaleString("en-IN")}</span>
                    </div>
                    <div className="flex justify-between items-center py-1">
                      <span className="text-viz-neutral">CFCFRMS Ref:</span>
                      <code className="font-mono text-viz-primary font-bold">{entity.cfr_ref}</code>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column (5 cols): 1-Hop Relationship Network & Direct Links */}
            <div className="lg:col-span-5 space-y-4">
              <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <Share2 className="w-4 h-4 text-viz-primary" />
                    <h2 className="text-sm font-bold text-viz-text">1-Hop Relationship Network</h2>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-medium">
                    {entity.direct_edges.length} Bound Edges
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  {entity.direct_edges.map((edge, idx) => (
                    <div key={idx} className="p-3 rounded bg-surface-subtle border border-border-divider flex items-center justify-between">
                      <div>
                        <span className="text-[10px] uppercase font-bold text-viz-neutral block">{edge.type}</span>
                        <code className="text-xs font-mono font-bold text-viz-text mt-0.5 block">{edge.identifier}</code>
                        <span className="text-[11px] text-viz-neutral">{edge.label}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-[11px] font-bold">
                        {edge.status}
                      </span>
                    </div>
                  ))}
                </div>

                <Link
                  href="/graph"
                  className="w-full h-8 px-3 rounded bg-surface-subtle hover:bg-surface-container-high border border-border-control text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors"
                >
                  <span>Launch Interactive Graph Canvas</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: FORENSIC TIMELINE (18) */}
        {/* ========================================================================= */}
        {activeTab === "timeline" && (
          <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-divider">
              <div>
                <div className="flex items-center gap-2">
                  <History className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-base font-bold text-viz-text">Forensic Chronology &amp; Telemetry Trail</h2>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-mono text-xs font-bold">
                    18 Synchronized Events
                  </span>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">
                  Full multi-source audit trail reconstructing SIM binding, fake KYC, victim debits, and subsequent Axis Bank lien execution.
                </p>
              </div>

              {/* Filters */}
              <div className="flex items-center gap-2">
                <select
                  value={timelineCategory}
                  onChange={(e) => setTimelineCategory(e.target.value)}
                  className="h-7 px-2.5 bg-surface-subtle border border-border-divider rounded text-xs text-viz-text focus:outline-none"
                >
                  <option value="ALL">All Categories</option>
                  <option value="TRANSACTION">Transactions Only</option>
                  <option value="TELEMETRY">Telemetry &amp; Towers</option>
                  <option value="INTAKE">Citizen &amp; DLT Intake</option>
                  <option value="LEGAL">Legal &amp; FIR</option>
                  <option value="ENFORCEMENT">Enforcement Actions</option>
                </select>
              </div>
            </div>

            {/* Timeline Stream */}
            <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border-divider">
              {filteredTimeline.map((evt) => (
                <div key={evt.id} className="relative group">
                  {/* Dot */}
                  <div className={`absolute -left-6 top-1.5 w-3 h-3 rounded-full border-2 border-surface ${
                    evt.badgeTone === "danger"
                      ? "bg-error"
                      : evt.badgeTone === "warning"
                      ? "bg-viz-warning"
                      : evt.badgeTone === "success"
                      ? "bg-viz-primary"
                      : "bg-viz-neutral"
                  }`} />

                  {/* Card */}
                  <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider hover:border-viz-primary/40 transition-colors">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-viz-text">{evt.id}</span>
                        <span className="text-[11px] font-semibold text-viz-neutral uppercase tracking-wider px-1.5 py-0.2 rounded bg-surface border border-border-divider">
                          {evt.category}
                        </span>
                        <span className="font-semibold text-xs text-viz-text">{evt.title}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        {evt.quantum && (
                          <span className="font-mono font-bold text-error">₹{evt.quantum.toLocaleString("en-IN")}</span>
                        )}
                        <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-surface border border-border-divider text-viz-neutral">
                          {evt.badge}
                        </span>
                        <span className="text-viz-neutral font-mono text-[11px]">
                          {formatDateTime(evt.timestamp)}
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-viz-neutral mt-1 leading-relaxed">{evt.description}</p>
                    <div className="mt-2 pt-2 border-t border-border-divider/50 flex items-center justify-between text-[11px] text-viz-neutral">
                      <span>Source: <strong className="text-viz-text">{evt.source}</strong></span>
                      <span className="font-mono">Merkle Validated §65B</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: DIRECT RELATIONSHIPS (12) */}
        {/* ========================================================================= */}
        {activeTab === "relationships" && (
          <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-divider">
              <div>
                <div className="flex items-center gap-2">
                  <Share2 className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-base font-bold text-viz-text">Direct 1-Hop &amp; 2-Hop Relationship Topology</h2>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-mono text-xs font-bold">
                    12 Bound Entity Edges
                  </span>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">
                  Graph-correlated telephony anchors, intermediary bank VPAs, DNS hosts, and exit cryptocurrency rails bound to this entity.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={relationshipCategory}
                  onChange={(e) => setRelationshipCategory(e.target.value)}
                  className="h-7 px-2.5 bg-surface-subtle border border-border-divider rounded text-xs text-viz-text focus:outline-none"
                >
                  <option value="ALL">All Relationships</option>
                  <option value="TELEPHONY">Telephony Anchors</option>
                  <option value="BANKING">Banking Rails &amp; VPAs</option>
                  <option value="INFRASTRUCTURE">Phishing &amp; APKs</option>
                  <option value="CRYPTO_EXIT">Cryptocurrency Exits</option>
                </select>
                <Link
                  href="/graph"
                  className="h-7 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold inline-flex items-center gap-1 transition-colors"
                >
                  <span>Open Full Canvas</span>
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
            </div>

            {/* Grid of 12 Relationships */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {filteredRelationships.map((rel) => {
                const IconComponent = rel.icon;
                return (
                  <div
                    key={rel.id}
                    className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider hover:border-viz-primary/40 flex flex-col justify-between space-y-2 transition-colors"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <div className="w-6 h-6 rounded bg-surface flex items-center justify-center text-viz-primary border border-border-divider">
                            <IconComponent className="w-3.5 h-3.5" />
                          </div>
                          <span className="text-[10px] uppercase font-bold text-viz-neutral">{rel.category}</span>
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text">
                          {rel.status}
                        </span>
                      </div>

                      <h3 className="text-xs font-bold text-viz-text mt-2 line-clamp-1">{rel.target_name}</h3>
                      <code className="text-[11px] font-mono text-viz-primary block mt-0.5">{rel.target_id}</code>
                      <p className="text-[11px] text-viz-neutral mt-1">Role: <strong className="text-viz-text">{rel.relationship_type}</strong></p>
                    </div>

                    <div className="pt-2 border-t border-border-divider/50 space-y-1 text-[11px]">
                      <div className="flex justify-between items-center text-viz-neutral">
                        <span>Volume: <strong className="text-viz-text font-mono">{rel.volume}</strong></span>
                        <span className="font-mono text-viz-primary">{rel.hop_distance}-Hop ({rel.confidence}%)</span>
                      </div>
                      <div className="flex justify-between items-center text-[10px] text-viz-neutral">
                        <span>Span: {rel.first_seen} → {rel.last_seen}</span>
                        <span className="uppercase font-semibold text-viz-primary">{rel.flow_direction}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: CORRELATED CAMPAIGNS (2) */}
        {/* ========================================================================= */}
        {activeTab === "campaigns" && (
          <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border-divider">
              <div>
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-base font-bold text-viz-text">Correlated Syndicate Campaigns</h2>
                  <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text font-mono text-xs font-bold">
                    2 Active Syndicates
                  </span>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">
                  Syndicates attributing util-power-84920@okaxis as a primary or secondary laundering collection point.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {CORRELATED_CAMPAIGNS.map((camp) => (
                <div
                  key={camp.id}
                  className="p-5 rounded-xl bg-surface-subtle border border-border-divider space-y-4 hover:border-viz-primary/40 transition-colors"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-viz-primary">{camp.code}</span>
                        <span className="px-2 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text font-bold text-[10px] uppercase">
                          {camp.status}
                        </span>
                        <span className="text-[11px] font-mono text-viz-neutral">Overlap: {camp.overlap_score}%</span>
                      </div>
                      <h3 className="text-sm font-bold text-viz-text mt-1.5">{camp.title}</h3>
                    </div>
                    <Link
                      href={`/campaigns/${camp.id}`}
                      className="px-2.5 py-1 bg-viz-primary hover:bg-[#00483f] text-white rounded text-xs font-semibold inline-flex items-center gap-1 transition-colors shrink-0"
                    >
                      <span>Open Workspace</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <p className="text-xs text-viz-neutral leading-relaxed">{camp.description}</p>

                  {/* Quantitative Strip */}
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="p-2.5 rounded bg-surface border border-border-divider">
                      <span className="text-[10px] uppercase font-bold text-viz-neutral block">Total Loss</span>
                      <span className="font-mono font-bold text-error text-sm">
                        ₹{(camp.total_loss / 100000).toFixed(1)} Lakhs
                      </span>
                    </div>
                    <div className="p-2.5 rounded bg-surface border border-border-divider">
                      <span className="text-[10px] uppercase font-bold text-viz-neutral block">Lien Placed</span>
                      <span className="font-mono font-bold text-viz-primary text-sm">
                        ₹{(camp.lien_recovered / 100000).toFixed(1)} Lakhs
                      </span>
                    </div>
                    <div className="p-2.5 rounded bg-surface border border-border-divider">
                      <span className="text-[10px] uppercase font-bold text-viz-neutral block">Victims</span>
                      <span className="font-mono font-bold text-viz-text text-sm">{camp.victims_count} Citizens</span>
                    </div>
                  </div>

                  {/* Shared IOCs */}
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-viz-neutral block mb-1.5">
                      Shared Indicators of Compromise (IOCs)
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {camp.shared_iocs.map((ioc) => (
                        <span key={ioc} className="px-2 py-0.5 rounded bg-surface border border-border-divider font-mono text-[11px] text-viz-text">
                          {ioc}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-border-divider flex items-center justify-between text-[11px] text-viz-neutral">
                    <span>Investigating Officer: <strong className="text-viz-text">{camp.lead_officer}</strong></span>
                    <span>Corridor: {camp.jurisdictions.join(", ")}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 5: EVIDENCE & BANKING RECEIPTS (14) */}
        {/* ========================================================================= */}
        {activeTab === "evidence" && (
          <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-divider">
              <div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-base font-bold text-viz-text">Forensic Repository &amp; Banking Receipts</h2>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-mono text-xs font-bold">
                    14 Corroborated Artifacts
                  </span>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">
                  Digitally signed evidence packages with SHA-256 Merkle proofs admissible under Section 65B Indian Evidence Act / Section 63 BSA 2023.
                </p>
              </div>

              <button className="h-8 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-xs">
                <FileDown className="w-3.5 h-3.5" />
                <span>Export Full Evidence Bundle (ZIP)</span>
              </button>
            </div>

            {/* Evidence Table */}
            <div className="w-full overflow-x-auto border border-border-divider rounded-lg">
              <table className="w-full text-left border-collapse text-xs select-text">
                <thead>
                  <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                    <th className="px-3 font-semibold">Ref &amp; Title</th>
                    <th className="px-3 font-semibold">Category</th>
                    <th className="px-3 font-semibold">Format &amp; Size</th>
                    <th className="px-3 font-semibold">SHA-256 Fingerprint</th>
                    <th className="px-3 font-semibold">Timestamp</th>
                    <th className="px-3 font-semibold">Certification</th>
                    <th className="px-3 text-right font-semibold">Download</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-divider text-viz-text">
                  {FORENSIC_EVIDENCE.map((item) => (
                    <tr key={item.id} className="h-10 hover:bg-surface-subtle transition-colors">
                      <td className="px-3 py-2">
                        <div className="flex flex-col">
                          <span className="font-semibold text-viz-text">{item.title}</span>
                          <span className="font-mono text-[10px] text-viz-primary">{item.ref}</span>
                        </div>
                      </td>
                      <td className="px-3">
                        <span className="px-1.5 py-0.5 rounded bg-surface-subtle border border-border-divider text-[10px] font-mono uppercase font-bold text-viz-neutral">
                          {item.type}
                        </span>
                      </td>
                      <td className="px-3 text-viz-neutral text-[11px]">
                        {item.format} ({item.size})
                      </td>
                      <td className="px-3 font-mono text-[11px] text-viz-neutral">
                        <code>{item.hash}</code>
                      </td>
                      <td className="px-3 text-[11px] text-viz-neutral whitespace-nowrap">
                        {formatDateTime(item.timestamp)}
                      </td>
                      <td className="px-3">
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[10px] font-semibold">
                          <ShieldCheck className="w-3 h-3" />
                          {item.status}
                        </span>
                      </td>
                      <td className="px-3 text-right whitespace-nowrap">
                        <button className="p-1.5 rounded hover:bg-surface border border-border-divider text-viz-primary hover:text-viz-primary transition-colors inline-flex items-center gap-1">
                          <Download className="w-3.5 h-3.5" />
                          <span className="text-[11px] font-medium">Download</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 6: RESOLUTION & MERGE HISTORY */}
        {/* ========================================================================= */}
        {activeTab === "resolution" && (
          <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-border-divider">
              <div>
                <div className="flex items-center gap-2">
                  <GitMerge className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-base font-bold text-viz-text">Entity Resolution &amp; Deduplication Audit</h2>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-mono text-xs font-bold">
                    Jaccard Index: 0.94
                  </span>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">
                  Audit log of automatic and analyst-supervised entity mergers, cluster bindings, and risk score progression.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text transition-colors">
                  Rollback Recent Merge
                </button>
                <button className="h-8 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold transition-colors shadow-xs">
                  Propose New Alias Binding
                </button>
              </div>
            </div>

            {/* Merged Aliases */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-viz-neutral">
                Correlated Aliases Bound to Node
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-viz-text">Telephony MSISDN</span>
                    <span className="font-mono text-viz-primary font-bold">Score 0.98</span>
                  </div>
                  <code className="text-xs font-mono text-viz-text block">+91 98******10</code>
                  <p className="text-[11px] text-viz-neutral">Matched via SIM registration SMS and Axis Bank OTP delivery records.</p>
                </div>
                <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-viz-text">Bank Account Ledger</span>
                    <span className="font-mono text-viz-primary font-bold">Score 1.00</span>
                  </div>
                  <code className="text-xs font-mono text-viz-text block">AXIS-9210100******84</code>
                  <p className="text-[11px] text-viz-neutral">Direct 1:1 primary underlying savings bank ledger account.</p>
                </div>
                <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-viz-text">Campaign Dropper Anchor</span>
                    <span className="font-mono text-viz-primary font-bold">Score 0.94</span>
                  </div>
                  <code className="text-xs font-mono text-viz-text block">bescom-bill-renew.in</code>
                  <p className="text-[11px] text-viz-neutral">Target redirection destination hardcoded in reverse-engineered APK.</p>
                </div>
              </div>
            </div>

            {/* Risk Progression Ledger */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-viz-neutral">
                Risk State Transition History
              </h3>
              <div className="border border-border-divider rounded-lg divide-y divide-border-divider text-xs">
                <div className="p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-viz-neutral">21 Oct 2026, 09:15</span>
                    <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral font-semibold">State 1: Intake</span>
                    <span className="text-viz-neutral">First registered in database via automated honey-trap intake.</span>
                  </div>
                  <span className="text-viz-neutral text-[11px]">System Sentinel</span>
                </div>
                <div className="p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-viz-neutral">22 Oct 2026, 10:14</span>
                    <span className="px-2 py-0.5 rounded bg-tone-warning-bg text-tone-warning-text font-semibold">State 3: Velocity Spike</span>
                    <span className="text-viz-neutral">Parameter tampering detection triggered automatic alert §7 A10.</span>
                  </div>
                  <span className="text-viz-neutral text-[11px]">Model Engine v4</span>
                </div>
                <div className="p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-viz-neutral">23 Oct 2026, 09:35</span>
                    <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text font-semibold">State 5: Syndicate Linked</span>
                    <span className="text-viz-neutral">Graph correlation engine connected node to State Electricity Cutoff #UTL-8490.</span>
                  </div>
                  <span className="text-viz-neutral text-[11px]">GNN Reasoner</span>
                </div>
                <div className="p-3 flex items-center justify-between bg-tone-danger-bg/20">
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-error">24 Oct 2026, 14:10</span>
                    <span className="px-2 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text font-bold">State 6: Lien Enforced</span>
                    <span className="text-viz-text font-medium">Formal Section 102 CrPC Lien served; ₹24,350 frozen in Axis Bank.</span>
                  </div>
                  <span className="text-viz-text font-semibold text-[11px]">Inspector Raghavendra M.</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 7: DISPUTES & LEGAL NOTICES */}
        {/* ========================================================================= */}
        {activeTab === "disputes" && (
          <div className="w-full bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-divider">
              <div>
                <div className="flex items-center gap-2">
                  <Scale className="w-4 h-4 text-viz-primary" />
                  <h2 className="text-base font-bold text-viz-text">Statutory Notices &amp; Legal Adjudication Status</h2>
                  <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text font-mono text-xs font-bold">
                    BNSS 2023 &amp; IT Act 2000
                  </span>
                </div>
                <p className="text-xs text-viz-neutral mt-0.5">
                  Formal notices issued under statutory provisions, bank lien freezing orders, and citizen dispute hearing filings.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button className="h-8 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-xs">
                  <Download className="w-3.5 h-3.5" />
                  <span>Generate Certified §65B Packet</span>
                </button>
              </div>
            </div>

            {/* 3 Statutory Legal Notices */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral">Order #01</span>
                  <span className="px-2 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text text-[10px] font-bold">
                    ENFORCED
                  </span>
                </div>
                <div>
                  <h3 className="text-xs font-bold text-viz-text">Section 102 CrPC / §106 BNSS</h3>
                  <p className="text-[11px] text-viz-primary font-mono mt-0.5 font-semibold">Ref: KA-CY-2026-N102-0941</p>
                  <p className="text-xs text-viz-neutral mt-1 leading-relaxed">
                    Formal statutory restraint served on Axis Bank Nodal Officer demanding total freeze on all egress channels.
                  </p>
                </div>
                <div className="pt-2 border-t border-border-divider/50 flex justify-between items-center text-[11px]">
                  <span className="text-viz-neutral">Frozen Quantum:</span>
                  <span className="font-mono font-bold text-error">₹24,350.00</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral">Order #02</span>
                  <span className="px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[10px] font-bold">
                    COMPLIED
                  </span>
                </div>
                <div>
                  <h3 className="text-xs font-bold text-viz-text">Section 91 CrPC Production Notice</h3>
                  <p className="text-[11px] text-viz-primary font-mono mt-0.5 font-semibold">Ref: KA-CY-2026-N91-0318</p>
                  <p className="text-xs text-viz-neutral mt-1 leading-relaxed">
                    Notice served to Bharti Airtel Nodal Officer demanding tower CDRs and subscriber voter ID application form.
                  </p>
                </div>
                <div className="pt-2 border-t border-border-divider/50 flex justify-between items-center text-[11px]">
                  <span className="text-viz-neutral">Response Time:</span>
                  <span className="font-semibold text-viz-text">4h 12m</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-viz-neutral">Order #03</span>
                  <span className="px-2 py-0.5 rounded bg-tone-warning-bg text-tone-warning-text text-[10px] font-bold">
                    HEARING LISTED
                  </span>
                </div>
                <div>
                  <h3 className="text-xs font-bold text-viz-text">Section 79A IT Act Examiner Certificate</h3>
                  <p className="text-[11px] text-viz-primary font-mono mt-0.5 font-semibold">Ref: CERT-79A-BCP-142</p>
                  <p className="text-xs text-viz-neutral mt-1 leading-relaxed">
                    Digital evidence authenticity certificate prepared for 1st Additional Chief Metropolitan Magistrate Bengaluru.
                  </p>
                </div>
                <div className="pt-2 border-t border-border-divider/50 flex justify-between items-center text-[11px]">
                  <span className="text-viz-neutral">Hearing Date:</span>
                  <span className="font-semibold text-viz-warning">26 Oct 2026</span>
                </div>
              </div>
            </div>

            {/* Disputed Lien Challenge Details */}
            <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-viz-warning" />
                  <h3 className="text-xs font-bold text-viz-text">Account Holder Dispute Appeal (Rohit Dasgupta)</h3>
                </div>
                <span className="px-2 py-0.5 rounded bg-surface border border-border-divider text-xs text-viz-neutral">
                  Filing Ref: DISP-2026-OCT-891
                </span>
              </div>
              <p className="text-xs text-viz-neutral leading-relaxed">
                Account holder filed an emergency appeal with the Axis Bank Grievance Redressal Officer claiming their phone was infected with rogue malware after downloading a bill viewer, and that the ₹1,48,200 funneling occurred without their explicit PIN authorization. Police Cyber Cell has impounded device for forensic extraction.
              </p>
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-border-divider/50">
                <button className="h-7 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold transition-colors">
                  Schedule IO Interrogation
                </button>
                <button className="h-7 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text transition-colors">
                  Download Impounded Handset Extraction Report
                </button>
                <button className="h-7 px-3 rounded bg-tone-danger-strong-bg hover:bg-[#f0c3bf] text-tone-danger-strong-text text-xs font-bold transition-colors">
                  Reject Appeal &amp; Forward to Charge Sheet
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
