from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ProductInput(BaseModel):
    """Input schema for product analysis request"""

    Item_Num: Optional[int] = Field(None, alias="Item Num", description="Item number")
    Structure_Group: Optional[str] = Field(
        None, alias="Structure Group", description="Product structure group"
    )
    Vendor_Abbreviation: Optional[str] = Field(
        None, alias="Vendor Abbreviation", description="Vendor abbreviation"
    )
    Vendor_Name: Optional[str] = Field(
        None, alias="Vendor Name", description="Vendor name"
    )
    Catalog_Num: Optional[str] = Field(
        None, alias="Catalog Num", description="Catalog number"
    )
    Item_Desc_Short: Optional[str] = Field(
        None, alias="Item Desc Short", description="Short item description"
    )
    Item_Desc_Full: Optional[str] = Field(
        None, alias="Item Desc Full", description="Full item description"
    )
    UOM: Optional[str] = Field(None, description="Unit of measure")
    Price: Optional[str] = Field(None, description="Price")
    ITEM_STATUS: Optional[str] = Field(None, description="Item status")
    ITEM_DISCONTINUED: Optional[str] = Field(None, description="Discontinued status")

    FEATURES_AND_BENEFITS_1: Optional[str] = None
    FEATURES_AND_BENEFITS_2: Optional[str] = None
    FEATURES_AND_BENEFITS_3: Optional[str] = None
    FEATURES_AND_BENEFITS_4: Optional[str] = None
    FEATURES_AND_BENEFITS_5: Optional[str] = None
    FEATURES_AND_BENEFITS_6: Optional[str] = None
    FEATURES_AND_BENEFITS_7: Optional[str] = None
    FEATURES_AND_BENEFITS_8: Optional[str] = None
    FEATURES_AND_BENEFITS_9: Optional[str] = None
    FEATURES_AND_BENEFITS_10: Optional[str] = None
    FEATURES_AND_BENEFITS_11: Optional[str] = None
    FEATURES_AND_BENEFITS_12: Optional[str] = None
    FEATURES_AND_BENEFITS_13: Optional[str] = None
    FEATURES_AND_BENEFITS_14: Optional[str] = None
    FEATURES_AND_BENEFITS_15: Optional[str] = None
    FEATURES_AND_BENEFITS_16: Optional[str] = None
    FEATURES_AND_BENEFITS_17: Optional[str] = None
    FEATURES_AND_BENEFITS_18: Optional[str] = None
    FEATURES_AND_BENEFITS_19: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Item_Num": 1110513,
                "Structure_Group": "Masks",
                "Vendor_Name": "3M Company",
                "Item_Desc_Short": "MASK, RESPIRATOR-DISP N95-MEDICAL ONESZ (50/BX 8BX/CS)",
                "Item_Desc_Full": "Particulate Respirator / Surgical Mask 3M™ VFlex™ Medical N95",
                "UOM": "BX",
                "Price": "$31.82",
                "FEATURES_AND_BENEFITS_1": "NIOSH N95 Approved",
                "FEATURES_AND_BENEFITS_2": "FDA cleared for use as surgical mask",
            }
        }


class CategoryInfo(BaseModel):
    """Category information with main category and subcategories"""

    main_category: str = Field(..., description="Main medical category")
    subcategories: List[str] = Field(
        ..., description="List of relevant subcategories", min_length=0, max_length=5
    )


class ProductAnalysisResponse(BaseModel):
    """Response schema for product analysis"""

    name_pattern: str = Field(..., description="Standardized product name pattern")
    product_summary: str = Field(
        ..., description="Product summary in 'About this Product' bullet-point format"
    )
    product_description: str = Field(
        ...,
        description="Product description paragraph followed by HTML table with specifications",
    )
    keywords: List[str] = Field(
        ..., description="15-30 relevant keywords", min_length=15, max_length=30
    )
    category: CategoryInfo = Field(
        ..., description="Product category with main category and subcategories"
    )
    tax_code: str = Field(..., description="Suggested tax code")
    tax_code_name: str = Field(..., description="Tax code name")
    tax_code_confidence: float = Field(
        ..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0
    )
    tax_code_reasoning: str = Field(
        ..., description="Explanation for tax code selection"
    )
    processing_time_seconds: float = Field(
        ..., description="Total API processing time in seconds"
    )
    total_tokens: int = Field(..., description="Total tokens used across all LLM calls")

    class Config:
        json_schema_extra = {
            "example": {
                "name_pattern": "Allergan Botox Therapeutic 100 Units - Muscle Relaxant",
                "product_summary": "About this Product\n\n• Botox® Therapeutic...",
                "product_description": "Botox® Therapeutic is a prescription medication...\n\n<table>...</table>",
                "keywords": [
                    "Botox",
                    "Allergan",
                ],
                "category": {
                    "main_category": "Injectables",
                    "subcategories": [],
                },
                "tax_code": "51020",
                "tax_code_name": "Prescription Drugs",
                "tax_code_confidence": 0.85,
                "tax_code_reasoning": "Medical supplies often fall under similar tax treatment as prescription medical items.",
                "processing_time_seconds": 8.45,
                "total_tokens": 3250,
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Product analysis failed",
                "detail": "Invalid product data format",
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    qdrant_connected: bool = Field(..., description="Qdrant connection status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "qdrant_connected": True,
            }
        }


class CategoriesResponse(BaseModel):
    """Available categories response"""

    categories: Dict[str, List[str]] = Field(..., description="Category hierarchy")

    class Config:
        json_schema_extra = {
            "example": {
                "categories": {
                    "Medical Supplies": ["Disposable", "Instruments", "Lab Supplies"],
                    "Equipment": ["Surgical", "Consumables", "Parts"],
                }
            }
        }
