from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any

from src.utils import clamp_rate, normalize_text


REQUIRED_COLUMNS = {
    "segment_name",
    "recency_days",
    "purchase_frequency",
    "avg_order_value",
    "engagement_rate",
    "churn_risk",
    "discount_sensitivity",
    "preferred_category",
    "lifecycle_stage",
}

REQUIRED_CUSTOMER_COLUMNS = {
    "customer_id",
    "recency_days",
    "purchase_frequency",
    "avg_order_value",
}

OPTIONAL_CUSTOMER_COLUMNS = {
    "total_revenue",
    "tenure",
    "repeat_customer",
    "avg_days_between_purchases",
}


def _parse_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "segment_name": normalize_text(row["segment_name"]),
        "recency_days": int(float(row["recency_days"])),
        "purchase_frequency": float(row["purchase_frequency"]),
        "avg_order_value": float(row["avg_order_value"]),
        "engagement_rate": clamp_rate(float(row["engagement_rate"])),
        "churn_risk": normalize_text(row["churn_risk"]).lower(),
        "discount_sensitivity": normalize_text(row["discount_sensitivity"]).lower(),
        "preferred_category": normalize_text(row["preferred_category"]),
        "lifecycle_stage": normalize_text(row["lifecycle_stage"]).lower(),
    }


def load_segments(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {csv_path}")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"Missing required columns in {csv_path}: {missing_str}")

        rows = [_parse_row(row) for row in reader]

    if not rows:
        raise ValueError(f"No segment rows found in {csv_path}")

    return rows


def _parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    text = normalize_text(value)
    if text == "":
        return default
    return float(text)


def _parse_int(value: str | None, default: int = 0) -> int:
    return int(round(_parse_float(value, float(default))))


def _parse_customer_row(row: dict[str, str]) -> dict[str, Any]:
    purchase_frequency = _parse_float(row.get("purchase_frequency"))
    avg_order_value = _parse_float(row.get("avg_order_value"))
    total_revenue = _parse_float(row.get("total_revenue"), purchase_frequency * avg_order_value)
    repeat_customer = _parse_int(row.get("repeat_customer"), 1 if purchase_frequency > 1 else 0)

    return {
        "customer_id": normalize_text(row["customer_id"]),
        "recency_days": _parse_int(row.get("recency_days")),
        "purchase_frequency": purchase_frequency,
        "avg_order_value": avg_order_value,
        "total_revenue": total_revenue,
        "tenure": _parse_int(row.get("tenure")),
        "repeat_customer": repeat_customer,
        "avg_days_between_purchases": _parse_float(row.get("avg_days_between_purchases")),
    }


def load_customer_transactions(
    csv_path: Path,
    sample_size: int = 5,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load customer-level transactional data and return all rows plus a reproducible sample."""
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in {csv_path}")

        missing = REQUIRED_CUSTOMER_COLUMNS.difference(reader.fieldnames)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"Missing required customer columns in {csv_path}: {missing_str}")

        rows = [_parse_customer_row(row) for row in reader]

    if not rows:
        raise ValueError(f"No customer rows found in {csv_path}")

    if len(rows) < sample_size:
        raise ValueError(
            f"Requested sample size {sample_size}, but only {len(rows)} customer rows exist in {csv_path}"
        )

    sampler = random.Random(seed)
    sampled_rows = sampler.sample(rows, sample_size)
    return rows, sampled_rows
