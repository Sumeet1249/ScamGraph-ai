#!/usr/bin/env python3
"""Quick Test: Scam Detection on Real Examples

Tests the trained baseline model on real scam and legitimate messages.

Usage:
    python test_messages.py
    python test_messages.py --verbose
    python test_messages.py --category scam
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ml.message.baseline import BaselineMessageModel

# Scam Examples
SCAM_MESSAGES = [
    {
        "id": "SCAM-01",
        "category": "KYC",
        "text": "Your bank account will be frozen in 24 hours due to suspicious activity. Verify your identity immediately: bit.ly/verify-now",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-02",
        "category": "Electricity",
        "text": "URGENT: Your electricity connection will be DISCONNECTED TODAY! Outstanding bill: ₹2,847 PAY NOW: https://discam-pay.com/bill",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-03",
        "category": "Job",
        "text": "Earn ₹50,000/month from home! No experience needed. Join now: https://work-from-home-jobs.xyz/register Limited spots available!",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-04",
        "category": "Loan",
        "text": "INSTANT LOAN APPROVED! ₹1,00,000 ready to transfer. Interest: Only 1% per month. NO QUESTIONS ASKED. Apply now: https://quickloan-instant.co/apply",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-05",
        "category": "Courier",
        "text": "Your parcel is held at customs. Duty due: ₹5,000. Pay here to release: https://customs-duty-pay.site/pay. Parcel will be returned if not paid within 24hrs.",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-06",
        "category": "Digital Arrest",
        "text": "You are accused of money laundering. Case filed by CBI. Call immediately: +1-800-123-4567. Evidence will be filed against you within 24 hours.",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-07",
        "category": "Support",
        "text": "Apple Support: Unauthorized transaction detected on your account. Amount: ₹15,000. Approve refund: https://apple-support-verify.co/refund. Enter your Apple ID.",
        "expected": "SCAM",
    },
    {
        "id": "SCAM-08",
        "category": "KYC",
        "text": "Your Aadhaar linked to incorrect bank. Update now within 2 hours. Click: https://aadhaar-verify.tk/update. Failure will result in suspension.",
        "expected": "SCAM",
    },
]

# Real/Legitimate Examples
REAL_MESSAGES = [
    {
        "id": "REAL-01",
        "category": "Bank Alert",
        "text": "HDFC Bank: Your account (****1234) was accessed on 21-10-2026 at 14:30 IST. If this wasn't you, reply BLOCK. Call 1860-425-3030.",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-02",
        "category": "Transaction",
        "text": "ICICI Bank: Your payment of ₹5,000 to ABC Store has been processed. Transaction ID: TXN-20261021-987654. Available balance: ₹45,230.",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-03",
        "category": "Account Update",
        "text": "Your credit limit has been increased to ₹2,50,000 (from ₹1,50,000) effective immediately. Thank you for being a valued customer!",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-04",
        "category": "Bill",
        "text": "Your electricity bill for October 2026 is ready. Amount: ₹2,847. Due date: 30-10-2026. View bill using your consumer ID: 123456789.",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-05",
        "category": "Delivery",
        "text": "Your Flipkart order #FKM-2026-98765 is out for delivery today. Estimated delivery: 14:00-18:00 IST. Not at home? Reply RESCHEDULE.",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-06",
        "category": "Job",
        "text": "Interview Confirmation from LinkedIn Recruiter. Company: Acme Corp. Position: Software Engineer. Date: 25-10-2026, 14:00 IST. Email: recruit@acmecorp.com",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-07",
        "category": "Salary",
        "text": "Your salary for September 2026 has been credited to your account. Amount: ₹75,000. Company: Tech Solutions Inc. Slip: Available in HR portal.",
        "expected": "LEGITIMATE",
    },
    {
        "id": "REAL-08",
        "category": "Bill",
        "text": "Your water bill for October 2026 is due on 25-10-2026. Amount: ₹1,245. Consumer Reference: WB-987654. Pay online: municipal-water.gov.in",
        "expected": "LEGITIMATE",
    },
]


def test_messages(
    category: str = "all",
    verbose: bool = False,
) -> dict:
    """Test the baseline model on real examples.
    
    Args:
        category: 'all', 'scam', or 'real'
        verbose: Print detailed output
        
    Returns:
        Summary statistics
    """
    print("=" * 80)
    print("SCAMGRAPH AI — MESSAGE DETECTION TEST")
    print("=" * 80 + "\n")

    # Load model
    print("Loading trained baseline model...")
    try:
        model = BaselineMessageModel.load()
        print("✓ Model loaded\n")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return {}

    # Prepare test sets
    test_data = []
    if category in ("all", "scam"):
        test_data.extend([(msg, "SCAM") for msg in SCAM_MESSAGES])
    if category in ("all", "real"):
        test_data.extend([(msg, "REAL") for msg in REAL_MESSAGES])

    if not test_data:
        print("No messages to test")
        return {}

    print(f"Testing {len(test_data)} messages...\n")

    # Test
    correct = 0
    results = []

    for msg_obj, msg_type in test_data:
        msg_id = msg_obj["id"]
        msg_text = msg_obj["text"]
        expected = msg_obj["expected"]
        msg_category = msg_obj["category"]

        # Predict
        result = model.predict_single(msg_text)

        # Check if correct
        predicted_label = "SCAM" if result["is_scam"] else "LEGITIMATE"
        is_correct = predicted_label == expected

        if is_correct:
            correct += 1
            status = "✓"
        else:
            status = "✗"

        # Store result
        results.append(
            {
                "id": msg_id,
                "category": msg_category,
                "type": msg_type,
                "expected": expected,
                "predicted": predicted_label,
                "probability": result["scam_probability"],
                "confidence": result["confidence"],
                "correct": is_correct,
            }
        )

        # Print
        if verbose:
            print(f"{status} {msg_id} ({msg_category})")
            print(f"  Text: {msg_text[:70]}...")
            print(f"  Expected: {expected}")
            print(f"  Predicted: {predicted_label} (prob={result['scam_probability']:.4f}, conf={result['confidence']:.4f})")
            print()
        else:
            print(f"{status} {msg_id:<12} {msg_category:<15} {expected:<12} → {predicted_label:<12} (prob={result['scam_probability']:.3f})")

    # Summary
    accuracy = correct / len(test_data) * 100 if test_data else 0
    print("\n" + "=" * 80)
    print(f"RESULTS: {correct}/{len(test_data)} correct ({accuracy:.1f}%)")
    print("=" * 80 + "\n")

    # Per-category accuracy
    by_category = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = {"correct": 0, "total": 0}
        by_category[cat]["total"] += 1
        if r["correct"]:
            by_category[cat]["correct"] += 1

    print("Accuracy by Category:")
    for cat in sorted(by_category.keys()):
        stats = by_category[cat]
        cat_acc = stats["correct"] / stats["total"] * 100
        print(f"  {cat:<15} {stats['correct']}/{stats['total']} ({cat_acc:.0f}%)")

    # Per-type accuracy
    scam_results = [r for r in results if r["type"] == "SCAM"]
    real_results = [r for r in results if r["type"] == "REAL"]

    if scam_results:
        scam_correct = sum(1 for r in scam_results if r["correct"])
        scam_acc = scam_correct / len(scam_results) * 100
        print(f"\nScam Detection: {scam_correct}/{len(scam_results)} ({scam_acc:.0f}%)")

    if real_results:
        real_correct = sum(1 for r in real_results if r["correct"])
        real_acc = real_correct / len(real_results) * 100
        print(f"Legitimate Allow: {real_correct}/{len(real_results)} ({real_acc:.0f}%)")

    # False positives / false negatives
    false_positives = sum(1 for r in results if r["expected"] == "LEGITIMATE" and r["predicted"] == "SCAM")
    false_negatives = sum(1 for r in results if r["expected"] == "SCAM" and r["predicted"] == "LEGITIMATE")

    print(f"\nFalse Positives (real flagged as scam): {false_positives}")
    print(f"False Negatives (scam missed): {false_negatives}")

    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("""
✓ High accuracy (>90%): Model is performing well
✓ Low false positives (<5%): Users won't be over-warned
✓ Low false negatives (<10%): Scams are being caught
✗ High false positives: Users get too many warnings
✗ High false negatives: Real scams slip through
    """)

    return {
        "total_tests": len(test_data),
        "correct": correct,
        "accuracy": accuracy,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "by_category": by_category,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Test ScamGraph message detection on real examples"
    )
    parser.add_argument(
        "--category",
        choices=["all", "scam", "real"],
        default="all",
        help="Which messages to test",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed results",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    results = test_messages(category=args.category, verbose=args.verbose)

    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
