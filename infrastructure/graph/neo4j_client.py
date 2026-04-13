"""infrastructure/graph/neo4j_client.py — Neo4j connection for CDSS drug safety."""
import logging
from django.conf import settings

log = logging.getLogger("virtual_hospital.neo4j")


class Neo4jClient:
    """Lazy-connecting Neo4j client.

    The driver is created on first use so Django can start without Neo4j
    being available (especially in CDSS_MOCK_MODE=True).
    """

    # Connection timeout in seconds. After this, a connection attempt gives up
    # rather than hanging the HTTP request indefinitely.
    CONNECTION_TIMEOUT = 5

    def __init__(self):
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            from neo4j import GraphDatabase
            # FIX: was missing connection_timeout — if Neo4j is unreachable,
            # GraphDatabase.driver() would hang indefinitely and block the
            # entire HTTP request. Now times out after 5 seconds.
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                connection_timeout=self.CONNECTION_TIMEOUT,
                max_connection_lifetime=3600,    # recycle connections after 1 hour
                max_connection_pool_size=10,     # limit concurrent connections
            )
        return self._driver

    def verify_connectivity(self) -> None:
        """Verify the driver can reach Neo4j. Used by the health check endpoint."""
        self._get_driver().verify_connectivity()

    def run(self, query: str, **params):
        """Execute a Cypher query and return the result.

        Opens a new session per call. For single queries (e.g. CDSS drug check)
        this is acceptable. For bulk operations, use run_in_session() instead.
        """
        with self._get_driver().session() as session:
            return session.run(query, **params)

    def run_in_session(self, fn):
        """Pass an open session to a callable for multi-query operations.

        Usage:
            def _check(session):
                r1 = session.run("MATCH ...")
                r2 = session.run("MATCH ...")
                return r1, r2
            neo4j_client.run_in_session(_check)

        Avoids opening/closing a session for each individual query.
        """
        with self._get_driver().session() as session:
            return fn(session)

    def close(self) -> None:
        """Close the driver and release all connections."""
        if self._driver:
            self._driver.close()
            self._driver = None


neo4j_client = Neo4jClient()