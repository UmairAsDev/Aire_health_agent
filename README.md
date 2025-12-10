# Aire Health AI - Product Categorization Agent

Production-ready LangGraph-based agent for automated product categorization and analysis.

## Features

- **🏷️ Name Pattern Generation**: Standardized product naming with brand, product name, size, and specifications
- **📋 Structured Summary**: Comprehensive product summary with overview, features, specs, use cases, and benefits
- **🔑 Keyword Extraction**: Generates exactly 15-20 relevant keywords for search and categorization
- **📁 Category Matching**: Automatic category assignment from product hierarchy (Main > Subcategory)
- **💰 Tax Code Suggestion**: AI-powered tax code recommendation with confidence scoring using Qdrant vector search

## Architecture

```
┌─────────────────┐
│  Product Data   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│           LangGraph Agent Workflow                      │
│                                                          │
│  1. Retrieve Tax Categories (Qdrant Vector Search)     │
│  2. Generate Name Pattern (LLM)                         │
│  3. Generate Structured Summary (LLM)                   │
│  4. Extract Keywords (LLM)                              │
│  5. Match Category (LLM)                                │
│  6. Suggest Tax Code (LLM)                              │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Analysis Output│
└─────────────────┘
```

## Tech Stack

- **LangGraph**: Agentic workflow orchestration
- **Qdrant**: Vector database for tax category retrieval
- **OpenAI GPT-4**: Intelligent product analysis
- **FastAPI**: High-performance API framework
- **Pydantic**: Data validation and serialization

## Installation

### Prerequisites

- Python 3.10+
- Qdrant instance (cloud or local)
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   cd /home/umair/projects/Aire_health_ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   
   # Qdrant
   QDRANT_URl=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   collection_name=tax_categories
   
   # Database (if needed)
   DATABASE_NAME=your_db_name
   HOST=localhost
   PORT=5432
   USERNAME=your_username
   PASSWORD=your_password
   ```

5. **Load tax categories into Qdrant**
   ```bash
   python database/vector_db/insert_data.py
   ```

6. **Verify Qdrant collection**
   ```bash
   python database/vector_db/verify_collection.py
   ```

## Usage

### Option 1: FastAPI Server

1. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Make API requests**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/analyze-product" \
     -H "Content-Type: application/json" \
     -d '{
       "Item_Num": 1110513,
       "Vendor_Name": "3M Company",
       "Item_Desc_Full": "Particulate Respirator / Surgical Mask 3M™ VFlex™ Medical N95",
       "UOM": "BX",
       "FEATURES_AND_BENEFITS_1": "NIOSH N95 Approved"
     }'
   ```

### Option 2: Direct Agent Usage

```python
import asyncio
from openai import AsyncOpenAI
from database.vector_db.vector_store import QdrantVectorStore
from app.core.product_agent import ProductCategorizationAgent
from config.config import settings

async def analyze_product():
    # Initialize
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    vector_store = QdrantVectorStore(openai_client=openai_client)
    agent = ProductCategorizationAgent(openai_client, vector_store)
    
    # Product data
    product = {
        "Item Num": 1110513,
        "Vendor Name": "3M Company",
        "Item Desc Full": "Particulate Respirator / Surgical Mask 3M™ VFlex™ Medical N95",
        # ... more fields
    }
    
    # Analyze
    result = await agent.analyze_product(product)
    
    print(f"Name Pattern: {result['name_pattern']}")
    print(f"Keywords: {result['keywords']}")
    print(f"Category: {result['category']}")
    print(f"Tax Code: {result['tax_code']}")
    
    # Cleanup
    await agent.close()

asyncio.run(analyze_product())
```

### Option 3: Run Examples

```bash
# Test agent with sample products
python tests/test_agent.py

# Run usage examples
python examples/example_usage.py
```

## API Endpoints

### POST /api/v1/analyze-product

Analyze a product and generate comprehensive categorization data.

