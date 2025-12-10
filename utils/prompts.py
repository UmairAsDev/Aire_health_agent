"""
LLM Prompts for Product Categorization Agent
"""

NAME_PATTERN_PROMPT = """You are a product naming expert. Given the following product information, create a standardized product name pattern.

Product Information:
{product_info}
Extract and format the following components:
1. Brand name (from vendor information)
2. Product name (main product identifier)
3. Size/dimensions (measurements, quantities)
4. Key specifications (1-2 most important features)


Format the name pattern as: [Brand] [Product Name] [Size] - [Key Specs]

Example: "3M VFlex N95 Medical Respirator Mask - One Size - 50/Box - NIOSH Approved"

Return ONLY the formatted name pattern, nothing else."""


PRODUCT_SUMMARY_PROMPT = """You are a product documentation specialist. Create a comprehensive product summary in "About this Product" format with bullet points.

Product Information:
{product_info}

Guidelines:
- Start with "About this Product" as the header
- Add a blank line after the header
- Create 6-10 bullet points using the "•" symbol
- Each bullet point should highlight key features, benefits, specifications, or use cases
- Extract information from FEATURES_AND_BENEFITS fields and product description
- Make bullet points detailed and informative (1-2 sentences each when appropriate)
- Focus on what makes the product unique and valuable
- Include brand name, product type, certifications, materials, and key specifications
- DO NOT include price information in the summary
- Think about what information would be most valuable to potential buyers
- Be Consistent with response format.



Return ONLY the formatted text with bullet points, nothing else."""


PRODUCT_DESCRIPTION_PROMPT = """You are an e-commerce product content specialist. Create a COMPREHENSIVE product description with TWO parts: a descriptive paragraph and a detailed specification table.

Product Information:
{product_info}

PART 1: PRODUCT DESCRIPTION PARAGRAPH
- Write 2-4 sentences describing the product
- Focus on key benefits, uses, and what makes it unique
- Use professional, engaging language suitable for e-commerce
- Highlight medical/therapeutic applications if applicable

PART 2: SPECIFICATION TABLE
- Create a detailed HTML table with ALL relevant product specifications
- Include as many specifications as available (10-15+ rows is fine for complex products)
- Use <table>, <tr>, <th>, and <td> tags

SPECIFICATIONS TO INCLUDE (if available):
- Brand/Manufacturer
- Product Type/Form
- Size/Dimensions/Quantity
- Material/Composition
- Active Ingredients (for pharmaceuticals)
- Strength/Dosage (for medications)
- Color/Appearance
- Packaging Details
- Storage Requirements
- Certifications/Standards (FDA, NIOSH, etc.)
- Special Features
- Intended Use/Application
- Sterility Status
- Shelf Life
- Any other relevant medical/technical specifications

WHAT TO EXCLUDE:
- Catalog numbers
- Vendor codes
- Unit of measure (UOM)
- Price information

FORMAT:
First the paragraph, then a blank line, then the HTML table.

EXAMPLE OUTPUT:
Botox® Therapeutic is a prescription medication containing Botulinum Toxin Type A, designed for therapeutic muscle relaxation treatments. This pharmaceutical-grade product is manufactured by Allergan and requires proper refrigeration to maintain efficacy. Each vial contains 100 units of onabotulinumtoxinA for precise dosing in clinical applications.

<table><tr><th>Brand</th><td>Allergan</td></tr><tr><th>Product Type</th><td>Injectable Therapeutic</td></tr><tr><th>Active Ingredient</th><td>Botulinum Toxin Type A (onabotulinumtoxinA)</td></tr><tr><th>Strength</th><td>100 Units per Vial</td></tr><tr><th>Form</th><td>Lyophilized Powder for Injection</td></tr><tr><th>Storage</th><td>Refrigerate at 2-8°C</td></tr><tr><th>Shelf Life</th><td>36 months (unopened)</td></tr><tr><th>Reconstitution</th><td>Use within 24 hours</td></tr><tr><th>Classification</th><td>Prescription Muscle Relaxant</td></tr></table>

Return the description paragraph followed by the HTML table."""


