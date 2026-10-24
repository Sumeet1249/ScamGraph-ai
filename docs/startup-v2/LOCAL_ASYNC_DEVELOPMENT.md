# LOCAL ASYNC DEVELOPMENT & RUNTIME CHECKS
**ScamGraph AI — Phase 7B Local Setup Guide**
*Document Version: 2.0.0 | Date: 2026-10-24*

---

## 1. Quickstart Commands

Developers can run the full async architecture locally with zero friction:

```bash
# 1. Start core databases and Redis via Docker Compose
docker compose up -d postgres neo4j redis

# 2. Start FastAPI Backend (Port 8001)
python -m uvicorn services.api.app.main:app --host 0.0.0.0 --port 8001 --reload

# 3. Start Frontend Next.js Web App (Port 3001)
npm --prefix apps/web run dev

# 4. Run Async Queue & Worker Regression Suite
python -m pytest tests/unit/test_async_jobs_step22.py -v
```

---

## 2. Zero-Dependency Fallback Mode

If Docker or Redis is not running locally:
- `services.jobs.queue` automatically defaults to `MemoryJobQueue`.
- `services.jobs.cache` automatically defaults to in-memory sliding-window storage.
- All priority scheduling, bounded backoff, dead-letter storage, and worker pipelines execute seamlessly in-process.
- No external services required to run unit tests.
