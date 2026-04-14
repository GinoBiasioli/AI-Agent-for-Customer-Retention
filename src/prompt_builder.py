from __future__ import annotations

from typing import Any


def build_campaign_prompt(
    segment: dict[str, Any],
    business_summary: str,
    strategy_recommendation: dict[str, Any],
) -> str:
    customer_brief = segment.get("customer_brief")
    customer_brief_section = f"\nCustomer brief:\n{customer_brief}\n" if customer_brief else ""

    return f"""
You are a senior CRM strategist and lifecycle marketer for an ecommerce brand.

Your task is to convert customer-level transactional context into a campaign strategy and a 3-email lifecycle sequence that a marketing team could realistically review, edit, and send.

Return JSON only with exactly these top-level keys:
- segment_name
- campaign_goal
- recommended_strategy
- tone
- cta
- send_timing
- rationale
- emails

The "emails" field must be an array of 3 objects. Each object must contain:
- step
- subject
- body

Rules:
- Keep the writing business-oriented, realistic, and commercially useful.
- Align the copy tightly with the inferred campaign goal and the segment economics.
- Do not invent customer facts beyond the provided customer brief and derived fields.
- Make the sequence feel progressive from email 1 to email 3, with a clear strategic escalation.
- Write like a real lifecycle marketer, not a generic AI assistant.
- Default to paragraph-style email copy. Do not use bullet lists unless they are truly necessary.
- Keep each subject line concise, natural, and campaign-ready. Avoid placeholders and robotic phrasing.
- Each email body should feel like a real draft: specific, persuasive, and easy to imagine in a brand CRM flow.
- Avoid sounding repetitive across the three emails.
- Mention the preferred category naturally when relevant, but do not force it awkwardly.
- The rationale should explain why this campaign goal, tone, cadence, and CTA make sense for the segment.

Email sequence guidance:
- Email 1 should introduce the core angle and establish relevance.
- Email 2 should deepen trust or interest with a new reason to engage.
- Email 3 should create momentum with urgency, exclusivity, or a clear next step that fits the segment.

Copy quality guidance:
- Prefer polished ecommerce CRM language over abstract strategy jargon.
- Avoid phrases like "valued customer," "we are excited," "journey," or other generic filler unless they truly fit.
- Avoid over-discounting premium or low-discount-sensitivity segments.
- For onboarding, focus on confidence, discovery, and first-to-second purchase momentum.
- For loyalty or upsell, sound premium and relationship-aware.
- For reactivation or win-back, sound relevant and persuasive without sounding desperate.
- For promotional conversion, make the commercial offer clear without making the brand sound cheap.

Derived marketing fields:
{segment}

{customer_brief_section}

Business summary:
{business_summary}

Pre-inferred strategy guidance:
{strategy_recommendation}
""".strip()
