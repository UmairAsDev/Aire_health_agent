from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator


class TaxCodeResult(TypedDict):
    """Tax code selection result"""

    tax_code: str
    tax_code_name: str
    confidence: float
    reasoning: str


class AgentState(TypedDict):
    """
    State for the product categorization agent.

    This state is passed between nodes in the LangGraph workflow.
    """

    product_data: Dict[str, Any]

    product_info_formatted: str
    retrieved_tax_categories: List[Dict[str, Any]]
    available_categories: Dict[str, List[str]]

    name_pattern: str
    product_summary: str
    product_description: str
    keywords: List[str]
    category: Dict[str, Any]
    tax_code_result: TaxCodeResult

    total_tokens: int  # Track total tokens used across all LLM calls

    errors: Annotated[List[str], operator.add]

    processing_steps: Annotated[List[str], operator.add]


class ProductAnalysisInput(TypedDict):
    """Input schema for product analysis"""

    product_data: Dict[str, Any]


class ProductAnalysisOutput(TypedDict):
    """Complete output schema for product analysis"""

    name_pattern: str
    product_summary: str
    product_description: str
    keywords: List[str]
    category: Dict[str, Any]  
    tax_code: str
    tax_code_name: str
    tax_code_confidence: float
    tax_code_reasoning: str
    total_tokens: int  
