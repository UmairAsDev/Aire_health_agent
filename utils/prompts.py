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
4. Key specifications (3-4 most important features)

Format the name pattern as: [Brand] [Product Name] [Size] - [Key Specs]

Example: "3M VFlex N95 Medical Respirator Mask - One Size - 50/Box - NIOSH Approved"

Return ONLY the formatted name pattern, nothing else."""


PRODUCT_SUMMARY_PROMPT = """You are a product documentation specialist. Create a product summary in "About this Product" format with bullet points.

Product Information:
{product_info}

Guidelines:
- Start with "About this Product" as the header
- Add a blank line after the header
- Create 4-6 bullet points using the "•" symbol
- Each bullet point should highlight key features, benefits, or specifications
- Extract information from FEATURES_AND_BENEFITS fields and product description
- Make bullet points concise and informative
- Focus on what makes the product unique and valuable

Example format:
About this Product

• McKesson Confiderm® 3.5C Nitrile Exam Gloves Small
• Powder-Free
• Tested for use with Chemotherapy Drugs using ASTM D6978-05
• Textured fingertips provide excellent tactile sensitivity and dexterity
• Improved conformability provides superior fit and extended wear comfort

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


KEYWORD_EXTRACTION_PROMPT = """You are a product SEO and categorization expert. Generate exactly {keyword_count} relevant keywords for the following product.

Product Information:
{product_info}

Guidelines for keyword generation:
1. Include product type and category keywords
2. Include brand and manufacturer keywords
3. Include technical specifications and features
4. Include use case and application keywords
5. Include industry-specific terminology
6. Mix of broad and specific terms
7. Include common search terms users might use
8. Avoid duplicates and very similar terms
9. Also generate the keywords of the the brand name.

Generate EXACTLY {keyword_count} keywords (between {min_count} and {max_count}).

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


TAX_CODE_SELECTION_PROMPT = """You are a tax classification expert. Select the most appropriate tax code for the following product.

Product Information:
{product_info}

Retrieved Tax Categories (from database):
{tax_categories}

Instructions:
1. Analyze the product type, description, and intended use
2. Compare with the retrieved tax category descriptions
3. Select the best matching tax code
4. Provide a confidence score (0.0 to 1.0)
5. Explain your reasoning

Consider:
- Product type and classification
- Intended use and application
- Regulatory requirements
- Industry standards

Return as JSON:
{{
  "tax_code": "selected_tax_code",
  "tax_code_name": "name of the tax category",
  "confidence": 0.85,
  "reasoning": "Explanation of why this tax code was selected and confidence level"
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
