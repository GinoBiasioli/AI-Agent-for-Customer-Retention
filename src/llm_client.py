from __future__ import annotations

import json
from typing import Any

from src.segment_logic import build_business_summary, recommend_strategy

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


def generate_campaign_with_openai(
    prompt: str,
    api_key: str,
    model: str,
) -> dict[str, Any]:
    if OpenAI is None:
        raise RuntimeError("The openai package is not installed. Run `pip install -r requirements.txt`.")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[{"role": "user", "content": prompt}],
        text={"format": {"type": "json_object"}},
    )
    return json.loads(response.output_text)


def generate_campaign_fallback(segment: dict[str, Any], campaign_goal: str) -> dict[str, Any]:
    strategy = recommend_strategy(segment, campaign_goal)
    summary = build_business_summary(segment, campaign_goal)
    category = segment["preferred_category"]

    body_openers = {
        "onboarding": "Welcome them with a clear next step and reduce decision friction.",
        "reactivation": "Reconnect through relevance before using any stronger commercial push.",
        "win-back": "Frame the message as a thoughtful invitation to return, not a generic blast.",
        "loyalty": "Show appreciation first so the sequence protects long-term customer value.",
        "upsell": "Position the premium option as a better-fit next step rather than a hard sell.",
        "cross-sell": "Use the known category preference to suggest adjacent products naturally.",
        "promotional conversion": "Keep the offer simple and immediate because this segment responds to value cues.",
    }

    emails = [
        {
            "step": 1,
            "subject": f"{segment['segment_name']}: a more relevant way to shop {category}",
            "body": (
                f"{body_openers[campaign_goal]} Start with a message tied to {category}, "
                f"reflect the segment's recent behavior, and direct them toward a low-friction browse journey."
            ),
        },
        {
            "step": 2,
            "subject": f"Why customers are returning to {category}",
            "body": (
                "Build trust with social proof, product discovery, or benefit education. "
                "This second touch should deepen interest and make the CTA feel more credible."
            ),
        },
        {
            "step": 3,
            "subject": f"A timely reason to act on {category}",
            "body": (
                "Close with clear momentum. Use urgency, exclusivity, or an incentive that fits the segment economics "
                "without undermining the broader strategy."
            ),
        },
    ]

    return {
        "segment_name": segment["segment_name"],
        "campaign_goal": strategy["campaign_goal"],
        "recommended_strategy": strategy["recommended_strategy"],
        "tone": strategy["tone"],
        "cta": strategy["cta"],
        "send_timing": strategy["send_timing"],
        "rationale": summary,
        "emails": emails,
        "generation_mode": "fallback_template",
    }
