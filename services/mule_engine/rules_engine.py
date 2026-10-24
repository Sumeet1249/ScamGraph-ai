"""Interpretable Baseline Rules Engine for Mule Risk Detection.

Evaluates behavioral features against transparent, configurable heuristic thresholds.
Generates named rule hits, severity weights, and explainable reason codes.
"""

from __future__ import annotations

from typing import List, Tuple

from packages.schemas.mule import MuleFeatureVector, MuleRuleHit


class MuleRulesEngine:
    """Deterministic, transparent behavioral rules evaluator."""

    @classmethod
    def evaluate(cls, features: MuleFeatureVector) -> Tuple[float, List[MuleRuleHit]]:
        """Evaluate feature vector against baseline rules.
        
        Returns:
            Tuple of (aggregate_rule_risk_score, list_of_triggered_rules)
        """
        hits: List[MuleRuleHit] = []
        raw_weighted_score = 0.0

        # Rule 1: High 1-Hour Velocity Burst
        if features.f01_velocity_1h_count >= 5:
            weight = min(0.35, 0.15 + (features.f01_velocity_1h_count - 5) * 0.03)
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_VELOCITY_BURST_1H",
                    name="1-Hour Rapid Velocity Burst",
                    description=f"{features.f01_velocity_1h_count} transactions recorded in a single 1-hour window.",
                    severity="HIGH" if features.f01_velocity_1h_count >= 8 else "MEDIUM",
                    weight=round(weight, 3),
                    trigger_value=features.f01_velocity_1h_count,
                )
            )
            raw_weighted_score += weight

        # Rule 2: Complete Volume Turnover (Churn / In-and-Out Pass-Through)
        if 0.85 <= features.f03_volume_turnover_ratio <= 1.15 and features.f02_velocity_24h_count >= 2:
            weight = 0.30
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_FULL_VOLUME_TURNOVER",
                    name="Complete Fund Turnover (Pass-Through)",
                    description=f"Debited volume closely matches credited volume ({int(features.f03_volume_turnover_ratio * 100)}% turnover).",
                    severity="HIGH",
                    weight=weight,
                    trigger_value=features.f03_volume_turnover_ratio,
                )
            )
            raw_weighted_score += weight

        # Rule 3: Rapid Fund Extraction / Short Dwell Time (<= 10 minutes)
        if (0 < features.f04_dwell_time_seconds_avg <= 600) or features.f05_rapid_churn_ratio >= 0.3:
            weight = 0.40
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_RAPID_PASS_THROUGH",
                    name="Rapid Fund Churn (<= 10 Min Dwell Time)",
                    description=f"Funds drained within {int(features.f04_dwell_time_seconds_avg)}s on average ({int(features.f05_rapid_churn_ratio * 100)}% churn).",
                    severity="CRITICAL",
                    weight=weight,
                    trigger_value=features.f04_dwell_time_seconds_avg,
                )
            )
            raw_weighted_score += weight


        # Rule 4: Fan-In Aggregation (Multiple victims -> single account)
        if features.f07_fan_in_count >= 3:
            weight = min(0.35, 0.20 + (features.f07_fan_in_count - 3) * 0.05)
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_FAN_IN_CONVERGENCE",
                    name="Fan-In Multi-Source Inflow",
                    description=f"{features.f07_fan_in_count} distinct unique senders converging on account.",
                    severity="HIGH",
                    weight=round(weight, 3),
                    trigger_value=features.f07_fan_in_count,
                )
            )
            raw_weighted_score += weight

        # Rule 5: Fan-Out Dispersal (Single account -> multiple destinations)
        if features.f08_fan_out_count >= 3:
            weight = min(0.30, 0.15 + (features.f08_fan_out_count - 3) * 0.04)
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_FAN_OUT_DISPERSAL",
                    name="Fan-Out Layering Dispersal",
                    description=f"Dispersing funds to {features.f08_fan_out_count} distinct destination accounts.",
                    severity="HIGH",
                    weight=round(weight, 3),
                    trigger_value=features.f08_fan_out_count,
                )
            )
            raw_weighted_score += weight

        # Rule 6: New Account Burst / High Dormancy Jump
        if (features.f10_account_age_days is not None and features.f10_account_age_days <= 30) and features.f11_dormancy_burst_score >= 5.0:
            weight = 0.35
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_NEW_ACCOUNT_BURST",
                    name="New Account High-Volume Burst",
                    description=f"Account age is {features.f10_account_age_days} days with {features.f11_dormancy_burst_score}x sudden activity surge.",
                    severity="HIGH",
                    weight=weight,
                    trigger_value=features.f11_dormancy_burst_score,
                )
            )
            raw_weighted_score += weight

        # Rule 7: Immediate Near-Zero Balance Extraction
        if features.f14_balance_extraction_ratio >= 0.70:
            weight = 0.25
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_ZERO_BALANCE_EXTRACTION",
                    name="Complete Post-Credit Balance Depletion",
                    description=f"{int(features.f14_balance_extraction_ratio * 100)}% of debits leave the account balance near zero.",
                    severity="MEDIUM",
                    weight=weight,
                    trigger_value=features.f14_balance_extraction_ratio,
                )
            )
            raw_weighted_score += weight

        # Rule 8: Round-Amount Chunking / Structuring
        if features.f13_round_chunking_detected:
            weight = 0.20
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_STRUCTURING_CHUNKING",
                    name="Threshold Skimming / Round Chunking",
                    description="Detected structured transactions (e.g. ₹9,999, ₹49,999 or clean ₹10,000 increments).",
                    severity="MEDIUM",
                    weight=weight,
                    trigger_value=True,
                )
            )
            raw_weighted_score += weight

        # Rule 9: Micro-Test Credit Followed by Large Spike
        if features.f15_micro_test_followed_by_spike:
            weight = 0.30
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_MICRO_TEST_SPIKE",
                    name="Micro-Test Validation Inflow",
                    description="Micro credit (₹1-₹10) immediately followed by high-value credit inflow.",
                    severity="HIGH",
                    weight=weight,
                    trigger_value=True,
                )
            )
            raw_weighted_score += weight

        # Rule 10: Registry Match Corroboration
        if features.f19_registry_match_indicator:
            weight = 0.45
            hits.append(
                MuleRuleHit(
                    rule_id="RULE_REGISTRY_CONFIRMED_HIT",
                    name="Confirmed Smart Registry Match",
                    description="Account identifier has a confirmed report in the centralized Smart Registry.",
                    severity="CRITICAL",
                    weight=weight,
                    trigger_value=True,
                )
            )
            raw_weighted_score += weight

        # Sort hits by descending weight
        hits.sort(key=lambda h: h.weight, reverse=True)

        # Exponential risk saturation: 1 - exp(-1.2 * raw_weighted_score)
        import math
        final_score = min(1.0, 1.0 - math.exp(-1.25 * raw_weighted_score))
        return round(final_score, 3), hits