KEYWORD_EXTRACTION_PROMPT = """You are an e-commerce SEO expert. Generate {keyword_count} SHORT, MEANINGFUL keywords for product search and discovery.

Product Information:
{product_info}

CRITICAL RULES:
- Each keyword must be 1-3 WORDS MAXIMUM (e.g., "nitrile gloves", "N95 mask", "powder-free")
- NO full sentences or long phrases
- Each word must have search value and meaning
- Think like a customer typing into a search box

Keyword Categories to Include:

1. **Brand & Manufacturer** (1-2 words)
   - Brand name (e.g., "3M", "McKesson")
   - Product line (e.g., "VFlex", "Confiderm")

2. **Product Type** (1-3 words)
   - Generic terms (e.g., "gloves", "mask", "respirator")
   - Specific types (e.g., "exam gloves", "surgical mask", "nitrile gloves")

3. **Key Features** (1-2 words)
   - Material (e.g., "nitrile", "latex-free")
   - Properties (e.g., "powder-free", "textured", "disposable")
   - Size (e.g., "small", "medium", "one-size")

4. **Certifications** (1-3 words)
   - Standards (e.g., "N95", "ASTM F1862", "FDA cleared")
   - Ratings (e.g., "medical grade", "NIOSH approved")

5. **Use Case** (1-3 words)
   - Application (e.g., "medical gloves", "surgical gloves", "exam gloves")
   - Setting (e.g., "healthcare", "dental", "laboratory")

6. **User Intent** (1-3 words)
   - Problem solving (e.g., "allergy-free", "chemical resistant")
   - Benefits (e.g., "comfortable fit", "tactile sensitivity")

EXAMPLES OF GOOD KEYWORDS:
✓ "nitrile gloves"
✓ "N95 respirator"
✓ "powder-free"
✓ "medical grade"
✓ "3M VFlex"
✓ "exam gloves"
✓ "latex-free"
✓ "disposable gloves"

EXAMPLES OF BAD KEYWORDS (TOO LONG):
✗ "gloves for medical professionals"
✗ "NIOSH approved N95 respirator mask"
✗ "powder-free nitrile examination gloves"

Generate EXACTLY {keyword_count} keywords (between {min_count} and {max_count}).
Each keyword should be searchable, meaningful, and 1-3 words only.

Return as a JSON array:
{{
  "keywords": ["keyword1", "keyword2", ...]
}}

Return ONLY valid JSON, no markdown formatting."""


CATEGORY_MATCHING_PROMPT = """You are a medical product categorization expert. Match the product to categories from the AVAILABLE CATEGORIES ONLY.

Product Information:
{product_info}

Available Categories (YOU MUST USE THESE ONLY):
{categories}

CRITICAL RULES:
1. **ONLY use categories from the Available Categories list above**
2. **DO NOT create new categories** - select from the provided list
3. Select the MAIN CATEGORY that best fits the product
4. Select 1-3 SUBCATEGORIES from that main category's subcategory list
5. If the main category has no subcategories (empty list), use an empty subcategories array

MEDICAL CATEGORIZATION APPROACH:
- **Medical Supplies**: Disposable items, general medical supplies, pharmaceuticals, surgical supplies
- **Equipment**: Surgical equipment, instruments, lab equipment, parts
- **Devices & Lasers**: Medical devices, laser equipment, surgical devices
- **Injectables**: Injectable medications, biologics, therapeutic injectables

SELECTION PROCESS:
1. Analyze the product's primary medical function
2. Match to ONE main category from: "Medical Supplies", "Equipment", "Devices & Lasers", or "Injectables"
3. Select 1-3 relevant subcategories from that category's list
4. If no subcategories are available, return empty array

OUTPUT FORMAT - Return as JSON:
{{
  "main_category": "One of the provided main categories",
  "subcategories": ["Subcategory from the list", "Another subcategory"]
}}

EXAMPLES:
- Botox Injectable → {{"main_category": "Injectables", "subcategories": []}}
- N95 Respirator Mask → {{"main_category": "Medical Supplies", "subcategories": ["Disposable"]}}
- Nitrile Exam Gloves → {{"main_category": "Medical Supplies", "subcategories": ["Disposable"]}}
- Surgical Scissors → {{"main_category": "Equipment", "subcategories": ["Surgical", "Instruments"]}}
- Laser Device → {{"main_category": "Devices & Lasers", "subcategories": ["Surgical"]}}

Return ONLY valid JSON with main_category from the provided list and subcategories from that category's subcategory list."""