**Request Body:**
```json
{
  "Item_Num": 1110513,
  "Vendor_Name": "3M Company",
  "Item_Desc_Short": "MASK, RESPIRATOR-DISP N95-MEDICAL ONESZ",
  "Item_Desc_Full": "Particulate Respirator / Surgical Mask 3M™ VFlex™ Medical N95",
  "UOM": "BX",
  "Price": "$31.82",
  "FEATURES_AND_BENEFITS_1": "NIOSH N95 Approved",
  "FEATURES_AND_BENEFITS_2": "FDA cleared for use as surgical mask"
}
```

**Response:**
```json
{
  "name_pattern": "3M VFlex N95 Medical Respirator Mask - One Size - 50/Box - NIOSH Approved",
  "structured_summary": {
    "overview": "The 3M VFlex N95 Medical Respirator is a NIOSH-approved...",
    "key_features": ["NIOSH N95 Approved", "FDA cleared", ...],
    "specifications": {"certification": "NIOSH N95", ...},
    "use_cases": ["Healthcare settings", ...],
    "benefits": ["Superior filtration efficiency", ...]
  },
  "keywords": ["N95 respirator", "surgical mask", ...],
  "category": "Medical Supplies > Disposable",
  "tax_code": "51020",
  "tax_code_name": "Prescription Drugs",
  "tax_code_confidence": 0.45,
  "tax_code_reasoning": "Medical supplies often fall under..."
}
```

### GET /api/v1/health

Check API health and Qdrant connection status.

### GET /api/v1/categories

Get available product categories.

## Project Structure

```
Aire_health_ai/
├── app/
│   ├── core/
│   │   ├── agent_state.py       # Agent state schema
│   │   ├── agent_tools.py       # LangGraph node functions
│   │   └── product_agent.py     # Main agent orchestration
│   └── service/
│       ├── routes.py            # FastAPI routes
│       └── schemas.py           # Pydantic models
├── config/
│   └── config.py                # Configuration settings
├── database/
│   └── vector_db/
│       ├── vector_store.py      # Qdrant vector store
│       ├── insert_data.py       # Load tax categories
│       └── verify_collection.py # Verify Qdrant setup
├── data/
│   ├── tax_categories.json      # Tax category database
│   ├── product_categories.json  # Product category hierarchy
│   └── aire_mckesson_catalog.json # Sample product catalog
├── utils/
│   ├── helper.py                # Helper functions
│   └── prompts.py               # LLM prompts
├── examples/
│   ├── example_usage.py         # Usage examples
│   └── example_output.md        # Sample outputs
├── tests/
│   └── test_agent.py            # Agent tests
├── main.py                      # FastAPI application
└── requirements.txt             # Dependencies
```

## Configuration

Key configuration parameters in `config/config.py`:

- `model_name`: OpenAI model (default: `gpt-4o`)
- `agent_temperature`: LLM temperature (default: `0.3`)
- `retrieval_top_k`: Number of tax categories to retrieve (default: `5`)
- `keyword_count_min`: Minimum keywords (default: `15`)
- `keyword_count_max`: Maximum keywords (default: `20`)

## Testing

```bash
# Test agent functionality
python tests/test_agent.py

# Verify Qdrant collection
python database/vector_db/verify_collection.py

# Run example usage
python examples/example_usage.py
```

## Troubleshooting

### Qdrant Connection Issues

1. Verify Qdrant URL and API key in `.env`
2. Check collection exists: `python database/vector_db/verify_collection.py`
3. Reload data if needed: `python database/vector_db/insert_data.py`

### OpenAI API Errors

1. Verify API key is valid
2. Check rate limits and quotas
3. Ensure model name is correct (`gpt-4o`)

### Keyword Count Issues

The agent targets 15-20 keywords. If you get warnings:
- Adjust `keyword_count_min` and `keyword_count_max` in config
- Check LLM prompt in `utils/prompts.py`

## License

Proprietary - Aire Health AI

## Support

For issues or questions, contact the development team.
