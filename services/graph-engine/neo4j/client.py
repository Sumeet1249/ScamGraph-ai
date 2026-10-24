"""Neo4j Async Driver and Connection Manager.

Adheres to Rule 21 & 22: Enforces timeouts and allows the application
to degrade gracefully when Neo4j is unavailable locally.
"""

import logging
from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver

from services.api.app.core.config import settings

logger = logging.getLogger("graph_engine.neo4j")


class Neo4jClient:
    """Encapsulates async Neo4j driver with resilience and safety timeouts."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self._driver: Optional[AsyncDriver] = None

    async def connect(self) -> bool:
        """Initialize connection pool. Returns True if successful, False if degraded."""
        try:
            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                connection_timeout=3.0,
                max_connection_lifetime=300,
            )
            # Verify connectivity
            await self._driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j at %s", self.uri)
            return True
        except Exception as e:
            logger.warning("Neo4j connection unavailable (%s). Running in degraded mode.", e)
            self._driver = None
            return False

    async def close(self):
        """Close connection pool."""
        if self._driver:
            await self._driver.close()
            self._driver = None

    @property
    def is_connected(self) -> bool:
        return self._driver is not None

    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a parameterized Cypher query with safety timeouts."""
        if not self._driver:
            logger.debug("Neo4j offline. Query skipped: %s", query[:60])
            return []

        try:
            async with self._driver.session() as session:
                result = await session.run(query, parameters or {})
                records = [record.data() async for record in result]
                return records
        except Exception as e:
            logger.error("Error executing Cypher query: %s", e)
            return []


# Global singleton instance
neo4j_client = Neo4jClient()
