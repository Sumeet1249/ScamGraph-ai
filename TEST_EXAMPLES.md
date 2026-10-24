# ScamGraph AI — Test Examples: Fake vs Real Messages

**Purpose**: Test the message detection model with realistic examples

---

## 🚨 FAKE/SCAM Examples

### Category 1: Fake KYC (Know Your Customer) Scams

#### Example 1: Bank Account Freeze
```
Fake Message:
"⚠️ ALERT: Your bank account will be frozen in 24 hours due to suspicious activity.
Verify your identity immediately: bit.ly/verify-now
Do not ignore. Your access will be terminated.
— SBI Security Team"

Markers:
• Urgency ("24 hours")
• Unverified sender
• Suspicious URL (bit.ly)
• Threat language ("frozen", "terminated")
• Typo/grammar issues
```

**Expected**: Model should flag as SCAM
- **F1**: 0.94+ (should detect)
- **Risk**: HIGH (85%+)

---

#### Example 2: Aadhaar Verification
```
Fake Message:
"Your Aadhaar linked to incorrect bank. Update now within 2 hours.
Click here: https://aadhaar-verify.tk/update
Failure to comply will result in account suspension.
Reply YES to confirm."

Markers:
• Time pressure ("2 hours")
• Domain mismatch (.tk not official)
• Credential request (Aadhaar)
• Generic greeting
• Unusual phone number
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (88%+)

---

### Category 2: Electricity Bill Scams

#### Example 3: Unpaid Bill Threat
```
Fake Message:
"URGENT: Your electricity connection will be DISCONNECTED TODAY!
Outstanding bill: ₹2,847
PAY NOW: https://discam-pay.com/bill
Ignore this notice at your own risk!"

Markers:
• ALL CAPS (urgency)
• Threat of disconnection
• Fake payment domain
• No reference number
• Urgent language
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (86%+)

---

#### Example 4: Fake Refund
```
Fake Message:
"Congratulations! Overcharge detected on your bill.
Refund of ₹890 approved.
Click to claim: http://powerco-refund.net/claim
OTP will be sent. Do not share with anyone."

Markers:
• Unexpected reward
• Credential/OTP request
• Non-official domain
• Too good to be true
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (82%+)

---

### Category 3: Job Offer Scams

#### Example 5: Work From Home
```
Fake Message:
"Earn ₹50,000/month from home!
No experience needed. Join now: https://work-from-home-jobs.xyz/register
Be your own boss. Limited spots available!"

Markers:
• Unrealistic pay
• Low barrier to entry
• Suspicious domain
• Pressure ("limited spots")
```

**Expected**: Model should flag as SCAM
- **Risk**: MEDIUM-HIGH (75%+)

---

#### Example 6: Company Recruitment
```
Fake Message:
"TCS Recruitment Drive - Congratulations!
You've been selected for interview.
Submit form here: bit.ly/tcs-recruit-2024
Valid only for 24 hours."

Markers:
• Impersonation (TCS brand)
• Shortened URL
• Time pressure
• Unverified sender
• Credential form request
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (84%+)

---

### Category 4: Investment Scams

#### Example 7: Loan Offer
```
Fake Message:
"💰 INSTANT LOAN APPROVED! 
₹1,00,000 ready to transfer
Interest: Only 1% per month
NO QUESTIONS ASKED
Apply now: https://quickloan-instant.co/apply
Reply APPROVE"

Markers:
• Unrealistic terms
• Urgency
• Minimal interest rate
• Credential request
• Impersonal tone
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (87%+)

---

#### Example 8: Stock Tips
```
Fake Message:
"Exclusive stock tip: XYZ Ltd stock will 3x in 30 days.
Invest now at ₹50/share.
Join our group: https://privatestocks.net/group
Only ₹2,999 membership fee."

Markers:
• Unrealistic returns
• Pressure to join group
• Membership fee
• Exclusive/insider claim
• Suspicious domain
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (83%+)

---

### Category 5: Courier/Customs Scams

#### Example 9: Package Customs Hold
```
Fake Message:
"Your parcel is held at customs.
Duty due: ₹5,000
Pay here to release: https://customs-duty-pay.site/pay
Parcel will be returned if not paid within 24hrs.
Ref: CUST-2024-98765"

Markers:
• Authority impersonation (customs)
• Payment request
• Urgency ("24 hrs")
• Official-looking reference
• Suspicious payment link
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (85%+)

---

#### Example 10: Fake Delivery
```
Fake Message:
"Your Amazon parcel failed delivery.
Retry here: https://amazonfake.tk/retry-delivery
Click within 2 hours or parcel will be returned."

Markers:
• Brand impersonation (Amazon)
• Domain spoofing
• Fake URL
• Time pressure
• Generic message
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (86%+)

---

### Category 6: Digital Arrest Scams

