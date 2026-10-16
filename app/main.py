"""
Main entry point for AI Support Intelligence Platform FastAPI backend.
Configures CORS, life-cycle initialization, routers, and health checks.
"""

import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.schemas import HealthResponse
from app.routes import tickets, knowledge
from app.services.classifier import get_classifier
from app.services.retriever import get_retriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management.
    Initializes database tables and preheats ML / RAG models.
    """
    print(f"[{settings.APP_NAME}] Initializing database tables...")
    init_db()

    print(f"[{settings.APP_NAME}] Preheating ML classifier service...")
    get_classifier()

    print(f"[{settings.APP_NAME}] Indexing knowledge base for RAG...")
    get_retriever()

    print(f"[{settings.APP_NAME}] Application startup complete. Ready to receive requests.")
    yield
    print(f"[{settings.APP_NAME}] Shutting down gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-grade AI Support Intelligence Platform featuring "
        "Scikit-learn ticket classification, explainable SLA priority heuristics, "
        "and RAG-grounded generative LLM support drafting."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS to permit requests from Streamlit UI and local/remote clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(tickets.router)
app.include_router(knowledge.router)


@app.get("/", tags=["General"])
def root_info():
    """Returns basic system metadata and links to interactive OpenAPI docs."""
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "ml_metrics": "/metrics"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """
    Comprehensive health check verifying readiness of DB, ML classifier, and RAG index.
    """
    classifier = get_classifier()
    retriever = get_retriever()

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        classifier_ready=classifier.is_ready(),
        knowledge_base_chunks=retriever.total_chunks(),
        llm_provider=settings.LLM_PROVIDER
    )


@app.get("/metrics", tags=["Machine Learning"])
def get_ml_metrics():
    """
    Returns actual empirical evaluation metrics from model training:
    Accuracy, precision, recall, F1-scores, and confusion matrix.
    """
    metrics_path = settings.MODELS_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            return json.load(f)
    return {"message": "Model has not been trained yet. Run python scripts/train_model.py."}
