import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal, create_tables
from app.routers import analytics, clusters, recommendations, rules


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version, description=settings.app_description)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(recommendations.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(clusters.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    create_tables()
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    logger.info("ShopSphere database connection verified.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.api_port, reload=True)
