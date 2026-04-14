from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def normalize_text(value: str) -> str:
    return " ".join(str(value).strip().split())


def clamp_rate(value: float) -> float:
    return max(0.0, min(1.0, value))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def tier_from_numeric(value: float, low_cutoff: float, high_cutoff: float) -> str:
    if value <= low_cutoff:
        return "low"
    if value >= high_cutoff:
        return "high"
    return "medium"