TAX_CODE_SELECTION_PROMPT = """You are a tax classification expert specializing in medical and pharmaceutical products. Select the MOST ACCURATE tax code from the retrieved categories.

Product Information:
{product_info}

Retrieved Tax Categories (from database):
{tax_categories}

CRITICAL INSTRUCTIONS:
1. **ONLY select from the Retrieved Tax Categories above** - these are the ONLY valid options
2. **Choose the BEST MATCH** from the retrieved list - there must be one that fits
3. **Be CONFIDENT** - if there's a reasonable match, use confidence 0.8 or higher
4. **Medical Product Focus**: These are medical/pharmaceutical products from healthcare settings

SELECTION CRITERIA (in priority order):
1. **Exact Product Match**: Does the tax category description exactly match this product type?
2. **Medical Classification**: Does it match the medical/pharmaceutical classification?
3. **Regulatory Category**: Does it align with FDA/medical device classification?
4. **Therapeutic Use**: Does it match the therapeutic or clinical application?
5. **Closest Alternative**: If no perfect match, which category is closest?

CONFIDENCE SCORING:
- **0.9-1.0**: Perfect or near-perfect match (exact product type in description)
- **0.8-0.89**: Strong match (same medical category, similar use)
- **0.7-0.79**: Good match (related category, reasonable fit)
- **0.6-0.69**: Acceptable match (general category applies)
- **Below 0.6**: Only if truly no good match exists

IMPORTANT:
- **Be decisive** - select the best available option with appropriate confidence
- **Use high confidence** when the match is clear
- **Explain your reasoning** clearly, referencing specific aspects of the product and tax category

Return as JSON:
{{
  "tax_code": "selected_tax_code_from_retrieved_list",
  "tax_code_name": "exact name from the tax category",
  "confidence": 0.85,
  "reasoning": "Detailed explanation: This product is [product type] which matches tax category [code] because [specific reasons]. The confidence is [level] because [justification]."
}}

Return ONLY valid JSON, no markdown formatting."""


def get_name_pattern_prompt(product_info: str) -> str:
    """Get formatted name pattern prompt"""
    return NAME_PATTERN_PROMPT.format(product_info=product_info)


def get_product_summary_prompt(product_info: str) -> str:
    """Get formatted product summary prompt"""
    return PRODUCT_SUMMARY_PROMPT.format(product_info=product_info)


def get_product_description_prompt(product_info: str) -> str:
    """Get formatted product description prompt"""
    return PRODUCT_DESCRIPTION_PROMPT.format(product_info=product_info)


def get_keyword_extraction_prompt(
    product_info: str, keyword_count: int = 18, min_count: int = 15, max_count: int = 30
) -> str:
    """Get formatted keyword extraction prompt"""
    return KEYWORD_EXTRACTION_PROMPT.format(
        product_info=product_info,
        keyword_count=keyword_count,
        min_count=min_count,
        max_count=max_count,
    )


def get_category_matching_prompt(product_info: str, categories: str) -> str:
    """Get formatted category matching prompt"""
    return CATEGORY_MATCHING_PROMPT.format(
        product_info=product_info, categories=categories
    )


def get_tax_code_selection_prompt(product_info: str, tax_categories: str) -> str:
    """Get formatted tax code selection prompt"""
    return TAX_CODE_SELECTION_PROMPT.format(
        product_info=product_info, tax_categories=tax_categories
    )
