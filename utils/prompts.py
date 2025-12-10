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


PRODUCT_DESCRIPTION_PROMPT = """You are a product documentation specialist. Create an HTML table showing product details.

Product Information:
{product_info}

Guidelines:
- Create a clean HTML table with product specifications
- Use <table>, <tr>, <th>, and <td> tags
- Each row should have a specification name in <th> and value in <td>
- Include key specifications like: Brand, Size, Material, Color, Packaging, Certifications, etc.
- Extract values from the product information provided
- Keep it concise - include only the most important specifications (5-8 rows)
- Do NOT include any markdown formatting or code blocks
- Return ONLY the HTML table, no explanatory text

Example format:
<table><tr><th>Brand</th><td>McKesson</td></tr><tr><th>Powder-Free</th><td>Yes</td></tr><tr><th>Size</th><td>Small - 9.6 in</td></tr><tr><th>Cuff</th><td>Beaded</td></tr><tr><th>Fingertips</th><td>Textured</td></tr></table>

Return ONLY the HTML table, nothing else."""


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


CATEGORY_MATCHING_PROMPT = """You are a product categorization expert. Match the following product to the most appropriate category.

Product Information:
{product_info}

Available Categories:
{categories}

Instructions:
1. Analyze the product type, description, and features
2. Match to the most appropriate main category
3. Select the most relevant subcategory
4. Return in format: "Main Category > Subcategory"

If no perfect match exists, choose the closest category.

Return as JSON:
{{
  "category": "Main Category > Subcategory",
  "reasoning": "Brief explanation of why this category was chosen"
}}

Return ONLY valid JSON, no markdown formatting."""


TAX_CODE_SELECTION_PROMPT = """You are a tax classification expert specializing in medical and pharmaceutical products. Select the MOST ACCURATE tax code for the following product.

Product Information:
{product_info}

Retrieved Tax Categories (from database):
{tax_categories}

CRITICAL INSTRUCTIONS:
1. These products are primarily MEDICAL and PHARMACEUTICAL items from dermatology and healthcare departments
2. Analyze the product description, features, and intended use carefully
3. Match the product to the tax category that BEST describes its primary function and classification
4. Consider:
   - Is it a medical device, pharmaceutical, or medical supply?
   - What is its primary medical use?
   - Does it require FDA approval or medical certification?
   - Is it prescription or over-the-counter?
   - Is it a diagnostic tool, treatment device, or protective equipment?

5. Select the tax code with the HIGHEST relevance to the product's actual classification
6. Provide a confidence score (0.0 to 1.0) - only use high confidence (0.8+) if you're certain
7. If no perfect match exists, choose the closest category and explain why in reasoning

Return as JSON:
{{
  "tax_code": "selected_tax_code",
  "tax_code_name": "name of the tax category",
  "confidence": 0.85,
  "reasoning": "Detailed explanation of why this tax code was selected, including the product's primary classification and how it matches the tax category"
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
