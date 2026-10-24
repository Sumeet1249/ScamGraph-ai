# API Security & SSRF Defense Architecture

## 1. SSRF URL Validation Specification

All customer-submitted URLs (for link scanning, QR redirects, or webhook endpoints) pass through `validate_url_ssrf_safe`:
- **Prohibited Schemes**: Only `http` and `https` are permitted. Schemes such as `file://`, `gopher://`, `ftp://` are rejected.
- **Localhost & Loopback Filter**: Blocks `localhost`, `127.0.0.1`, `::1`, and `0.0.0.0`.
- **Cloud Metadata Defense**: Blocks `169.254.169.254` (AWS, GCP, Azure, OpenStack instance metadata endpoints).
- **Private IP RFC1918**: Blocks `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`.
- **Internal Domain Suffixes**: Blocks `.local`, `.internal`, `.corp`, and `.lan`.

## 2. API Key Storage & Verification
- Hashed using SHA-256 with cryptographic salting per organization boundary.
- Constant-time comparison prevents timing attacks.
