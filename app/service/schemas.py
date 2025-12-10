from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ProductInput(BaseModel):
    """Input schema for product analysis"""

    Item_Num: Optional[int] = Field(None, description="Product item number")
    Structure_Group: Optional[str] = Field(None, description="Product structure group")
    Vendor_Abbreviation: Optional[str] = Field(None, description="Vendor abbreviation")
    Vendor_Name: Optional[str] = Field(None, description="Vendor name")
    Catalog_Num: Optional[str] = Field(None, description="Catalog number")
    Item_Desc_Short: Optional[str] = Field(None, description="Short item description")
    Item_Desc_Full: Optional[str] = Field(None, description="Full item description")
    UOM: Optional[str] = Field(None, description="Unit of measure")
    Price: Optional[str] = Field(None, description="Product price")
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


class ProductAnalysisResponse(BaseModel):
    """Complete product analysis response"""

    name_pattern: str = Field(..., description="Standardized product name pattern")
    product_summary: str = Field(
        ..., description="Product summary in 'About this Product' bullet-point format"
    )
    product_description: str = Field(
        ..., description="Product description as HTML table with product details"
    )
    keywords: List[str] = Field(
        ..., description="15-30 relevant keywords", min_length=15, max_length=30
    )
    category: str = Field(
        ..., description="Product category in 'Main > Subcategory' format"
    )
    tax_code: str = Field(..., description="Suggested tax code")
    tax_code_name: str = Field(..., description="Tax code name")
    tax_code_confidence: float = Field(
        ..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0
    )
    tax_code_reasoning: str = Field(
        ..., description="Explanation for tax code selection"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name_pattern": "3M VFlex N95 Medical Respirator Mask - One Size - 50/Box - NIOSH Approved",
                "product_summary": "About this Product\n\n• McKesson Confiderm® 3.5C Nitrile Exam Gloves Small\n• Powder-Free\n• Tested for use with Chemotherapy Drugs using ASTM D6978-05. Gloves used for protection against chemotherapy drug exposure must be selected specifically for the type of glove being used.\n• Textured fingertips provide excellent tactile sensitivity and dexterity.\n• Improved conformability provides superior fit and extended wear comfort.",
                "product_description": "<table><tr><th>Brand</th><td>McKesson</td></tr><tr><th>Powder-Free</th><td>Yes</td></tr><tr><th>Size</th><td>Small - 9.6 in</td></tr><tr><th>Cuff</th><td>Beaded</td></tr><tr><th>Fingertips</th><td>Textured</td></tr></table>",
                "keywords": [
                    "N95 respirator",
                    "surgical mask",
                    "3M VFlex",
                    "NIOSH approved",
                    "FDA cleared",
                    "medical mask",
                    "particulate respirator",
                    "fluid resistant",
                    "healthcare PPE",
                    "disposable mask",
                    "elastic strap",
                    "ASTM F1862",
                    "airborne protection",
                    "one size fits most",
                    "hospital mask",
                    "medical supplies",
                    "respiratory protection",
                    "surgical PPE",
                ],
                "category": "Medical Supplies > Disposable",
                "tax_code": "51020",
                "tax_code_name": "Prescription Drugs",
                "tax_code_confidence": 0.45,
                "tax_code_reasoning": "Medical supplies often fall under similar tax treatment as prescription medical items.",
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
