from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5")
    input_csv: Path = INPUT_DIR / "customer_segments.csv"
    output_json: Path = OUTPUT_DIR / "generated_campaigns.json"
    output_csv: Path = OUTPUT_DIR / "generated_campaigns.csv"
    customer_input_csv: Path = INPUT_DIR / "customer_transactional_data.csv"
    customer_output_json: Path = OUTPUT_DIR / "generated_customer_campaigns.json"
    customer_output_csv: Path = OUTPUT_DIR / "generated_customer_campaigns.csv"


def get_settings() -> Settings:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()
