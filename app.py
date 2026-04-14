from __future__ import annotations

import json

from src.campaign_generator import generate_campaign
from src.config import get_settings
from src.customer_logic import customer_to_campaign_input
from src.load_data import load_customer_transactions


def main() -> None:
    settings = get_settings()
    _, sampled_customers = load_customer_transactions(settings.customer_input_csv, sample_size=5, seed=42)
    first_customer = sampled_customers[0]
    derived_customer = customer_to_campaign_input(first_customer)
    campaign = generate_campaign(derived_customer, settings)
    payload = {
        "customer_id": first_customer["customer_id"],
        "input_metrics": first_customer,
        "derived_fields": derived_customer,
        "campaign": campaign,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
