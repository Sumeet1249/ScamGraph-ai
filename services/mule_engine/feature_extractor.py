"""Mule Intelligence 19 Behavioral Feature Extractor (Module B).

Extracts 19 financial crime and money-mule behavioral patterns inspired by
the publicly documented capabilities of RBIH MuleHunter.ai.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional

from packages.schemas.mule import (
    MuleFeatureVector,
    TransactionDirection,
    TransactionRecord,
)


class MuleFeatureExtractor:
    """Extracts 19 behavioral indicators from account transaction sequence."""

    @classmethod
    def extract_features(
        cls,
        account_id: str,
        transactions: List[TransactionRecord],
        account_age_days: Optional[int] = None,
        historical_avg_daily_volume: Optional[float] = None,
        current_balance: Optional[float] = None,
        linked_vpa_count: int = 1,
        has_registry_match: bool = False,
    ) -> MuleFeatureVector:
        """Extract full 19-dimensional feature vector for an account."""
        now = datetime.now(timezone.utc)
        if not transactions:
            return MuleFeatureVector(
                account_id=account_id,
                evaluated_at=now,
                is_partial_features=True,
            )

        # Sort transactions chronologically
        txns = sorted(transactions, key=lambda t: t.timestamp)

        # ---------------------------------------------------------------------
        # 1. Temporal & Velocity Features (F01 - F05)
        # ---------------------------------------------------------------------
        # F01: Velocity in peak 1h window
        peak_1h_count = 0
        for i, t in enumerate(txns):
            t_start = t.timestamp
            count_in_1h = sum(
                1 for t2 in txns[i:]
                if (t2.timestamp - t_start).total_seconds() <= 3600
            )
            peak_1h_count = max(peak_1h_count, count_in_1h)

        # F02: Total 24h count (from latest transaction timestamp)
        latest_time = txns[-1].timestamp
        count_24h = sum(
            1 for t in txns
            if (latest_time - t.timestamp).total_seconds() <= 86400
        )

        # F03: Volume Turnover Ratio (Debited / Credited)
        total_credit = sum(t.amount for t in txns if t.direction == TransactionDirection.CREDIT)
        total_debit = sum(t.amount for t in txns if t.direction == TransactionDirection.DEBIT)
        turnover_ratio = (total_debit / total_credit) if total_credit > 0 else 0.0

        # F04 & F05: Dwell time between credit and subsequent debit & rapid churn
        dwell_times: List[float] = []
        rapid_churn_count = 0
        total_credits = sum(1 for t in txns if t.direction == TransactionDirection.CREDIT)

        for i, t in enumerate(txns):
            if t.direction == TransactionDirection.CREDIT:
                # Find the next immediate debit
                for t_next in txns[i + 1 :]:
                    if t_next.direction == TransactionDirection.DEBIT:
                        diff_sec = (t_next.timestamp - t.timestamp).total_seconds()
                        if diff_sec >= 0:
                            dwell_times.append(diff_sec)
                            if diff_sec <= 300:  # <= 5 minutes
                                rapid_churn_count += 1
                        break

        avg_dwell_seconds = (sum(dwell_times) / len(dwell_times)) if dwell_times else 0.0
        rapid_churn_ratio = (rapid_churn_count / total_credits) if total_credits > 0 else 0.0

        # ---------------------------------------------------------------------
        # 2. Counterparty & Flow Topology (F06 - F09)
        # ---------------------------------------------------------------------
        senders = set()
        recipients = set()
        all_counterparties = set()

        for t in txns:
            cp = t.counterparty_account or t.source_account or t.destination_account
            if cp:
                all_counterparties.add(cp)
                if t.direction == TransactionDirection.CREDIT:
                    senders.add(cp)
                elif t.direction == TransactionDirection.DEBIT:
                    recipients.add(cp)

        diversity = (len(all_counterparties) / len(txns)) if txns else 0.0
        fan_in = len(senders)
        fan_out = len(recipients)
        fan_in_to_out = (fan_in / (fan_out + 1e-4)) if fan_out > 0 else float(fan_in)

        # ---------------------------------------------------------------------
        # 3. Lifecycle & Account Profile (F10 - F12)
        # ---------------------------------------------------------------------
        # F11: Dormancy burst factor
        burst_score = 0.0
        if historical_avg_daily_volume is not None and historical_avg_daily_volume > 0:
            current_volume = total_credit + total_debit
            burst_score = current_volume / historical_avg_daily_volume
        elif total_credit + total_debit > 50000 and (account_age_days is not None and account_age_days < 30):
            # New account with high volume
            burst_score = 10.0

        # F12: Odd hours ratio (12 AM - 5 AM UTC or local)
        odd_hours_count = sum(1 for t in txns if 0 <= t.timestamp.hour < 5)
        odd_hours_ratio = odd_hours_count / len(txns)

        # ---------------------------------------------------------------------
        # 4. Cash Flow & Structuring Patterns (F13 - F16)
        # ---------------------------------------------------------------------
        # F13: Round chunking (₹9,999, ₹49,999, ₹99,999, or multiples of ₹10,000)
        chunking_detected = False
        for t in txns:
            amt = t.amount
            if (
                abs(amt - 9999) < 1.0
                or abs(amt - 49999) < 1.0
                or abs(amt - 99999) < 1.0
                or (amt >= 10000 and amt % 5000 == 0)
            ):
                chunking_detected = True
                break

        # F14: Immediate near-zero balance extraction ratio
        low_balance_exits = 0
        debit_count = sum(1 for t in txns if t.direction == TransactionDirection.DEBIT)
        for t in txns:
            if t.direction == TransactionDirection.DEBIT and t.balance_after is not None:
                if t.balance_after < (0.02 * t.amount) or t.balance_after < 500.0:
                    low_balance_exits += 1
        balance_extraction_ratio = (low_balance_exits / debit_count) if debit_count > 0 else 0.0

        # F15: Micro-test transaction followed immediately by high-value spike
        micro_test_spike = False
        for i in range(len(txns) - 1):
            t_curr = txns[i]
            t_next = txns[i + 1]
            if (
                t_curr.direction == TransactionDirection.CREDIT
                and t_curr.amount <= 10.0
                and t_next.direction == TransactionDirection.CREDIT
                and t_next.amount >= 5000.0
                and (t_next.timestamp - t_curr.timestamp).total_seconds() <= 3600
            ):
                micro_test_spike = True
                break

        # F16: Repeated identical transaction amount
        amount_counts = Counter(round(t.amount, 2) for t in txns)
        max_repetition = max(amount_counts.values()) if amount_counts else 0

        # ---------------------------------------------------------------------
        # 5. Channel & Registry Indicators (F17 - F19)
        # ---------------------------------------------------------------------
        upi_txns = sum(1 for t in txns if t.channel.value in ("UPI", "WALLET"))
        channel_risk_ratio = upi_txns / len(txns)

        return MuleFeatureVector(
            account_id=account_id,
            evaluated_at=now,
            f01_velocity_1h_count=peak_1h_count,
            f02_velocity_24h_count=count_24h,
            f03_volume_turnover_ratio=round(turnover_ratio, 3),
            f04_dwell_time_seconds_avg=round(avg_dwell_seconds, 1),
            f05_rapid_churn_ratio=round(rapid_churn_ratio, 3),
            f06_counterparty_diversity=round(diversity, 3),
            f07_fan_in_count=fan_in,
            f08_fan_out_count=fan_out,
            f09_fan_in_to_out_ratio=round(fan_in_to_out, 3),
            f10_account_age_days=account_age_days,
            f11_dormancy_burst_score=round(burst_score, 2),
            f12_odd_hours_ratio=round(odd_hours_ratio, 3),
            f13_round_chunking_detected=chunking_detected,
            f14_balance_extraction_ratio=round(balance_extraction_ratio, 3),
            f15_micro_test_followed_by_spike=micro_test_spike,
            f16_identical_amount_repetition_count=max_repetition,
            f17_upi_handle_count=linked_vpa_count,
            f18_channel_risk_concentration=round(channel_risk_ratio, 3),
            f19_registry_match_indicator=has_registry_match,
            is_partial_features=(account_age_days is None or historical_avg_daily_volume is None),
        )
