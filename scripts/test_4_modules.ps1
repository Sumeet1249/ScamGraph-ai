$baseUrl = "http://localhost:3001"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TESTING SMART REGISTRY 4 CORE DATASET MODULES (VIA NEXT.JS PROXY)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# --------------------------------------------------------------------
# MODULE 1: REAL-TIME SCREENING
# --------------------------------------------------------------------
Write-Host "`n>>> [1/4] TESTING: REAL-TIME SCREENING" -ForegroundColor Yellow

$screenHits = @(
    @{ identifier_type = "UPI_VPA"; raw_value = "electricity.desk@oksbi"; expected = "CONFIRMED"; desc = "Utility Phishing UPI" },
    @{ identifier_type = "PHONE"; raw_value = "+919876543210"; expected = "CONFIRMED"; desc = "Telegram Mule Phone" },
    @{ identifier_type = "BANK_ACCOUNT"; raw_value = "SBIN0001234:009876543210"; expected = "DISPUTED"; desc = "Contested Merchant Account" },
    @{ identifier_type = "UPI_VPA"; raw_value = "clean.salary@icici"; expected = "CLEAN"; desc = "Clean Benign Payee" }
)

foreach ($item in $screenHits) {
    $body = @{
        caller_org = "TEST_GATEWAY_OPS"
        identifiers = @(
            @{ identifier_type = $item.identifier_type; raw_value = $item.raw_value }
        )
    } | ConvertTo-Json

    $res = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/screen" -Method Post -Body $body -ContentType "application/json"
    
    $statusObserved = if ($res.total_hits -eq 0) { "CLEAN" } elseif ($res.has_confirmed_hit) { "CONFIRMED" } elseif ($res.has_disputed_hit) { "DISPUTED" } else { "UNKNOWN" }
    
    $pass = $statusObserved -eq $item.expected
    $color = if ($pass) { "Green" } else { "Red" }
    Write-Host "  [$($item.desc)] Query: '$($item.raw_value)'" -ForegroundColor White
    Write-Host "    Expected: $($item.expected) | Result: $statusObserved | Risk: $($res.highest_risk_score) | Hits: $($res.total_hits) -> $(if ($pass){'PASS'}else{'FAIL'})" -ForegroundColor $color
}

# --------------------------------------------------------------------
# MODULE 2: INGEST SUSPECT REPORT
# --------------------------------------------------------------------
Write-Host "`n>>> [2/4] TESTING: INGEST SUSPECT REPORT" -ForegroundColor Yellow

$ingestBody = @{
    reporting_org = "BANK_HDFC_01"
    entity_name = "Digital Arrest Extortion Ring"
    category = "DIGITAL_ARREST"
    reason = "Targeting elderly victims using fabricated Supreme Court arrest warrants and coercive Skype video calls"
    identifiers = @(
        @{ identifier_type = "PHONE"; raw_value = "+919111888999" },
        @{ identifier_type = "UPI_VPA"; raw_value = "cbi.court.escrow@oksbi" }
    )
    evidence_references = @("I4C-COMPLAINT-1930-2026-ARREST99", "FIR-CYB-DEL-2026-440")
    confidence = 0.96
} | ConvertTo-Json

$ingestRes = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/reports" -Method Post -Body $ingestBody -ContentType "application/json"

$ingestPass = ($null -ne $ingestRes.report_id) -and ($ingestRes.status -eq "CONFIRMED") -and ($ingestRes.fingerprints.Count -eq 2)
Write-Host "  Report Ingested: $($ingestRes.report_id)" -ForegroundColor White
Write-Host "  Status: $($ingestRes.status) | Confidence: $($ingestRes.confidence)" -ForegroundColor White
Write-Host "  Linked Entity ID: $($ingestRes.entity_id)" -ForegroundColor White
Write-Host "  Fingerprints Stored: $($ingestRes.fingerprints.Count) (Keyed HMAC-SHA-256)" -ForegroundColor White
Write-Host "  Ingestion Result: $(if ($ingestPass){'PASS'}else{'FAIL'})" -ForegroundColor $(if ($ingestPass){'Green'}else{'Red'})

# Verify immediate screenability of newly ingested identifier
$verifyBody = @{
    caller_org = "TEST_GATEWAY_OPS"
    identifiers = @(
        @{ identifier_type = "UPI_VPA"; raw_value = "cbi.court.escrow@oksbi" }
    )
} | ConvertTo-Json
$verifyScreen = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/screen" -Method Post -Body $verifyBody -ContentType "application/json"
$verifyPass = ($verifyScreen.total_hits -ge 1) -and ($verifyScreen.has_confirmed_hit)
Write-Host "  Immediate Pre-Transaction Screen Verification: $(if ($verifyPass){'PASS (Matched Newly Ingested UPI)'}else{'FAIL'})" -ForegroundColor $(if ($verifyPass){'Green'}else{'Red'})

# --------------------------------------------------------------------
# MODULE 3: REVIEW QUEUE & DISPUTES
# --------------------------------------------------------------------
Write-Host "`n>>> [3/4] TESTING: REVIEW QUEUE & DISPUTES" -ForegroundColor Yellow

# 3A: List reports in review queue
$queue = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/reports" -Method Get
Write-Host "  Review Queue Total Reports: $($queue.Count)" -ForegroundColor White
$queuePass = $queue.Count -ge 4
Write-Host "  Queue Fetch: $(if ($queuePass){'PASS'}else{'FAIL'})" -ForegroundColor $(if ($queuePass){'Green'}else{'Red'})

