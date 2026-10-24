# Hard Negatives (`data/hard_negatives/`)

## Intended Purpose
Contains benign, legitimate Indian transactional messages and payment notifications that superficially resemble scam language:
- Official bank KYC renewal reminders (with valid official domain links)
- Electricity discom routine maintenance announcements
- Legitimate courier delivery OTP updates
- Genuine salary and cashback credits

## Governance Rules
1. Used explicitly to evaluate and suppress false-positive alerts on real banking and utility notifications.
2. Verified legitimate sources only.
