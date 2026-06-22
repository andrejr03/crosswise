"""Simple deterministic normalizers for future matching inputs."""

from __future__ import annotations

import re
import unicodedata
from datetime import date


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value)
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_supplier_name(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"[.,]", "", text)
    text = re.sub(r"\b(ltd|limited|inc|corp|corporation|gmbh|llc)\b", "", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_supplier_aliases(values: list[str]) -> list[str]:
    normalized = [normalize_supplier_name(value) for value in values]
    return sorted({value for value in normalized if value})


def normalize_sku_text(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_currency_code(value: str) -> str:
    return value.strip().upper()


def normalize_date(value: str) -> str:
    return date.fromisoformat(value.strip()).isoformat()
