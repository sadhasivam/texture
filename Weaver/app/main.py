from fastapi import FastAPI

from app.api.v1 import algorithms, datasets, health, runs
from app.core.config import settings
from app.core.cors import setup_cors
from app.ml.decision_tree import DecisionTreeAdapter
from app.ml.linear_regression import LinearRegressionAdapter
from app.ml.logistic_regression import LogisticRegressionAdapter
from app.ml.random_forest import RandomForestAdapter
from app.services.algorithm_registry import registry

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend for Texture ML learning studio",
    version="0.1.0",
)

# Setup CORS
setup_cors(app)


# Register algorithms
def register_algorithms():
    """Register all algorithm adapters."""
    registry.register(LinearRegressionAdapter())
    registry.register(LogisticRegressionAdapter())
    registry.register(DecisionTreeAdapter())
    registry.register(RandomForestAdapter())


# Startup event
@app.on_event("startup")
async def startup_event():
    register_algorithms()


# Include routers
app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["health"])
app.include_router(algorithms.router, prefix=f"{settings.api_v1_prefix}/algorithms", tags=["algorithms"])
app.include_router(datasets.router, prefix=f"{settings.api_v1_prefix}/datasets", tags=["datasets"])
app.include_router(runs.router, prefix=f"{settings.api_v1_prefix}/runs", tags=["runs"])


@app.get("/")
async def root():
    return {"message": "Weaver API - Texture ML learning studio backend"}
