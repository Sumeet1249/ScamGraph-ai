"""Neo4j schema migration runner.

Applies constraints and indexes to the connected Neo4j instance idempotently.
"""

import logging
from typing import Dict, List

from services.graph_engine.neo4j.client import Neo4jClient, neo4j_client
from services.graph_engine.neo4j.schema import SCHEMA_CONSTRAINTS, SCHEMA_INDEXES

logger = logging.getLogger("graph_engine.migrations")


async def apply_migrations(client: Neo4jClient = None) -> Dict[str, int]:
    """Execute all schema constraints and indexes.

    Returns dict of executed count. Gracefully returns zeroes if Neo4j is offline.
    """
    c = client or neo4j_client
    if not c.is_connected:
        connected = await c.connect()
        if not connected:
            logger.info("Neo4j offline. Skipping schema migration execution.")
            return {"constraints": 0, "indexes": 0, "status": "SKIPPED_OFFLINE"}

    constraints_applied = 0
    indexes_applied = 0

    for stmt in SCHEMA_CONSTRAINTS:
        try:
            await c.execute_query(stmt)
            constraints_applied += 1
        except Exception as e:
            logger.warning(f"Error applying constraint '{stmt[:50]}...': {e}")

    for stmt in SCHEMA_INDEXES:
        try:
            await c.execute_query(stmt)
            indexes_applied += 1
        except Exception as e:
            logger.warning(f"Error applying index '{stmt[:50]}...': {e}")

    logger.info(
        f"Applied Neo4j migrations: {constraints_applied} constraints, {indexes_applied} indexes."
    )
    return {
        "constraints": constraints_applied,
        "indexes": indexes_applied,
        "status": "APPLIED",
    }
