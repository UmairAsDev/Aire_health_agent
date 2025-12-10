import pathlib
import sys
import asyncio
import logging

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))
from openai import AsyncOpenAI
from config.config import settings
from database.vector_db.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def verify_collection():
    """Verify Qdrant collection and test search functionality"""
    try:
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, max_retries=5)
        vector_store = QdrantVectorStore(openai_client=openai_client)

        collection_name = settings.collection_name

        logger.info(f"Checking if collection '{collection_name}' exists...")
        exists = await vector_store.client.collection_exists(collection_name)

        if not exists:
            logger.error(f"Collection '{collection_name}' does not exist!")
            logger.info(
                "Please run insert_data.py first to create and populate the collection"
            )
            return

        logger.info(f"✓ Collection '{collection_name}' exists")

        collection_info = await vector_store.client.get_collection(collection_name)
        logger.info(f"Collection status: {collection_info.status}")
        logger.info(f"Vector size: {collection_info.config.params.vectors.size}")#type:ignore
        logger.info(
            f"Distance metric: {collection_info.config.params.vectors.distance}"# type:ignore
        )

        count_result = await vector_store.client.count(collection_name=collection_name)
        logger.info(f"Total documents: {count_result.count}")

        logger.info("\n" + "=" * 60)
        logger.info("Testing search functionality...")
        logger.info("=" * 60)

        test_queries = [
            "prescription drugs and medications",
            "medical masks and protective equipment",
            "software and digital services",
            "clothing and apparel",
        ]

        for query in test_queries:
            logger.info(f"\nQuery: '{query}'")
            results = await vector_store.search(
                collection_name=collection_name, query=query, top_k=3
            )

            if results:
                logger.info(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    logger.info(f"  {i}. {result.get('name', 'N/A')}")
                    logger.info(
                        f"     Tax Code: {result.get('product_tax_code', 'N/A')}"
                    )
                    logger.info(
                        f"     Description: {result.get('description', 'N/A')[:100]}..."
                    )
            else:
                logger.warning(f"No results found for query: '{query}'")

        logger.info("\n" + "=" * 60)
        logger.info("Verification complete!")
        logger.info("=" * 60)

        await vector_store.close()

    except Exception as e:
        logger.error(f"Error during verification: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(verify_collection())
