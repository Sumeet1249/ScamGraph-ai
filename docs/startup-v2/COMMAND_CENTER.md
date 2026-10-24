# Command Center Specification (Prompt 19 / Phase 6A)

## 1. Role & Landing Page Philosophy
The Command Center (`/command`) is the operational landing page for fraud analysts. It directly answers:
**WHAT REQUIRES ATTENTION RIGHT NOW?**

It deliberately rejects vanity metrics (e.g. "Total Scams Checked: 1,000,000") in favor of honest operational telemetry tied directly to active time windows (24h, 7d, 30d):
1. **Active Threat Alerts**: Regional velocity outbreaks, rapid growth signals, and campaign resurgences.
2. **Surging Campaigns**: Syndicates whose incident arrival rates exceed baseline acceleration thresholds.
3. **Pending Review Queue**: Human-in-the-loop candidate merges, supernode disambiguations, and novel variant reviews.
4. **Active Casefiles**: Multi-incident investigation cases currently under active analyst management.
5. **System Intelligence Health**: Continuous monitoring of Knowledge Graph latency, discovery engine throughput, and multimodal processing pipelines.