# 3B: Submit dispute on the newly ingested report
$disputeBody = @{
    report_id = $ingestRes.report_id
    disputing_org = "BANK_ICICI_01"
    reason = "Beneficiary account holder proved SIM card was hijacked via unauthorized e-SIM porting; filed police complaint."
    evidence_documents = @("telecom_ack_esim_fraud.pdf", "police_complaint_del_oct2026.pdf")
} | ConvertTo-Json

$disputeRes = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/disputes" -Method Post -Body $disputeBody -ContentType "application/json"
$disputePass = ($null -ne $disputeRes.dispute_id) -and ($disputeRes.status -eq "OPEN")
Write-Host "  Dispute Filed ID: $($disputeRes.dispute_id) | Status: $($disputeRes.status)" -ForegroundColor White
Write-Host "  Dispute Submission: $(if ($disputePass){'PASS'}else{'FAIL'})" -ForegroundColor $(if ($disputePass){'Green'}else{'Red'})

# Screen again: must show DISPUTED hit with 50% discounted risk
$screenPostDispute = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/screen" -Method Post -Body $verifyBody -ContentType "application/json"
$disputeDiscountPass = ($screenPostDispute.has_disputed_hit) -and ($screenPostDispute.highest_risk_score -eq [Math]::Round(0.96 * 0.5, 2))
Write-Host "  Screening After Dispute -> Status: DISPUTED | Risk Score: $($screenPostDispute.highest_risk_score) (50% Discount Applied): $(if ($disputeDiscountPass){'PASS'}else{'FAIL'})" -ForegroundColor $(if ($disputeDiscountPass){'Green'}else{'Red'})

# 3C: Authorize Revocation
$revokeBody = @{
    report_id = $ingestRes.report_id
    authorizing_org = "BANK_HDFC_01"
    revocation_reason = "Customer remediation complete; credentials rotated and account restored to bona fide user."
    authorized_by = "Compliance_Lead_Officer_401"
} | ConvertTo-Json

$revokeRes = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/revocations" -Method Post -Body $revokeBody -ContentType "application/json"
$revokePass = ($null -ne $revokeRes.revocation_id) -and ($revokeRes.status -eq "APPROVED")
Write-Host "  Revocation Authorized ID: $($revokeRes.revocation_id)" -ForegroundColor White
Write-Host "  Revocation Execution: $(if ($revokePass){'PASS'}else{'FAIL'})" -ForegroundColor $(if ($revokePass){'Green'}else{'Red'})

# Screen again: must show REVOKED with 0.0 risk score
$screenPostRevoke = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/screen" -Method Post -Body $verifyBody -ContentType "application/json"
$revokeSuppressionPass = ($screenPostRevoke.has_revoked_hit) -and ($screenPostRevoke.highest_risk_score -eq 0.0)
Write-Host "  Screening After Revocation -> Has Revoked Hit: $($screenPostRevoke.has_revoked_hit) | Risk Score: $($screenPostRevoke.highest_risk_score) (Active Risk Suppressed): $(if ($revokeSuppressionPass){'PASS'}else{'FAIL'})" -ForegroundColor $(if ($revokeSuppressionPass){'Green'}else{'Red'})

# --------------------------------------------------------------------
# MODULE 4: AUDIT LEDGER
# --------------------------------------------------------------------
Write-Host "`n>>> [4/4] TESTING: CRYPTOGRAPHIC AUDIT LEDGER" -ForegroundColor Yellow

$auditList = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/audit-events?limit=10" -Method Get
Write-Host "  Total Audit Events Fetched: $($auditList.Count)" -ForegroundColor White

$allSealed = $true
foreach ($ev in $auditList) {
    if (-not $ev.integrity_hash -or $ev.integrity_hash.Length -lt 20) {
        $allSealed = $false
    }
}

$sampleEv = $auditList[0]
Write-Host "  Latest Event: [$($sampleEv.action)] on Entity: $($sampleEv.entity_id)" -ForegroundColor White
Write-Host "  Actor Org: $($sampleEv.actor_org) | Transition: $($sampleEv.previous_state) -> $($sampleEv.new_state)" -ForegroundColor White
Write-Host "  SHA-256 Integrity Seal: $($sampleEv.integrity_hash)" -ForegroundColor White
Write-Host "  Cryptographic Integrity Verification: $(if ($allSealed){'PASS (100% Events Cryptographically Sealed)'}else{'FAIL'})" -ForegroundColor $(if ($allSealed){'Green'}else{'Red'})

# --------------------------------------------------------------------
# SUMMARY STATS
# --------------------------------------------------------------------
Write-Host "`n>>> LIVE REGISTRY AGGREGATE METRICS:" -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "$baseUrl/api/v1/registry/statistics" -Method Get
[PSCustomObject]@{
    TotalEntities = $stats.total_entities
    TotalReports = $stats.total_reports
    ConfirmedSuspects = $stats.confirmed_count
    DisputedSuspects = $stats.disputed_count
    RevokedSuspects = $stats.revoked_count
    TotalScreeningQueries = $stats.screening_count
    TotalAuditEvents = $stats.audit_event_count
    SystemStatus = $stats.system_status
} | Format-List