#### Example 11: CBI/Police Warning
```
Fake Message:
"⚠️ WARNING ⚠️
You are accused of money laundering.
Case filed by CBI. Call immediately: +1-800-123-4567
Evidence will be filed against you within 24 hours.
Do not ignore."

Markers:
• Authority impersonation (CBI)
• Threat language
• Criminal accusation
• Urgency
• Intimidation
• International number
```

**Expected**: Model should flag as SCAM
- **Risk**: CRITICAL (92%+)

---

### Category 7: Support/Refund Scams

#### Example 12: Fake Support
```
Fake Message:
"Apple Support: Unauthorized transaction detected on your account.
Amount: ₹15,000
Approve refund: https://apple-support-verify.co/refund
Enter your Apple ID and password to authorize."

Markers:
• Brand impersonation (Apple)
• Credential request
• Unauthorized transaction claim
• URL spoofing
• Urgency
```

**Expected**: Model should flag as SCAM
- **Risk**: HIGH (89%+)

---

## ✅ REAL/LEGITIMATE Examples

### Category 1: Genuine Bank Alerts

#### Real Example 1: Login Notification
```
Real Message:
"HDFC Bank: Your account (****1234) was accessed on 21-10-2026 at 14:30 IST
from IP: 192.168.1.1. If this wasn't you, reply BLOCK immediately.
Account blocked? Call 1860-425-3030."

Markers:
• Masked account number
• Specific timestamp
• Specific IP address
• Action-oriented (not urgent)
• Official contact number
• Transactional, not threatening
```

**Expected**: Model should flag as LEGITIMATE
- **F1**: 0.94+ (should not flag)
- **Risk**: LOW (5%-)
- **Why**: Specific details, official channels, informational tone

---

#### Real Example 2: Transaction Confirmation
```
Real Message:
"ICICI Bank: Your payment of ₹5,000 to 'ABC Store' has been processed.
Transaction ID: TXN-20261021-987654
Available balance: ₹45,230
For assistance: 1860-274-6000"

Markers:
• Merchant name included
• Transaction ID
• Remaining balance
• Informational (no threats)
• Official bank number
• Specific amount
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (2%-)
- **Confidence**: HIGH (95%+)

---

#### Real Example 3: Account Update
```
Real Message:
"Your credit limit has been increased to ₹2,50,000 (from ₹1,50,000)
effective immediately. Review in your app: IBANK.NET.
Thank you for being a valued customer!"

Markers:
• Positive (not threat-based)
• Specific numbers
• Clear source
• No urgency
• No credential request
• No links to click
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (1%-)

---

### Category 2: Genuine Service Notifications

#### Real Example 4: Electricity Bill
```
Real Message:
"Your electricity bill for October 2026 is ready.
Amount: ₹2,847
Due date: 30-10-2026
View bill: Click here or use your consumer ID in the app.
Consumer ID: 123456789"

Markers:
• Specific month and year
• Specific amount
• Clear due date
• Consumer reference
• No urgency ("ready", not "overdue")
• Generic action link (not suspicious URL)
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (3%-)

---

#### Real Example 5: Delivery Update
```
Real Message:
"Your Flipkart order #FKM-2026-98765 is out for delivery today.
Estimated delivery: 14:00-18:00 IST
Tracking: Link in app
Not at home? Reply RESCHEDULE or call 1860-419-0000"

Markers:
• Specific order number
• Clear timeline
• Flexible options
• Official Flipkart number
• Informational tone
• No payment request
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (2%-)

---

### Category 3: Genuine Job Notifications

#### Real Example 6: Interview Schedule
```
Real Message:
"Interview Confirmation from LinkedIn Recruiter
Company: Acme Corp
Position: Software Engineer
Date: 25-10-2026, 14:00 IST
Interview link will be sent 30 minutes before.
Questions? Email: recruit@acmecorp.com"

Markers:
• Specific company name
• Specific role
• Specific date and time
• Professional tone
• Email contact (not links)
• No urgency
• No credential request
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (1%-)

---

#### Real Example 7: Job Update
```
Real Message:
"Your salary for September 2026 has been credited to your account.
Amount: ₹75,000
Company: Tech Solutions Inc.
Date: 01-10-2026
Slip: Available in HR portal (login with employee ID)"

Markers:
• Specific month
• Specific amount
• Company name
• Factual/informational
• Secure access (employee ID)
• No threats
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (1%-)

---

### Category 4: Genuine Bill Reminders

#### Real Example 8: Water Bill
```
Real Message:
"Your water bill for October 2026 is due on 25-10-2026.
Amount: ₹1,245
Consumer Reference: WB-987654
Pay online: municipal-water.gov.in
Payment methods: Debit card, UPI, net banking"

Markers:
• Specific month
• Specific due date
• Official domain (.gov.in)
• Reference number
• Multiple payment options
• Clear information
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (2%-)

---

#### Real Example 9: Internet Plan Renewal
```
Real Message:
"Your Airtel broadband plan renewal date is 30-10-2026.
Current plan: 100 Mbps / Month
Plan cost: ₹999
Renew before due date to avoid service interruption.
Manage subscription: My Airtel app"

