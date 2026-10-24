"""Incident Repository Abstraction and In-Memory Implementation (Step 11).

Defines the repository interface to ensure business logic does not depend
directly on in-memory storage, facilitating seamless future migration to PostgreSQL.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime, timezone
import asyncio

from services.api.app.domain import (
    Incident,
    Event,
    Evidence,
    IncidentStatus,
)


class IncidentRepository(ABC):
    """Abstract interface for Incident, Event, and Evidence persistence."""

    @abstractmethod
    async def create_incident(self, incident: Incident) -> Incident:
        """Create a new incident session."""
        pass

    @abstractmethod
    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Retrieve incident by ID."""
        pass

    @abstractmethod
    async def get_incident_scoped(
        self,
        incident_id: str,
        owner_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> Optional[Incident]:
        """Retrieve incident enforcing tenant or owner boundary at query time."""
        pass

    @abstractmethod
    async def list_incidents(self) -> List[Incident]:
        """Retrieve all incidents."""
        pass

    @abstractmethod
    async def list_incidents_scoped(
        self,
        owner_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> List[Incident]:
        """Retrieve incidents matching tenant or owner boundary at query time."""
        pass

    @abstractmethod
    async def add_event(self, incident_id: str, event: Event) -> Event:
        """Add an event to an existing incident session."""
        pass

    @abstractmethod
    async def get_events(self, incident_id: str) -> List[Event]:
        """Retrieve all events for an incident."""
        pass

    @abstractmethod
    async def get_timeline(self, incident_id: str) -> List[Event]:
        """Retrieve events sorted chronologically by timestamp."""
        pass

    @abstractmethod
    async def add_evidence(self, incident_id: str, evidence: Evidence) -> Evidence:
        """Attach an evidence observation to an incident."""
        pass

    @abstractmethod
    async def get_evidence(self, incident_id: str) -> List[Evidence]:
        """Retrieve all evidence items for an incident."""
        pass


class InMemoryIncidentRepository(IncidentRepository):
    """In-memory implementation with asyncio lock for thread safety."""

    def __init__(self):
        self._incidents: Dict[str, Incident] = {}
        self._events: Dict[str, List[Event]] = {}
        self._evidence: Dict[str, List[Evidence]] = {}
        self._lock = asyncio.Lock()

    async def create_incident(self, incident: Incident) -> Incident:
        async with self._lock:
            self._incidents[incident.id] = incident
            self._events[incident.id] = []
            self._evidence[incident.id] = []
            return incident

    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        async with self._lock:
            return self._incidents.get(incident_id)

    async def get_incident_scoped(
        self,
        incident_id: str,
        owner_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> Optional[Incident]:
        async with self._lock:
            inc = self._incidents.get(incident_id)
            if not inc:
                return None
            if owner_id and inc.owner_id != owner_id:
                return None
            if org_id and inc.org_id != org_id:
                return None
            return inc

    async def list_incidents(self) -> List[Incident]:
        async with self._lock:
            return list(self._incidents.values())

    async def list_incidents_scoped(
        self,
        owner_id: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> List[Incident]:
        async with self._lock:
            results = []
            for inc in self._incidents.values():
                if owner_id and inc.owner_id != owner_id:
                    continue
                if org_id and inc.org_id != org_id:
                    continue
                results.append(inc)
            return results

    async def add_event(self, incident_id: str, event: Event) -> Event:
        async with self._lock:
            if incident_id not in self._incidents:
                return None
            event.incident_id = incident_id
            self._events[incident_id].append(event)
            # Update incident updated_at
            inc = self._incidents[incident_id]
            inc.updated_at = datetime.now(timezone.utc)
            return event

    async def get_events(self, incident_id: str) -> List[Event]:
        async with self._lock:
            if incident_id not in self._incidents:
                return None
            return list(self._events.get(incident_id, []))

    async def get_timeline(self, incident_id: str) -> List[Event]:
        async with self._lock:
            if incident_id not in self._incidents:
                return None
            events = self._events.get(incident_id, [])
            # Chronological sort
            return sorted(events, key=lambda ev: ev.timestamp)

    async def add_evidence(self, incident_id: str, evidence: Evidence) -> Evidence:
        async with self._lock:
            if incident_id not in self._incidents:
                return None
            evidence.incident_id = incident_id
            self._evidence[incident_id].append(evidence)
            inc = self._incidents[incident_id]
            inc.updated_at = datetime.now(timezone.utc)
            return evidence

    async def get_evidence(self, incident_id: str) -> List[Evidence]:
        async with self._lock:
            if incident_id not in self._incidents:
                return None
            return list(self._evidence.get(incident_id, []))


# Global singleton repository instance for dependency injection
incident_repository: IncidentRepository = InMemoryIncidentRepository()


def get_incident_repository() -> IncidentRepository:
    """FastAPI Dependency Provider for IncidentRepository."""
    return incident_repository
