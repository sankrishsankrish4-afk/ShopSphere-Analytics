from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CartRequest(BaseModel):
    cart_items: list[int] = Field(..., description="Product IDs currently in the cart")
    customer_id: int | None = Field(default=None, description="Optional customer ID for segment-aware rules")


class RecommendationResponse(BaseModel):
    product_id: int = Field(..., description="Recommended product ID")
    name: str = Field(..., description="Recommended product name")
    confidence: float = Field(..., description="Probability of buying this product given the cart")
    lift: float = Field(..., description="Strength of association compared with chance")
    reason: str = Field(..., description="Human-readable explanation for the recommendation")

    model_config = ConfigDict(from_attributes=True)


class RuleResponse(BaseModel):
    id: int
    antecedent: list[int] = Field(..., description="Cart-side itemset")
    consequent: list[int] = Field(..., description="Recommended itemset")
    support: float = Field(..., description="P(antecedent and consequent)")
    confidence: float = Field(..., description="P(consequent | antecedent)")
    lift: float = Field(..., description="Association strength versus random chance")
    algorithm: str = Field(..., description="apriori, fpgrowth, or eclat")
    segment: str | None = Field(default=None, description="Optional persona-specific scope")

    model_config = ConfigDict(from_attributes=True)


class RuleListResponse(BaseModel):
    rules: list[RuleResponse]
    total: int


class ClusterResponse(BaseModel):
    customer_id: int
    cluster_label: int
    persona_name: str
    features: dict[str, Any]


class AnalyticsSummaryResponse(BaseModel):
    total_transactions: int
    total_products: int
    total_rules: int
    avg_lift: float
    top_categories: list[str]
