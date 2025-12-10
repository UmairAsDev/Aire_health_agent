from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
import pathlib
import sys
import uuid

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))
from config.config import settings

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class QdrantVectorStore:
    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URl, api_key=settings.QDRANT_API_KEY
        )

    async def embed(self, texts: List[str]) -> List[List[float]]:
        res = await self.openai_client.embeddings.create(
            model=settings.embedding_model, input=texts
        )
        return [d.embedding for d in res.data]

    async def qdrant_connection(
        self, collection_name: str, data: List[Dict[str, Any]], text_data: List[str]
    ):
        try:
            existing_collection = await self.client.collection_exists(collection_name)
            if not existing_collection:
                logger.info(f"Creating collection{collection_name}")
                await self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=settings.vector_size, distance=models.Distance.COSINE
                    ),
                )

            count_result = await self.client.count(collection_name=collection_name)
            if count_result.count > 0:
                logger.info(
                    f"Collection '{collection_name}' already has {count_result.count} items. Skipping upload."
                )
                return

            logger.info(f"Uploading {len(data)} items to '{collection_name}'...")
            await self._upload(collection_name, data, text_data)
            logger.info(f"Successfully uploaded data to '{collection_name}'.")
        except Exception as e:
            logger.warning(f"Error starting qdrant database{e}")

    async def _upload(
        self,
        collection_name: str,
        data: List[Dict[str, Any]],
        text_fields: List[str],
        batch_size: int = 100,
    ):

        total = len(data)
        for i in range(0, total, batch_size):
            batch = data[i : i + batch_size]

            texts_to_embed = []
            points = []

            for item in batch:
                text_content = ". ".join(
                    [
                        f"{field.capitalize()}: {str(item.get(field, ''))}"
                        for field in text_fields
                        if item.get(field)
                    ]
                )
                texts_to_embed.append(text_content)

            try:
                response = await self.openai_client.embeddings.create(
                    input=texts_to_embed, model=settings.embedding_model
                )
                embeddings = [e.embedding for e in response.data]

                for j, item in enumerate(batch):
                    unique_str = str(
                        item.get("id")
                        or item.get("product_tax_code")
                        or texts_to_embed[j]
                    )
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_str))

                    points.append(
                        models.PointStruct(
                            id=point_id, vector=embeddings[j], payload=item
                        )
                    )

                await self.client.upsert(collection_name=collection_name, points=points)
                print(f"Processed batch {i + len(batch)}/{total}")

            except Exception as e:
                print(f"Error processing batch {i}: {e}")

    async def search(
        self, collection_name: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Embeds query and searches Qdrant.
        """
        try:
            response = await self.openai_client.embeddings.create(
                input=query, model=settings.embedding_model
            )
            query_vector = response.data[0].embedding

            search_result = await self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )

            results = [hit.payload for hit in search_result.points]  # type:ignore
            return results #type:ignore

        except Exception as e:
            print(f"Search error in {collection_name}: {e}")
            return []

    async def close(self):
        await self.client.close()
