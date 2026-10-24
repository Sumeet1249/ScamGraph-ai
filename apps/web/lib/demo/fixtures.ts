import type { CytoscapeGraph } from "@/lib/api/types";

export const demoGraph: CytoscapeGraph = {
  nodes: [
    {
      data: {
        id: "node_msg_1",
        label: "SMS Impersonating SBI",
        node_type: "MESSAGE",
        type: "MESSAGE",
        severity: "HIGH",
        nature: "DIRECTLY_OBSERVED",
        risk_score: 82,
      },
    },
    {
      data: {
        id: "node_url_1",
        label: "sbi-kyc-update.online",
        node_type: "URL",
        type: "URL",
        severity: "CRITICAL",
        nature: "DERIVED",
        risk_score: 94,
      },
    },
    {
      data: {
        id: "node_call_1",
        label: "+91 98765 43210 (Vishing)",
        node_type: "VOICE_CALL",
        type: "VOICE_CALL",
        severity: "HIGH",
        nature: "DIRECTLY_OBSERVED",
        risk_score: 78,
      },
    },
    {
      data: {
        id: "node_otp_1",
        label: "Concurrent Bank OTP",
        node_type: "OTP_EVENT",
        type: "OTP_EVENT",
        severity: "CRITICAL",
        nature: "DIRECTLY_OBSERVED",
        risk_score: 95,
      },
    },
    {
      data: {
        id: "node_vpa_1",
        label: "scammer.cashback@oksbi",
        node_type: "PAYMENT_INTENT",
        type: "PAYMENT_INTENT",
        severity: "CRITICAL",
        nature: "DIRECTLY_OBSERVED",
        risk_score: 91,
      },
    },
    {
      data: {
        id: "node_mule_1",
        label: "Layer-1 Mule Acct (A/c 8921)",
        node_type: "MULE_ACCOUNT",
        type: "MULE_ACCOUNT",
        severity: "CRITICAL",
        nature: "INFERRED",
        risk_score: 88,
      },
    },
  ],
  edges: [
    {
      data: {
        id: "edge_1",
        source: "node_msg_1",
        target: "node_url_1",
        label: "EMBEDS_LINK",
        relationship: "EMBEDS_LINK",
        relation_type: "EMBEDS_LINK",
      },
    },
    {
      data: {
        id: "edge_2",
        source: "node_call_1",
        target: "node_otp_1",
        label: "COINCIDES_WITH",
        relationship: "COINCIDES_WITH",
        relation_type: "COINCIDES_WITH",
      },
    },
    {
      data: {
        id: "edge_3",
        source: "node_url_1",
        target: "node_vpa_1",
        label: "SOLICITS_PAYMENT",
        relationship: "SOLICITS_PAYMENT",
        relation_type: "SOLICITS_PAYMENT",
      },
    },
    {
      data: {
        id: "edge_4",
        source: "node_vpa_1",
        target: "node_mule_1",
        label: "FUNDS_FLOW_TO",
        relationship: "FUNDS_FLOW_TO",
        relation_type: "FUNDS_FLOW_TO",
      },
    },
  ],
};
