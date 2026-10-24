# ScamGraph AI — URL Safety & Infrastructure Intelligence (Step 16)

## 1. Overview & Architecture

When an arbitrary or suspected phishing URL is submitted by a user or ingested from an SMS/chat message, ScamGraph AI safely processes it through a strict multi-layer intelligence pipeline before any external interaction takes place.

```
Raw URL Input
     │
     ▼
[URLNormalizer] ─────────► NormalizedURL (clean scheme, lowercase host, strip fragment)
     │
     ▼
[URLSafetyValidator] ────► SSRF Check: Validates Hostnames & Resolved IP Subnets
     │                     (Rejects 127.0.0.0/8, 10.0.0.0/8, 192.168.0.0/16, ::1, metadata)
     ▼ (If Safe)
 ┌───┴───────────────────────────────────────────────────────┐
 │                                                           │
 ▼                                                           ▼
[LexicalAnalyzer]                                    [DNSAnalyzer]
Entropy, token counts, punycode, dots                 A, AAAA, CNAME, Nameservers
 │                                                           │
 ▼                                                           ▼
[RDAPAnalyzer]                                       [TLSAnalyzer]
Registrar, creation, expiry dates                     Subject, issuer, valid dates, SANs
 │                                                           │
 └───────────────────────────┬───────────────────────────────┘
                             │
                             ▼
                    [RedirectAnalyzer]
                    Safe Hop-by-Hop Tracing (Max Depth 5)
                    Each Hop re-validated by URLSafetyValidator
                             │
                             ▼
                 [Canonical Evidence[] & Entity[]]
```

---

## 2. SSRF Protection & Network Boundary Rules

Security is paramount. The [URLSafetyValidator](file:///s:/ScamGraph-AI/services/investigation/url_analysis/safety.py) blocks:

* **Loopback**: `127.0.0.0/8`, `::1/128`, `localhost`
* **Private RFC 1918**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
* **IPv6 Local**: `fc00::/7`
* **Link-Local & Cloud Metadata**: `169.254.0.0/16` (AWS/GCP/Azure metadata `169.254.169.254`), `fe80::/10`
* **Multicast & Reserved**: `224.0.0.0/4`, `ff00::/8`, `240.0.0.0/4`
* **Internal Hostnames**: `localhost`, `*.internal`, `*.local`, `*.lan`
* **DNS Rebinding Protection**: Validates **both** the requested hostname and every IP address returned by socket DNS resolution.

Any attempt to query internal endpoints (e.g. `http://127.0.0.1:8000/secret` or `http://169.254.169.254/latest/meta-data/`) is aborted immediately with `status: "rejected"`.

---

## 3. Data Collected & Canonical Evidence

| Signal | Source | Description |
| :--- | :--- | :--- |
| `URL_LEXICAL_OBSERVATION` | `URL_ANALYZER` | Length, dots, hyphens, Shannon entropy, suspicious token matches |
| `DIRECT_IP_HOST_OBSERVED` | `URL_ANALYZER` | Target uses raw IP address instead of registered domain |
| `PUNYCODE_HOMOGRAPH_OBSERVED` | `URL_ANALYZER` | IDN punycode character sequences detected |
| `DNS_RESOLUTION` | `DNS` | Observed A and AAAA record mappings |
| `CNAME_OBSERVED` | `DNS` | Canonical name alias chains |
| `DOMAIN_REGISTRATION_OBSERVATION` | `RDAP` | Domain registration age, registrar, and expiration |
| `TLS_CERTIFICATE_OBSERVATION` | `TLS` | Issuer organization, validity dates, SAN count |
| `REDIRECT_OBSERVATION` | `URL_ANALYZER` | HTTP 301/302/307/308 redirect provenance |

> **Critical Rule**: This module collects objective evidence only. It **never** outputs a final verdict of `SCAM`, `FRAUD`, or `SAFE`.

---

## 4. Resilience & Partial Results

Each individual analyzer enforces strict timeouts:
* DNS: 3.0s
* RDAP: 3.0s
* TLS: 3.0s
* Redirect hop: 2.5s

If an individual component experiences a timeout or network error (e.g. RDAP server is slow or domain is synthetic), the investigation returns `status: "partial"`, preserving all successfully gathered evidence and logging errors without failing the overall incident evaluation.

---

## 5. API Reference

### `POST /api/v1/analyze/url`

**Request**:
```json
{
  "incident_id": "inc_123456789abc",
  "url": "https://example.com/test-path"
}
```

**Response (200 OK)**:
```json
{
  "investigation_id": "inv-url-9f20e8b1",
  "status": "completed",
  "normalized_url": "https://example.com/test-path",
  "features": {
    "url_length": 30,
    "https_scheme": true,
    "has_ip_hostname": false,
    "has_punycode": false,
    "hostname_entropy": 2.75
  },
  "entities": [
    { "entity_type": "URL", "normalized_value": "https://example.com/test-path" },
    { "entity_type": "DOMAIN", "normalized_value": "example.com" }
  ],
  "evidence": [
    {
      "source": "URL_ANALYZER",
      "signal": "URL_LEXICAL_OBSERVATION",
      "observation": "URL length: 30, Dots: 1, Suspicious tokens: 0"
    }
  ],
  "errors": []
}
```