Markers:
• Specific renewal date
• Specific plan details
• Clear pricing
• Informational (not urgent)
• Official app mention
• No credential request
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (3%-)

---

### Category 5: Genuine Insurance Notifications

#### Real Example 10: Policy Renewal
```
Real Message:
"Your health insurance policy #HI-2026-123456 expires on 31-10-2026.
Renew now to avoid coverage gap.
Premium: ₹15,000 (annual)
Download renewal form: insureself.in/renew
Validity: Valid until 31-10-2027"

Markers:
• Specific policy number
• Clear expiry date
• Specific premium
• Official domain
• Clear next steps
• No threats
```

**Expected**: Model should flag as LEGITIMATE
- **Risk**: LOW (2%-)

---

## 📊 Test Matrix

### For Manual Testing

| # | Message | Type | Expected Risk | Model Should |
|----|---------|------|----------------|--------------|
| 1 | Bank freeze threat | FAKE | 85%+ | FLAG |
| 2 | Aadhaar update | FAKE | 88%+ | FLAG |
| 3 | Bill disconnection | FAKE | 86%+ | FLAG |
| 4 | Login notification | REAL | <5% | ALLOW |
| 5 | Transaction confirm | REAL | <3% | ALLOW |
| 6 | Credit limit increase | REAL | <2% | ALLOW |
| 7 | Job offer scam | FAKE | 75%+ | FLAG |
| 8 | Interview schedule | REAL | <2% | ALLOW |
| 9 | Digital arrest | FAKE | 92%+ | FLAG |
| 10 | Salary credited | REAL | <2% | ALLOW |

---

## 🎯 How to Test

### Option 1: Manual Testing (If Backend Running)
1. Access API at http://127.0.0.1:8001/docs
2. Find `/analyze` endpoint
3. Paste messages from above
4. Check model prediction and risk score

### Option 2: Simulator Testing
1. Go to http://localhost:3001/lab
2. Start Electricity Bill scenario
3. Make different decisions
4. Observe risk scoring

### Option 3: Python Testing
```python
from ml.message.baseline import BaselineMessageModel

# Load trained model
model = BaselineMessageModel.load()

# Test fake message
fake_msg = "Your bank account will be frozen in 24 hours..."
result = model.predict_single(fake_msg)
print(f"Fake: {result}")
# Expected: {"is_scam": True, "scam_probability": 0.95+}

# Test real message
real_msg = "Your electricity bill for October is ready. Amount: ₹2,847"
result = model.predict_single(real_msg)
print(f"Real: {result}")
# Expected: {"is_scam": False, "scam_probability": 0.05-}
```

---

## 🔍 What to Look For

### Scam Indicators (Should Detect)
- ✓ Urgency ("24 hours", "immediately")
- ✓ Threats ("account frozen", "disconnected")
- ✓ Credential requests ("verify now", "enter password")
- ✓ Suspicious URLs (bit.ly, non-official domains)
- ✓ Too good to be true (unrealistic rewards)
- ✓ Authority impersonation (fake banks, CBI)
- ✓ Grammar/spelling errors
- ✓ Unusual number formats
- ✓ Pressure tactics

### Legitimate Indicators (Should Allow)
- ✓ Specific details (account number, reference ID)
- ✓ Clear purpose (informational, not threatening)
- ✓ Official channels (phone, app, website)
- ✓ No urgency beyond normal
- ✓ No credential requests
- ✓ Professional language
- ✓ Transparent information
- ✓ Flexibility (options, not ultimatums)

---

## 📈 Expected Performance

| Category | Baseline F1 | English F1 | Status |
|----------|------------|-----------|--------|
| Fake Messages | 0.9406 | 0.9610 | ✅ Should detect |
| Real Messages | 0.9406 | 0.9610 | ✅ Should allow |
| False Alarms | 4.0% | 3.23% | ✅ Low FPR |
| Missed Scams | 5.7% | 2.63% | ✅ Low FNR |

---

## 💡 Tips for Testing

1. **Mix real and fake**: Test in sequence to avoid bias
2. **Vary categories**: Test different scam types
3. **Check confidence**: Look at scam_probability, not just label
4. **Note edge cases**: Messages that are ambiguous
5. **Track FPR**: False alarms frustrate users
6. **Track FNR**: Missed scams are dangerous

---

## 🎓 Learning Outcomes

After testing, you should understand:
- ✓ How the model distinguishes scams from legitimate messages
- ✓ Which features are most important (urgency, threats, URLs)
- ✓ How language affects detection (English stronger)
- ✓ Where false positives/negatives occur
- ✓ Why context matters (journey, not just message)

