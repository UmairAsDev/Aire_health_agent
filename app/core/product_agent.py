import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from openai import AsyncOpenAI
from database.vector_db.vector_store import QdrantVectorStore
from app.core.agent_state import AgentState, ProductAnalysisOutput
from app.core.agent_tools import ProductAgentTools
from config.config import settings

logger = logging.getLogger(__name__)


class ProductCategorizationAgent:
    """
    LangGraph-based agent for product categorization and analysis.

    Workflow:
    1. Retrieve tax categories from Qdrant
    2. Generate name pattern
    3. Generate structured summary
    4. Extract keywords
    5. Match category
    6. Suggest tax code
    """

    def __init__(self, openai_client: AsyncOpenAI, vector_store: QdrantVectorStore):
        self.openai_client = openai_client
        self.vector_store = vector_store
        self.tools = ProductAgentTools(openai_client, vector_store)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""

        workflow = StateGraph(AgentState)

        workflow.add_node("retrieve_tax_categories", self.tools.retrieve_tax_categories)
        workflow.add_node("generate_name_pattern", self.tools.generate_name_pattern)
        workflow.add_node(
            "generate_product_summary", self.tools.generate_product_summary
        )
        workflow.add_node(
            "generate_product_description", self.tools.generate_product_description
        )
        workflow.add_node("extract_keywords", self.tools.extract_keywords)
        workflow.add_node("match_category", self.tools.match_category)
        workflow.add_node("suggest_tax_code", self.tools.suggest_tax_code)

        workflow.set_entry_point("retrieve_tax_categories")

        workflow.add_edge("retrieve_tax_categories", "generate_name_pattern")
        workflow.add_edge("generate_name_pattern", "generate_product_summary")
        workflow.add_edge("generate_product_summary", "generate_product_description")
        workflow.add_edge("generate_product_description", "extract_keywords")
        workflow.add_edge("extract_keywords", "match_category")
        workflow.add_edge("match_category", "suggest_tax_code")
        workflow.add_edge("suggest_tax_code", END)

        return workflow.compile()  # type:ignore

    async def analyze_product(
        self, product_data: Dict[str, Any]
    ) -> ProductAnalysisOutput:
        """
        Analyze a product and generate all outputs

        Args:
            product_data: Product data from catalog

        Returns:
            ProductAnalysisOutput with all generated fields
        """
        try:
            logger.info(
                f"Starting product analysis for: {product_data.get('Item Num', 'Unknown')}"
            )

            initial_state: AgentState = {
                "product_data": product_data,
                "product_info_formatted": "",
                "retrieved_tax_categories": [],
                "available_categories": {},
                "name_pattern": "",
                "product_summary": "",
                "product_description": "",
                "keywords": [],
                "category": "",
                "tax_code_result": {
                    "tax_code": "",
                    "tax_code_name": "",
                    "confidence": 0.0,
                    "reasoning": "",
                },
                "errors": [],
                "processing_steps": [],
            }

            final_state = await self.graph.ainvoke(initial_state)  # type:ignore

            # Log processing steps (deduplicate to avoid showing accumulated steps)
            steps = final_state.get("processing_steps", [])
            unique_steps = []
            seen = set()
            for step in steps:
                if step not in seen:
                    unique_steps.append(step)
                    seen.add(step)
                    logger.info(f"   ✓ {step}")

            if final_state.get("errors"):
                for error in final_state["errors"]:
                    logger.warning(f"  ⚠ {error}")

            output: ProductAnalysisOutput = {
                "name_pattern": final_state["name_pattern"],
                "product_summary": final_state["product_summary"],
                "product_description": final_state["product_description"],
                "keywords": final_state["keywords"],
                "category": final_state["category"],
                "tax_code": final_state["tax_code_result"]["tax_code"],
                "tax_code_name": final_state["tax_code_result"]["tax_code_name"],
                "tax_code_confidence": final_state["tax_code_result"]["confidence"],
                "tax_code_reasoning": final_state["tax_code_result"]["reasoning"],
            }

            logger.info(
                f"Product analysis complete for: {product_data.get('Item Num', 'Unknown')}"
            )

            return output

        except Exception as e:
            logger.error(f"Error in product analysis: {str(e)}", exc_info=True)
            raise

    async def close(self):
        """Close connections"""
        await self.vector_store.close()


_agent_instance = None


async def get_agent() -> ProductCategorizationAgent:
    """Get or create agent instance"""
    global _agent_instance

    if _agent_instance is None:
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, max_retries=5)
        vector_store = QdrantVectorStore(openai_client=openai_client)
        _agent_instance = ProductCategorizationAgent(openai_client, vector_store)
        logger.info("Product categorization agent initialized")

    return _agent_instance


async def shutdown_agent():
    """Shutdown agent and close connections"""
    global _agent_instance

    if _agent_instance is not None:
        await _agent_instance.close()
        _agent_instance = None
        logger.info("Product categorization agent shutdown")
