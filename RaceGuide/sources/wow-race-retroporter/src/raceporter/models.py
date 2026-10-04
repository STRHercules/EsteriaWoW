from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RetailSourceConfig:
    mode: str
    product: str
    region: str
    locale: str
    build_version: str
    build_key: str
    local_client_root: Path | None
    raw: dict[str, Any] = field(repr=False)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.mode not in {"online", "local"}:
            errors.append("Retail source mode must be online or local")
        if not self.product:
            errors.append("Retail source product is required")
        if not self.region:
            errors.append("Retail source region is required")
        if not self.locale:
            errors.append("Retail source locale is required")
        if self.mode == "local" and self.local_client_root is None:
            errors.append("local_client_root is required when Retail source mode is local")
        return errors


@dataclass(frozen=True)
class ProjectConfig:
    project_root: Path
    retail_source: RetailSourceConfig
    sources_root: Path
    retail_sources_root: Path
    retail_db2_root: Path
    retail_races_root: Path
    cache_root: Path
    casc_cache_root: Path
    workspace_root: Path
    extracted_root: Path
    converted_root: Path
    generated_root: Path
    packages_root: Path
    state_root: Path
    logs_root: Path
    raw: dict[str, Any] = field(repr=False)


@dataclass(frozen=True)
class RaceManifest:
    slug: str
    display_name: str
    retail_race_id: int
    target_race_id: int
    faction: str
    base_race: str
    raw: dict[str, Any] = field(repr=False)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.slug:
            errors.append("slug is required")
        if self.retail_race_id <= 0:
            errors.append("retail_race_id must be greater than zero")
        if not 1 <= self.target_race_id <= 255:
            errors.append("target_race_id must be between 1 and 255")
        if self.faction not in {"alliance", "horde", "neutral"}:
            errors.append("faction must be alliance, horde, or neutral")
        if not self.base_race:
            errors.append("base_race is required")
        return errors
