// Neo4j Schema Constraints & Indexes
CREATE CONSTRAINT incident_id_unique IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT step_id_unique IF NOT EXISTS FOR (s:JourneyStep) REQUIRE s.stepId IS UNIQUE;
CREATE CONSTRAINT sender_id_unique IF NOT EXISTS FOR (snd:Sender) REQUIRE snd.identifier IS UNIQUE;
CREATE CONSTRAINT url_normalized_unique IF NOT EXISTS FOR (u:Url) REQUIRE u.normalizedUrl IS UNIQUE;
CREATE CONSTRAINT upi_vpa_unique IF NOT EXISTS FOR (v:UPIHandle) REQUIRE v.vpa IS UNIQUE;
