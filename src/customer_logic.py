from __future__ import annotations

from typing import Any

from src.utils import clamp_rate, tier_from_numeric


def _derive_engagement_rate(customer: dict[str, Any]) -> float:
    """Create a simple engagement proxy from transactional behavior when no true engagement field exists."""
    recency_component = max(0.0, 1.0 - min(customer["recency_days"], 180) / 180)
    frequency_component = min(customer["purchase_frequency"] / 10, 1.0)
    repeat_component = 1.0 if customer["repeat_customer"] else 0.35
    value_component = min(customer["avg_order_value"] / 250, 1.0)

    engagement = (
        recency_component * 0.4
        + frequency_component * 0.3
        + repeat_component * 0.15
        + value_component * 0.15
    )
    return round(clamp_rate(engagement), 2)


def _derive_churn_risk(customer: dict[str, Any]) -> str:
    recency_days = customer["recency_days"]
    frequency = customer["purchase_frequency"]

    if recency_days >= 120:
        return "high"
    if recency_days >= 60:
        return "high" if frequency <= 2 else "medium"
    if recency_days >= 30:
        return "medium"
    return "low"


def _derive_discount_sensitivity(customer: dict[str, Any]) -> str:
    aov = customer["avg_order_value"]
    revenue = customer["total_revenue"]
    frequency = customer["purchase_frequency"]

    if aov < 50 or (revenue < 150 and frequency <= 2):
        return "high"
    if aov < 110 or revenue < 400:
        return "medium"
    return "low"


def _derive_lifecycle_stage(customer: dict[str, Any], churn_risk: str) -> str:
    frequency = customer["purchase_frequency"]
    tenure = customer["tenure"]
    recency_days = customer["recency_days"]

    if frequency <= 1.5 and tenure <= 30:
        return "onboarding"
    if churn_risk == "high" and recency_days >= 120:
        return "win_back"
    if churn_risk == "high":
        return "reactivation"
    if frequency >= 5 and tenure >= 180:
        return "loyalty"
    if frequency >= 3:
        return "growth"
    return "active"


def _derive_preferred_category(customer: dict[str, Any]) -> str:
    # The transactional file has no category-level field, so we use a neutral ecommerce fallback.
    return "General Merchandise"


def _build_customer_archetype(customer: dict[str, Any], churn_risk: str, lifecycle_stage: str) -> str:
    value_tier = tier_from_numeric(customer["avg_order_value"], 60, 150)
    frequency_tier = tier_from_numeric(customer["purchase_frequency"], 1.5, 5.0)

    if lifecycle_stage == "onboarding":
        return f"New {value_tier.title()}-Value Customer"
    if churn_risk == "high":
        return f"At-Risk {value_tier.title()}-Value Buyer"
    if frequency_tier == "high" and value_tier == "high":
        return "VIP Loyalist"
    if frequency_tier == "high":
        return "Frequent Buyer"
    if value_tier == "high":
        return "High-Value Buyer"
    return f"{frequency_tier.title()}-Frequency {value_tier.title()}-Value Shopper"


def customer_to_campaign_input(customer: dict[str, Any]) -> dict[str, Any]:
    """
    Map customer-level transactional metrics into the structured marketing fields
    expected by the existing campaign generator.
    """
    churn_risk = _derive_churn_risk(customer)
    engagement_rate = _derive_engagement_rate(customer)
    discount_sensitivity = _derive_discount_sensitivity(customer)
    lifecycle_stage = _derive_lifecycle_stage(customer, churn_risk)
    preferred_category = _derive_preferred_category(customer)
    archetype = _build_customer_archetype(customer, churn_risk, lifecycle_stage)

    segment_name = f"Customer {customer['customer_id']} - {archetype}"

    return {
        "customer_id": customer["customer_id"],
        "segment_name": segment_name,
        "recency_days": customer["recency_days"],
        "purchase_frequency": customer["purchase_frequency"],
        "avg_order_value": customer["avg_order_value"],
        "total_revenue": customer["total_revenue"],
        "tenure": customer["tenure"],
        "repeat_customer": customer["repeat_customer"],
        "avg_days_between_purchases": customer["avg_days_between_purchases"],
        "engagement_rate": engagement_rate,
        "churn_risk": churn_risk,
        "discount_sensitivity": discount_sensitivity,
        "preferred_category": preferred_category,
        "lifecycle_stage": lifecycle_stage,
        "customer_brief": build_customer_brief(customer),
    }


def build_customer_brief(customer: dict[str, Any]) -> str:
    """Render the raw transactional metrics as a concise natural-language brief."""
    repeat_status = "repeat customer" if customer["repeat_customer"] else "first-time customer"
    avg_gap = customer["avg_days_between_purchases"]
    avg_gap_text = (
        f"Average days between orders is {avg_gap:.1f}."
        if avg_gap > 0
        else "Average days between orders is not available yet."
    )

    return (
        f"Days since last purchase: {customer['recency_days']}. "
        f"Number of purchases: {customer['purchase_frequency']:.1f}. "
        f"Average order value: {customer['avg_order_value']:.2f}. "
        f"Total revenue: {customer['total_revenue']:.2f}. "
        f"Tenure: {customer['tenure']} days. "
        f"Customer type: {repeat_status}. "
        f"{avg_gap_text}"
    )
