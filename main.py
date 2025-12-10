from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.service.routes import router
from app.core.product_agent import shutdown_agent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    logger.info("Starting Aire Health AI Product Categorization API...")
    logger.info("Initializing agent and connections...")

    yield

    logger.info("Shutting down Aire Health AI Product Categorization API...")
    await shutdown_agent()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Aire Health AI - Product Categorization API",
    description="""
    Production-ready API for automated product categorization and analysis.
    
    ## Features
    
    * **Name Pattern Generation**: Standardized product naming with brand, product, size, and specs
    * **Structured Summary**: Comprehensive product summary with features, specs, use cases, and benefits
    * **Keyword Extraction**: 15-20 relevant keywords for search and categorization
    * **Category Matching**: Automatic category assignment from product hierarchy
    * **Tax Code Suggestion**: AI-powered tax code recommendation with confidence scoring
    
    ## Powered By
    
    * LangGraph for agentic workflow orchestration
    * Qdrant for vector-based tax category retrieval
    * OpenAI GPT-4 for intelligent analysis
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Aire Health AI - Product Categorization API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
