"""API v1 Router Aggregator."""

from fastapi import APIRouter
from services.api.app.api.v1.endpoints import (
    analyze,
    campaigns,
    graph,
    incidents,
    investigate,
    lab,
    mule,
    registry,
    risk,
    simulator,
)

api_router = APIRouter()
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(investigate.router, prefix="/investigate", tags=["investigate"])
api_router.include_router(lab.router, prefix="/lab", tags=["lab"])
api_router.include_router(simulator.router, prefix="/simulator", tags=["simulator"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(registry.router, prefix="/registry", tags=["registry"])
api_router.include_router(mule.router, prefix="/mule", tags=["mule"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])





