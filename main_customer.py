from __future__ import annotations

import csv
from typing import Any

from src.campaign_generator import generate_campaign
from src.config import get_settings
from src.customer_logic import customer_to_campaign_input
from src.load_data import load_customer_transactions
from src.utils import write_json


SAMPLE_SIZE = 5
SAMPLE_SEED = 42


def flatten_customer_campaign(record: dict[str, Any]) -> dict[str, Any]:
    campaign = record["campaign"]
    emails = campaign["emails"]
    input_metrics = record["input_metrics"]
    derived_fields = record["derived_fields"]

    return {
        "customer_id": record["customer_id"],
        "segment_name": derived_fields["segment_name"],
        "campaign_goal": campaign["campaign_goal"],
        "recommended_strategy": campaign["recommended_strategy"],
        "tone": campaign["tone"],
        "cta": campaign["cta"],
        "send_timing": campaign["send_timing"],
        "recency_days": input_metrics["recency_days"],
        "purchase_frequency": input_metrics["purchase_frequency"],
        "avg_order_value": input_metrics["avg_order_value"],
        "total_revenue": input_metrics["total_revenue"],
        "tenure": input_metrics["tenure"],
        "repeat_customer": input_metrics["repeat_customer"],
        "avg_days_between_purchases": input_metrics["avg_days_between_purchases"],
        "derived_engagement_rate": derived_fields["engagement_rate"],
        "derived_churn_risk": derived_fields["churn_risk"],
        "derived_discount_sensitivity": derived_fields["discount_sensitivity"],
        "derived_preferred_category": derived_fields["preferred_category"],
        "derived_lifecycle_stage": derived_fields["lifecycle_stage"],
        "customer_brief": derived_fields["customer_brief"],
        "email_1_subject": emails[0]["subject"],
        "email_1_body": emails[0]["body"],
        "email_2_subject": emails[1]["subject"],
        "email_2_body": emails[1]["body"],
        "email_3_subject": emails[2]["subject"],
        "email_3_body": emails[2]["body"],
        "rationale": campaign["rationale"],
        "generation_mode": campaign["generation_mode"],
    }


def write_csv(path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_customer_campaign_records(
    sampled_customers: list[dict[str, Any]],
    settings,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    total_customers = len(sampled_customers)

    for index, customer in enumerate(sampled_customers, start=1):
        customer_id = customer["customer_id"]
        print(f"[{index}/{total_customers}] Transforming customer: {customer_id}")
        derived_fields = customer_to_campaign_input(customer)
        print(f"[{index}/{total_customers}] Generating campaign: {derived_fields['segment_name']}")
        campaign = generate_campaign(derived_fields, settings)
        records.append(
            {
                "customer_id": customer_id,
                "input_metrics": customer,
                "derived_fields": derived_fields,
                "campaign": campaign,
                "generation_mode": campaign["generation_mode"],
            }
        )
        print(f"[{index}/{total_customers}] Finished customer: {customer_id} ({campaign['generation_mode']})")

    return records


def main() -> None:
    settings = get_settings()
    print(f"Loading customer transactions from: {settings.customer_input_csv}")
    all_customers, sampled_customers = load_customer_transactions(
        settings.customer_input_csv,
        sample_size=SAMPLE_SIZE,
        seed=SAMPLE_SEED,
    )
    sampled_ids = [customer["customer_id"] for customer in sampled_customers]

    print(f"Loaded {len(all_customers)} customers.")
    print(f"Sampled {len(sampled_customers)} customers with seed {SAMPLE_SEED}.")
    print(f"Sampled customer ids: {sampled_ids}")

    records = generate_customer_campaign_records(sampled_customers, settings)
    flattened = [flatten_customer_campaign(record) for record in records]

    print("Writing customer JSON output...")
    write_json(settings.customer_output_json, records)
    print("Writing customer CSV output...")
    write_csv(settings.customer_output_csv, flattened)

    print(f"Loaded customers: {len(all_customers)}")
    print(f"Sampled customers: {len(sampled_customers)}")
    print(f"Sampled customer ids: {sampled_ids}")
    print(f"JSON output: {settings.customer_output_json}")
    print(f"CSV output: {settings.customer_output_csv}")


if __name__ == "__main__":
    main()
