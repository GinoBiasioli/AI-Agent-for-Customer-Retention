from __future__ import annotations

from typing import Any

from src.config import Settings
from src.llm_client import generate_campaign_fallback, generate_campaign_with_openai
from src.prompt_builder import build_campaign_prompt
from src.segment_logic import build_business_summary, infer_campaign_goal, recommend_strategy


def generate_campaign(segment: dict[str, Any], settings: Settings) -> dict[str, Any]:
    campaign_goal = infer_campaign_goal(segment)
    strategy = recommend_strategy(segment, campaign_goal)
    summary = build_business_summary(segment, campaign_goal)
    prompt = build_campaign_prompt(segment, summary, strategy)

    if settings.openai_api_key:
        try:
            campaign = generate_campaign_with_openai(
                prompt=prompt,
                api_key=settings.openai_api_key,
                model=settings.openai_model,
            )
            campaign["generation_mode"] = "openai"
        except Exception as exc:
            print(f"OpenAI generation failed for {segment['segment_name']}: {exc}. Falling back to template mode.")
            campaign = generate_campaign_fallback(segment, campaign_goal)
    else:
        campaign = generate_campaign_fallback(segment, campaign_goal)

    campaign["segment_summary"] = summary
    return campaign


def generate_campaigns(segments: list[dict[str, Any]], settings: Settings) -> list[dict[str, Any]]:
    campaigns: list[dict[str, Any]] = []
    total_segments = len(segments)

    for index, segment in enumerate(segments, start=1):
        print(f"[{index}/{total_segments}] Processing segment: {segment['segment_name']}")
        campaign = generate_campaign(segment, settings)
        print(
            f"[{index}/{total_segments}] Finished segment: {segment['segment_name']} "
            f"({campaign['generation_mode']})"
        )
        campaigns.append(campaign)

    return campaigns
