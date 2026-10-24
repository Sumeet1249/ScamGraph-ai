"use client";

import { useEffect, useRef, useState } from "react";
import { EmptyState } from "@/components/shared/States";
import { GraphLegend } from "./GraphLegend";
import { GraphNodeDrawer } from "./GraphNodeDrawer";
import type { CytoscapeGraph, CytoscapeNodeData } from "@/lib/api/types";

/**
 * Interactive evidence graph using Cytoscape.js.
 *
 * Phase 1: renders the graph with the new design tokens + node drawer.
 * Phase 4 will add: filters, path highlighting, related-incident expansion,
 * fit/zoom controls. (No invented relationships — uses backend edge data.)
 */
export function EvidenceGraph({ graph }: { graph: CytoscapeGraph | null }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<unknown>(null);
  const [selected, setSelected] = useState<CytoscapeNodeData | null>(null);

  useEffect(() => {
    let mounted = true;

    async function init() {
      if (!containerRef.current || !graph) return;
      const cytoscape = (await import("cytoscape")).default;
      if (!mounted) {
        return;
      }
      if (cyRef.current && typeof (cyRef.current as { destroy: () => void }).destroy === "function") {
        (cyRef.current as { destroy: () => void }).destroy();
      }

      const elements = [
        ...graph.nodes.map((n) => ({ group: "nodes" as const, data: n.data })),
        ...graph.edges.map((e) => ({ group: "edges" as const, data: e.data })),
      ];

      const cy = cytoscape({
        container: containerRef.current,
        elements: elements as never,
        wheelSensitivity: 0.25,
        style: [
          {
            selector: "node",
            style: {
              "background-color": "#261E1A",
              label: "data(label)",
              color: "#EDEBE9",
              "font-size": "10px",
              "text-valign": "bottom",
              "text-margin-y": 5,
              width: 34,
              height: 34,
              "border-width": 2,
              "border-color": "rgba(229, 228, 226, 0.18)",
            },
          },
          { selector: 'node[node_type = "incident"]', style: { "background-color": "#C4B5E8", "border-color": "#D3C7F0", color: "#EDEBE9", width: 44, height: 44, "font-weight": "bold" } },
          { selector: 'node[node_type = "campaign"]', style: { "background-color": "#E38E7C", "border-color": "#EC6B65", width: 46, height: 46, "font-weight": "bold" } },
          { selector: 'node[node_type = "journey_step"]', style: { "background-color": "#A8836B", "border-color": "#CDB3A0" } },
          { selector: 'node[node_type = "message"]', style: { "background-color": "#E5E4E2", "border-color": "#EDEBE9" } },
          { selector: 'node[node_type = "url"]', style: { "background-color": "#7FAFD0", "border-color": "#8FB3C9" } },
          { selector: 'node[node_type = "domain"]', style: { "background-color": "#7DBFAA", "border-color": "#6DC79A" } },
          { selector: 'node[node_type = "upi_handle"]', style: { "background-color": "#D8C36F", "border-color": "#E2BE5C" } },
          { selector: 'node[node_type = "phone"]', style: { "background-color": "#D99DB8", "border-color": "#E2B3C5" } },
          { selector: 'node[severity = "CRITICAL"]', style: { "border-color": "#EC6B65", "border-width": 3 } },
          { selector: 'node[severity = "HIGH"]', style: { "border-color": "#E8924F", "border-width": 3 } },
          {
            selector: "edge",
            style: {
              width: 1.5,
              "line-color": "rgba(229, 228, 226, 0.22)",
              "target-arrow-color": "rgba(229, 228, 226, 0.45)",
              "target-arrow-shape": "triangle",
              "curve-style": "bezier",
              label: "data(label)",
              "font-size": "8px",
              color: "#B9B4B1",
              "text-background-opacity": 0.85,
              "text-background-color": "#120E0C",
              "text-background-padding": "2px",
            },
          },
          { selector: ":selected", style: { "border-color": "#C4B5E8", "border-width": 4, "line-color": "#C4B5E8", "target-arrow-color": "#C4B5E8" } },
        ],
        layout: { name: "breadthfirst", directed: true, padding: 28, spacingFactor: 1.3 },
      });

      cy.on("tap", "node", (evt: { target: { data: () => CytoscapeNodeData } }) => {
        setSelected(evt.target.data());
      });

      cyRef.current = cy;
    }

    init();
    return () => {
      mounted = false;
      const c = cyRef.current as { destroy?: () => void } | null;
      c?.destroy?.();
    };
  }, [graph]);

  if (!graph || graph.nodes.length === 0) {
    return (
      <EmptyState
        title="No graph data yet"
        message="The evidence graph appears once an incident has been investigated through the ScamGraph engine."
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-ink-muted">
          {graph.nodes.length} nodes · {graph.edges.length} relationships
        </div>
        <GraphLegend />
      </div>
      <div className="relative overflow-hidden rounded-xl border border-line bg-elevated">
        <div ref={containerRef} className="h-[460px] w-full" role="img" aria-label="Evidence relationship graph" />
      </div>
      <GraphNodeDrawer node={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
