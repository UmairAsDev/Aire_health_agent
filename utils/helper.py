import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_product_categories(file_path: str) -> Dict[str, List[str]]:
    """Load product categories from JSON file"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading product categories: {e}")
        return {}


def extract_brand_name(product_data: Dict[str, Any]) -> str:
    """Extract brand name from product data"""
    # Try both field name formats
    brand = (
        product_data.get("Vendor Name")
        or product_data.get("Vendor_Name")
        or product_data.get("Vendor Abbreviation")
        or product_data.get("Vendor_Abbreviation")
        or ""
    )
    return brand.strip() if brand else ""


def extract_size_dimensions(product_data: Dict[str, Any]) -> str:
    """Extract size/dimensions from product description and UOM"""
    size_parts = []

    uom = product_data.get("UOM", "")
    if uom:
        size_parts.append(uom)

    desc_short = product_data.get("Item Desc Short", "")
    desc_full = product_data.get("Item Desc Full", "")

    size_patterns = [
        r"\d+\.?\d*\s*(?:mm|cm|m|ml|mL|L|mg|g|kg|inch|in|oz|lb)",
        r"\d+\s*x\s*\d+",
        r"\d+\.?\d*\s*(?:mg|g)\s*/\s*(?:ml|mL)",
        r"\d+\s*(?:gauge|ga|G)",
    ]

    for pattern in size_patterns:
        matches = re.findall(pattern, desc_short + " " + desc_full, re.IGNORECASE)
        size_parts.extend(matches[:2])

    return " ".join(dict.fromkeys(size_parts))


def parse_specifications(product_data: Dict[str, Any]) -> List[str]:
    """Parse specifications from features and benefits"""
    specs = []

    for i in range(1, 20):
        feature_key = f"FEATURES_AND_BENEFITS_{i}"
        feature = product_data.get(feature_key)
        if feature and feature.strip():
            specs.append(feature.strip())

    return specs


def format_product_for_llm(product_data: Dict[str, Any]) -> str:
    """Format product data for LLM prompt"""
    parts = []

    # Helper function to get field value (handles both "Field Name" and "Field_Name")
    def get_field(field_name: str) -> Optional[str]:
        # Try with spaces first
        value = product_data.get(field_name)
        if value is not None and str(value).strip():
            return str(value).strip()
        # Try with underscores
        value = product_data.get(field_name.replace(" ", "_"))
        if value is not None and str(value).strip():
            return str(value).strip()
        return None

    # Vendor information
    vendor = get_field("Vendor Name") or get_field("Vendor_Name")
    if vendor:
        parts.append(f"Vendor: {vendor}")

    # Product descriptions
    desc_short = get_field("Item Desc Short") or get_field("Item_Desc_Short")
    if desc_short:
        parts.append(f"Short Description: {desc_short}")

    desc_full = get_field("Item Desc Full") or get_field("Item_Desc_Full")
    if desc_full:
        parts.append(f"Full Description: {desc_full}")

    # Product group
    group = get_field("Structure Group") or get_field("Structure_Group")
    if group:
        parts.append(f"Product Group: {group}")

    # Catalog number
    catalog = get_field("Catalog Num") or get_field("Catalog_Num")
    if catalog:
        parts.append(f"Catalog Number: {catalog}")

    # Unit of measure
    uom = get_field("UOM")
    if uom:
        parts.append(f"Unit of Measure: {uom}")

    # Features and benefits
    features = parse_specifications(product_data)
    if features:
        parts.append(f"\nFeatures and Benefits:")
        for i, feature in enumerate(features[:10], 1):  # Limit to 10 features
            parts.append(f"  {i}. {feature}")

    # If no meaningful data was found, return a minimal description
    if not parts:
        parts.append("Product information not available")

    return "\n".join(parts)


def validate_keyword_count(
    keywords: List[str], min_count: int = 15, max_count: int = 20
) -> bool:
    """Validate that keyword count is within acceptable range"""
    count = len(keywords)
    return min_count <= count <= max_count


def format_name_pattern(brand: str, product: str, size: str, specs: List[str]) -> str:
    """Format name pattern from components"""
    parts = []

    if brand:
        parts.append(brand)

    if product:
        parts.append(product)

    if size:
        parts.append(size)

    if specs:
        key_specs = " - ".join(specs[:2])
        parts.append(key_specs)

    return " - ".join(parts)


def parse_llm_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from LLM response, handling markdown code blocks"""
    try:

        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.debug(f"Response text: {response_text}")
        return None


def extract_product_name(product_data: Dict[str, Any]) -> str:
    """Extract clean product name from descriptions"""
    desc_full = product_data.get("Item Desc Full", "")
    if desc_full:
        brand = extract_brand_name(product_data)
        if brand and desc_full.startswith(brand):
            desc_full = desc_full[len(brand) :].strip()
        return desc_full

    desc_short = product_data.get("Item Desc Short", "")
    return desc_short


def clean_keywords(keywords: List[str]) -> List[str]:
    """Clean and deduplicate keywords"""
    cleaned = []
    seen = set()

    for kw in keywords:
        kw_clean = kw.strip().lower()

        if not kw_clean or kw_clean in seen:
            continue

        seen.add(kw_clean)
        cleaned.append(kw.strip())

    return cleaned


def get_category_hierarchy() -> Dict[str, List[str]]:
    """Get category hierarchy from product_categories.json"""
    from config.config import settings

    return load_product_categories(settings.PRODUCT_CATEGORIES_FILE)


def find_best_category_match(
    product_data: Dict[str, Any], categories: Dict[str, List[str]]
) -> str:
    """Find best category match based on product data"""
    structure_group = product_data.get("Structure Group", "").lower()

    for main_cat, subcats in categories.items():
        if structure_group in main_cat.lower():
            if subcats:
                return f"{main_cat} > {subcats[0]}"
            return main_cat

    if categories:
        first_main = list(categories.keys())[0]
        first_sub = categories[first_main][0] if categories[first_main] else None
        if first_sub:
            return f"{first_main} > {first_sub}"
        return first_main

    return "Uncategorized"
