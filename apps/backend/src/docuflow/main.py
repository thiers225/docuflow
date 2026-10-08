from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from docuflow.core.config import settings
from docuflow.db.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Vérifier la connexion à la base de données au démarrage
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    yield


app = FastAPI(
    title="DocuFlow",
    description="Extraction et validation de données documentaires",
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return "App Running"
    
@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok", "env": settings.app_env}
