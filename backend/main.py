from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.database import engine
from backend.models import Base
from backend.routes import router
from backend.routes_process_mining import (
    router as process_mining_router,
)


app = FastAPI(
    title="NEXUS API",
    description=(
        "AI-Powered Procurement Intelligence "
        "Platform with Process Mining"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(
    bind=engine
)


app.include_router(router)

app.include_router(
    process_mining_router
)


@app.get("/")
def root():
    return {
        "application": "NEXUS",
        "status": "online",
        "message": (
            "NEXUS API is running"
        ),
        "modules": [
            "Procurement Intelligence",
            "Predictive Risk",
            "AI Analysis",
            "Process Intelligence",
            "Celonis Integration",
            "PM4Py Process Mining",
        ],
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy",
            "database": "connected",
            "process_mining": "available",
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "process_mining": "unavailable",
            "error": str(error),
        }