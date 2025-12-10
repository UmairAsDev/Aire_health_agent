import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
from database.vector_db.vector_store import QdrantVectorStore
from utils.helper import (
    format_product_for_llm,
    parse_llm_json_response,
    get_category_hierarchy,
    validate_keyword_count,
    clean_keywords,
)
from utils.prompts import (
    get_name_pattern_prompt,
    get_product_summary_prompt,
    get_product_description_prompt,
    get_keyword_extraction_prompt,
    get_category_matching_prompt,
    get_tax_code_selection_prompt,
)
from config.config import settings
from app.core.agent_state import AgentState, TaxCodeResult

logger = logging.getLogger(__name__)


class ProductAgentTools:
    """Tools for the product categorization agent"""

    def __init__(self, openai_client: AsyncOpenAI, vector_store: QdrantVectorStore):
        self.openai_client = openai_client
        self.vector_store = vector_store

    async def retrieve_tax_categories(self, state: AgentState) -> AgentState:
        """
        Node: Retrieve relevant tax categories from Qdrant
        """
        try:
            logger.info("Retrieving tax categories from Qdrant...")

            product_info = format_product_for_llm(state["product_data"])
            state["product_info_formatted"] = product_info

            results = await self.vector_store.search(
                collection_name=settings.collection_name,
                query=product_info,
                top_k=settings.retrieval_top_k,
            )

            state["retrieved_tax_categories"] = results
            state["processing_steps"].append(f"Retrieved {len(results)} tax categories")

            logger.info(f"Retrieved {len(results)} tax categories")

        except Exception as e:
            error_msg = f"Error retrieving tax categories: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["retrieved_tax_categories"] = []

        return state

    async def generate_name_pattern(self, state: AgentState) -> AgentState:
        """
        Node: Generate standardized product name pattern
        """
        try:
            logger.info("Generating name pattern...")

            prompt = get_name_pattern_prompt(state["product_info_formatted"])

            response = await self.openai_client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "system", "content": "You are a product naming expert."},
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.agent_temperature,
                max_tokens=settings.agent_max_tokens,
            )

            name_pattern = response.choices[0].message.content.strip()  # type:ignore
            state["name_pattern"] = name_pattern
            state["processing_steps"].append("Generated name pattern")

            logger.info(f"Generated name pattern: {name_pattern}")

        except Exception as e:
            error_msg = f"Error generating name pattern: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["name_pattern"] = "Error generating name pattern"

        return state

    async def generate_product_summary(self, state: AgentState) -> AgentState:
        """
        Node: Generate product summary in 'About this Product' bullet-point format
        """
        try:
            logger.info("Generating product summary...")

            prompt = get_product_summary_prompt(state["product_info_formatted"])

            response = await self.openai_client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product documentation specialist.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.agent_temperature,
                max_tokens=settings.agent_max_tokens,
            )

            product_summary = response.choices[0].message.content
            if product_summary:
                state["product_summary"] = product_summary.strip()
                state["processing_steps"].append("Generated product summary")
                logger.info("Generated product summary")
            else:
                raise ValueError("Failed to generate product summary")

        except Exception as e:
            error_msg = f"Error generating product summary: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["product_summary"] = "Error generating summary"

        return state

    async def generate_product_description(self, state: AgentState) -> AgentState:
        """
        Node: Generate product description as HTML table
        """
        try:
            logger.info("Generating product description...")

            prompt = get_product_description_prompt(state["product_info_formatted"])

            response = await self.openai_client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product documentation specialist.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.agent_temperature,
                max_tokens=settings.agent_max_tokens,
            )

            product_description = response.choices[0].message.content
            if product_description:
                state["product_description"] = product_description.strip()
                state["processing_steps"].append("Generated product description")
                logger.info("Generated product description")
            else:
                raise ValueError("Failed to generate product description")

        except Exception as e:
            error_msg = f"Error generating product description: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["product_description"] = "Error generating description"

        return state

    async def extract_keywords(self, state: AgentState) -> AgentState:
        """
        Node: Extract 15-20 relevant keywords
        """
        try:
            logger.info("Extracting keywords...")

            target_count = (
                settings.keyword_count_min + settings.keyword_count_max
            ) // 2

            prompt = get_keyword_extraction_prompt(
                state["product_info_formatted"],
                keyword_count=target_count,
                min_count=settings.keyword_count_min,
                max_count=settings.keyword_count_max,
            )

            response = await self.openai_client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product SEO expert. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.agent_temperature,
                max_tokens=settings.agent_max_tokens,
                response_format={"type": "json_object"},
            )

            keywords_json = parse_llm_json_response(
                response.choices[0].message.content
            )  # type:ignore

            if keywords_json and "keywords" in keywords_json:
                keywords = clean_keywords(keywords_json["keywords"])

                if not validate_keyword_count(
                    keywords, settings.keyword_count_min, settings.keyword_count_max
                ):
                    logger.warning(
                        f"Keyword count {len(keywords)} outside range {settings.keyword_count_min}-{settings.keyword_count_max}"
                    )
                    if len(keywords) < settings.keyword_count_min:

                        keywords.extend(
                            [
                                f"keyword_{i}"
                                for i in range(
                                    settings.keyword_count_min - len(keywords)
                                )
                            ]
                        )
                    elif len(keywords) > settings.keyword_count_max:
                        keywords = keywords[: settings.keyword_count_max]

                state["keywords"] = keywords
                state["processing_steps"].append(f"Extracted {len(keywords)} keywords")
                logger.info(f"Extracted {len(keywords)} keywords")
            else:
                raise ValueError("Failed to parse keywords JSON")

        except Exception as e:
            error_msg = f"Error extracting keywords: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["keywords"] = []

        return state

    async def match_category(self, state: AgentState) -> AgentState:
        """
        Node: Match product to category
        """
        try:
            logger.info("Matching category...")

            categories = get_category_hierarchy()
            state["available_categories"] = categories

            categories_str = json.dumps(categories, indent=2)

            prompt = get_category_matching_prompt(
                state["product_info_formatted"], categories_str
            )

            response = await self.openai_client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product categorization expert. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.agent_temperature,
                max_tokens=settings.agent_max_tokens,
                response_format={"type": "json_object"},
            )

            category_json = parse_llm_json_response(
                response.choices[0].message.content
            )  # type:ignore

            if category_json and "category" in category_json:
                state["category"] = category_json["category"]
                state["processing_steps"].append(
                    f"Matched category: {category_json['category']}"
                )
                logger.info(f"Matched category: {category_json['category']}")
            else:
                raise ValueError("Failed to parse category JSON")

        except Exception as e:
            error_msg = f"Error matching category: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["category"] = "Uncategorized"

        return state

    async def suggest_tax_code(self, state: AgentState) -> AgentState:
        """
        Node: Suggest tax code from retrieved categories
        """
        try:
            logger.info("Suggesting tax code...")

            tax_cats = state.get("retrieved_tax_categories", [])
            if not tax_cats:
                raise ValueError("No tax categories retrieved")

            tax_cats_str = json.dumps(
                [
                    {
                        "code": cat.get("product_tax_code"),
                        "name": cat.get("name"),
                        "description": cat.get("description"),
                    }
                    for cat in tax_cats
                ],
                indent=2,
            )

            prompt = get_tax_code_selection_prompt(
                state["product_info_formatted"], tax_cats_str
            )

            response = await self.openai_client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a tax classification expert. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.agent_temperature,
                max_tokens=settings.agent_max_tokens,
                response_format={"type": "json_object"},
            )

            tax_json = parse_llm_json_response(
                response.choices[0].message.content
            )  # type:ignore

            if tax_json:
                state["tax_code_result"] = TaxCodeResult(
                    tax_code=tax_json.get("tax_code", ""),
                    tax_code_name=tax_json.get("tax_code_name", ""),
                    confidence=tax_json.get("confidence", 0.0),
                    reasoning=tax_json.get("reasoning", ""),
                )
                state["processing_steps"].append(
                    f"Suggested tax code: {tax_json.get('tax_code')}"
                )
                logger.info(
                    f"Suggested tax code: {tax_json.get('tax_code')} (confidence: {tax_json.get('confidence')})"
                )
            else:
                raise ValueError("Failed to parse tax code JSON")

        except Exception as e:
            error_msg = f"Error suggesting tax code: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
            state["tax_code_result"] = TaxCodeResult(
                tax_code="",
                tax_code_name="",
                confidence=0.0,
                reasoning=f"Error: {str(e)}",
            )

        return state
