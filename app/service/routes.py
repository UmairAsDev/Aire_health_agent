from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from app.service.schemas import (
    ProductInput,
    ProductAnalysisResponse,
    ErrorResponse,
    HealthCheckResponse,
    CategoriesResponse,
)
from app.core.product_agent import get_agent
from utils.helper import get_category_hierarchy
from config.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Product Analysis"])


@router.post(
    "/analyze-product",
    response_model=ProductAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Product",
    description="Analyze a product and generate name pattern, summary, keywords, category, and tax code",
)
async def analyze_product(product: ProductInput):
    """
    Analyze a product and generate comprehensive categorization data.

    Returns:
    - name_pattern: Standardized product name
    - structured_summary: Detailed product summary
    - keywords: 15-20 relevant keywords
    - category: Product category (Main > Subcategory)
    - tax_code: Suggested tax code with confidence
    """
    try:
        logger.info(f"Received product analysis request for Item: {product.Item_Num}")

        product_data = product.model_dump(
            by_alias=False
        )  # Use field names, not aliases

        agent = await get_agent()

        result = await agent.analyze_product(product_data)

        response = ProductAnalysisResponse(
            name_pattern=result["name_pattern"],
            product_summary=result["product_summary"],
            product_description=result["product_description"],
            keywords=result["keywords"],
            category=result["category"],
            tax_code=result["tax_code"],
            tax_code_name=result["tax_code_name"],
            tax_code_confidence=result["tax_code_confidence"],
            tax_code_reasoning=result["tax_code_reasoning"],
        )

        logger.info(f"Successfully analyzed product: {product.Item_Num}")
        return response

    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product analysis failed: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check API health and Qdrant connection status",
)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    try:
        agent = await get_agent()

        collection_exists = await agent.vector_store.client.collection_exists(
            settings.collection_name
        )

        return HealthCheckResponse(
            status="healthy", version="1.0.0", qdrant_connected=collection_exists
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "version": "1.0.0",
                "qdrant_connected": False,
                "error": str(e),
            },
        )


@router.get(
    "/categories",
    response_model=CategoriesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Categories",
    description="Get available product categories",
)
async def get_categories():
    """
    Get the available product categories hierarchy.
    """
    try:
        categories = get_category_hierarchy()
        return CategoriesResponse(categories=categories)

    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}",
        )
