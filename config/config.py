from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    embedding_model: str = "text-embedding-ada-002"
    vector_size: int = 1536
    model_name: str = "gpt-4o"

    agent_temperature: float = 0.3
    agent_max_tokens: int = 2000
    retrieval_top_k: int = 5
    keyword_count_min: int = 15
    keyword_count_max: int = 30
    DATABASE_NAME: str
    HOST: str
    PORT: str
    USERNAME: str
    PASSWORD: str
    QDRANT_URl: str
    QDRANT_API_KEY: str
    collection_name: str
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    TAX_CATEGORIES_FILE: str = os.path.join(DATA_DIR, "tax_categories.json")
    PRODUCT_CATEGORIES_FILE: str = os.path.join(DATA_DIR, "product_categories.json")
    TAX_EMBEDDINGS_CACHE: str = os.path.join(DATA_DIR, "tax_embeddings.json")
    CATEGORY_EMBEDDINGS_CACHE: str = os.path.join(DATA_DIR, "category_embeddings.json")

    class Config:
        env_file = ".env"


settings = Settings()  # type:ignore
