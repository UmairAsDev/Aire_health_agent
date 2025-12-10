import pathlib
import sys
import json
import logging
import asyncio

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))
from openai import AsyncOpenAI
from config.config import settings
from database.vector_db.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def insert_tax_categories():
    """Extract tax categories from JSON and upsert into Qdrant vector store"""
    try:
        
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, max_retries=5)
        vector_store = QdrantVectorStore(openai_client=openai_client)

        logger.info(f"Loading tax categories from: {settings.TAX_CATEGORIES_FILE}")
        with open(settings.TAX_CATEGORIES_FILE, "r") as f:
            json_data = json.load(f)

        data_items = []
        for item in json_data:
            if item.get("type") == "table" and item.get("name") == "tax_categories":
                data_items = item.get("data", [])
                break

        if not data_items:
            logger.error("No tax_categories data found in JSON file")
            return

        logger.info(f"Found {len(data_items)} tax categories")

        text_fields = ["name", "description", "product_tax_code"]

        # Upload to Qdrant
        await vector_store.qdrant_connection(
            collection_name=settings.collection_name,
            data=data_items,
            text_data=text_fields,
        )

        logger.info("Successfully inserted tax categories into Qdrant")

        # Close connection
        await vector_store.close()

    except FileNotFoundError:
        logger.error(f"Tax categories file not found: {settings.TAX_CATEGORIES_FILE}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Error processing tax categories: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(insert_tax_categories())
