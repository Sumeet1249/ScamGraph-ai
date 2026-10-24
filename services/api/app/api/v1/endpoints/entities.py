"""Entity Intelligence Endpoints for ScamGraph AI V2 (Prompt 6).

Provides privacy-aware entity lookup, observation history, relationship exploration,
resolution, and trust assessments.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.schemas.entity import (
    EntityObservation,
    EntityRelationship,
    EntityType,
    TrustAssessment,
)
from services.entity_intelligence.service import entity_intelligence_service

router = APIRouter(prefix="/entities", tags=["Entity Intelligence"])


class ResolveEntityRequest(BaseModel):
    """Request to normalize and resolve an entity string."""
    entity_type: EntityType
    raw_value: str
    incident_id: str = "temp_lookup"


class AssessEntityRequest(BaseModel):
    """Request to assess the evidence-backed trust and reputation of an entity."""
    entity_id: str


@router.get("/{entity_id}", response_model=Dict[str, Any])
async def get_entity_by_id(
    entity_id: str,
    access_tier: str = Query("CONSUMER", regex="^(CONSUMER|ANALYST)$", description="Authorization view tier"),
):
    """Retrieves an entity with strict privacy serialization.
    
    Consumers receive masked identifiers (******3210, s***@oksbi).
    Analysts receive full canonical lineage if authorized.
    """
    entity_data = entity_intelligence_service.get_entity(entity_id, access_tier=access_tier)
    if not entity_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found.",
        )
    return entity_data


@router.get("/{entity_id}/observations", response_model=List[EntityObservation])
async def get_entity_observations(entity_id: str):
    """Retrieves contextual sightings and incident observations for an entity."""
    return entity_intelligence_service.get_entity_observations(entity_id)


@router.get("/{entity_id}/relationships", response_model=List[EntityRelationship])
async def get_entity_relationships(entity_id: str):
    """Retrieves directed co-occurrences and infrastructure links connected to an entity."""
    return entity_intelligence_service.get_entity_relationships(entity_id)


@router.post("/resolve", response_model=Dict[str, Any])
async def resolve_entity(request: ResolveEntityRequest):
    """Normalizes and resolves an identifier against canonical entities."""
    # Anti-enumeration check
    allowed, msg = entity_intelligence_service.anti_enumeration.check_query_allowed(
        client_id="default_client",
        search_query=request.raw_value,
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    ent, obs = entity_intelligence_service.resolve_and_upsert_entity(
        entity_type=request.entity_type,
        raw_value=request.raw_value,
        incident_id=request.incident_id,
    )
    return {
        "entity_id": ent.entity_id,
        "entity_type": ent.entity_type.value,
        "masked_value": ent.masked_value,
        "canonical_hash": ent.canonical_hash,
        "observation_id": obs.observation_id,
        "verification_state": ent.verification_state.value,
        "observation_count": ent.observation_count,
    }


@router.post("/assess", response_model=TrustAssessment)
async def assess_entity_trust(request: AssessEntityRequest):
    """Calculates evidence-aware trust assessment, corroboration ratio, and temporal decay."""
    try:
        return entity_intelligence_service.assess_entity_trust(request.entity_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
