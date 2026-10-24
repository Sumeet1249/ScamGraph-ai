# services/api — FastAPI Gateway & Orchestration

## Overview
FastAPI-based asynchronous API gateway that handles:
- Event and message ingestion endpoints (SMS, WhatsApp, web, UPI collect events)
- Incident lifecycle management
- Query endpoints for journey subgraphs and risk assessments
- Streaming updates for real-time frontend visualization

## Technology
- Python 3.11+
- FastAPI & Uvicorn
- Pydantic v2
- SQLAlchemy 2.0 (asyncpg)
