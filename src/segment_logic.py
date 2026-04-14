from __future__ import annotations

from typing import Any

from src.utils import tier_from_numeric


def _describe_recency(recency_days: int) -> str:
    if recency_days <= 14:
        return "very recent"
    if recency_days <= 45:
        return "recent"
    if recency_days <= 90:
        return "stale"
    return "long inactive"


def infer_campaign_goal(segment: dict[str, Any]) -> str:
    stage = segment["lifecycle_stage"]
    churn_risk = segment["churn_risk"]
    engagement = segment["engagement_rate"]
    aov = segment["avg_order_value"]
    frequency = segment["purchase_frequency"]
    recency = segment["recency_days"]
    discount = segment["discount_sensitivity"]

    if stage == "onboarding" or frequency < 1.5 and recency <= 21:
        return "onboarding"
    if churn_risk == "high" and recency >= 90:
        return "win-back"
    if churn_risk == "high" or (engagement < 0.2 and recency >= 60):
        return "reactivation"
    if aov >= 150 and frequency >= 5 and churn_risk == "low":
        return "loyalty"
    if aov >= 120 and frequency >= 3:
        return "upsell"
    if discount == "high":
        return "promotional conversion"
    return "cross-sell"


def build_business_summary(segment: dict[str, Any], campaign_goal: str) -> str:
    recency_label = _describe_recency(segment["recency_days"])
    freq_tier = tier_from_numeric(segment["purchase_frequency"], 1.5, 5.0)
    aov_tier = tier_from_numeric(segment["avg_order_value"], 60, 150)
    engagement_tier = tier_from_numeric(segment["engagement_rate"], 0.2, 0.5)

    return (
        f"{segment['segment_name']} is a {segment['lifecycle_stage']} segment with {recency_label} activity, "
        f"{freq_tier} purchase frequency, {aov_tier} order value, and {engagement_tier} engagement. "
        f"Churn risk is {segment['churn_risk']} and discount sensitivity is {segment['discount_sensitivity']}. "
        f"The likely business objective is {campaign_goal}, centered on {segment['preferred_category']}."
    )


def recommend_strategy(segment: dict[str, Any], campaign_goal: str) -> dict[str, Any]:
    strategies = {
        "onboarding": {
            "recommended_strategy": "Teach the product range first, then build confidence, then prompt the second purchase.",
            "tone": "Warm, helpful, and confidence-building",
            "cta": "Explore bestsellers in the category",
            "send_timing": "Day 1 / Day 3 / Day 7",
        },
        "reactivation": {
            "recommended_strategy": "Lead with relevance, then show fresh value, then offer a gentle incentive if needed.",
            "tone": "Warm, persuasive, and benefit-led",
            "cta": "Come back and browse what is new",
            "send_timing": "Day 1 / Day 4 / Day 8",
        },
        "win-back": {
            "recommended_strategy": "Acknowledge the lapse, rebuild interest with curated value, then use a stronger recovery offer.",
            "tone": "Personal, reassuring, and urgency-aware",
            "cta": "Return with a limited-time reason to act",
            "send_timing": "Day 1 / Day 5 / Day 10",
        },
        "loyalty": {
            "recommended_strategy": "Reinforce brand affinity, reward loyalty, and deepen the relationship with exclusivity.",
            "tone": "Appreciative, premium, and relationship-focused",
            "cta": "Discover exclusive picks and member benefits",
            "send_timing": "Day 1 / Day 5 / Day 12",
        },
        "upsell": {
            "recommended_strategy": "Anchor on prior value, introduce a premium next step, and remove friction with guidance.",
            "tone": "Confident, consultative, and polished",
            "cta": "Upgrade to a higher-value option",
            "send_timing": "Day 1 / Day 4 / Day 9",
        },
        "cross-sell": {
            "recommended_strategy": "Connect their known interest to adjacent products and show how to build a fuller basket.",
            "tone": "Relevant, practical, and inspiring",
            "cta": "See complementary products",
            "send_timing": "Day 1 / Day 4 / Day 8",
        },
        "promotional conversion": {
            "recommended_strategy": "Use targeted offers carefully, highlight affordability, and create a clear reason to purchase now.",
            "tone": "Energetic, direct, and conversion-focused",
            "cta": "Shop the current offer",
            "send_timing": "Day 1 / Day 3 / Day 6",
        },
    }
    return {"campaign_goal": campaign_goal, **strategies[campaign_goal]}
