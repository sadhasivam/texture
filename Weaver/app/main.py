from fastapi import FastAPI

from app.api.v1 import algorithms, datasets, health, runs
from app.core.config import settings
from app.core.cors import setup_cors
from app.ml.adaboost import AdaBoostAdapter
from app.ml.dbscan import DBSCANAdapter
from app.ml.decision_tree import DecisionTreeAdapter
from app.ml.gradient_boosting import GradientBoostingAdapter
from app.ml.isolation_forest import IsolationForestAdapter
from app.ml.kmeans import KMeansAdapter
from app.ml.knn import KNNAdapter
from app.ml.linear_regression import LinearRegressionAdapter
from app.ml.logistic_regression import LogisticRegressionAdapter
from app.ml.naive_bayes import NaiveBayesAdapter
from app.ml.pca import PCAAdapter
from app.ml.random_forest import RandomForestAdapter
from app.ml.svm import SVMAdapter
from app.ml.tsne import TSNEAdapter
from app.ml.xgboost_adapter import XGBoostAdapter
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
    # Supervised - Regression
    registry.register(LinearRegressionAdapter())

    # Supervised - Classification
    registry.register(LogisticRegressionAdapter())
    registry.register(NaiveBayesAdapter())

    # Supervised - Both
    registry.register(DecisionTreeAdapter())
    registry.register(RandomForestAdapter())
    registry.register(GradientBoostingAdapter())
    registry.register(AdaBoostAdapter())
    registry.register(XGBoostAdapter())
    registry.register(SVMAdapter())
    registry.register(KNNAdapter())

    # Unsupervised - Clustering
    registry.register(KMeansAdapter())
    registry.register(DBSCANAdapter())

    # Unsupervised - Dimensionality Reduction
    registry.register(PCAAdapter())
    registry.register(TSNEAdapter())

    # Anomaly Detection
    registry.register(IsolationForestAdapter())


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
