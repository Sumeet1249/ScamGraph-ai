"""Neo4j Evidence Graph Schema Definitions and Constraints.

Declares canonical uniqueness constraints and indexes for ScamGraph Graph Intelligence V1.
"""

from typing import List

# Cypher DDL statements for uniqueness constraints
SCHEMA_CONSTRAINTS: List[str] = [
    # Incident identifier
    "CREATE CONSTRAINT incident_id_unique IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
    # Infrastructure nodes
    "CREATE CONSTRAINT domain_norm_unique IF NOT EXISTS FOR (d:Domain) REQUIRE d.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT url_norm_unique IF NOT EXISTS FOR (u:URL) REQUIRE u.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT ip_norm_unique IF NOT EXISTS FOR (ip:IP) REQUIRE ip.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT asn_norm_unique IF NOT EXISTS FOR (a:ASN) REQUIRE a.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT certificate_norm_unique IF NOT EXISTS FOR (c:Certificate) REQUIRE c.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT nameserver_norm_unique IF NOT EXISTS FOR (ns:Nameserver) REQUIRE ns.normalized_value IS UNIQUE",
    # Communications and Payment identifiers
    "CREATE CONSTRAINT phone_norm_unique IF NOT EXISTS FOR (p:Phone) REQUIRE p.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT payment_norm_unique IF NOT EXISTS FOR (pe:PaymentEntity) REQUIRE pe.normalized_value IS UNIQUE",
    # Brand and Tactics
    "CREATE CONSTRAINT brand_norm_unique IF NOT EXISTS FOR (b:Brand) REQUIRE b.normalized_value IS UNIQUE",
    "CREATE CONSTRAINT pattern_id_unique IF NOT EXISTS FOR (pat:Pattern) REQUIRE pat.id IS UNIQUE",
    "CREATE CONSTRAINT campaign_id_unique IF NOT EXISTS FOR (c:Campaign) REQUIRE c.id IS UNIQUE",
]

# Cypher indexes for fast query traversal
SCHEMA_INDEXES: List[str] = [
    "CREATE INDEX incident_created_at IF NOT EXISTS FOR (i:Incident) ON (i.created_at)",
    "CREATE INDEX domain_display_value IF NOT EXISTS FOR (d:Domain) ON (d.display_value)",
    "CREATE INDEX phone_display_value IF NOT EXISTS FOR (p:Phone) ON (p.display_value)",
    "CREATE INDEX payment_type IF NOT EXISTS FOR (pe:PaymentEntity) ON (pe.payment_type)",
]
