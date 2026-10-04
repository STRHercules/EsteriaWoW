from __future__ import annotations

from .base import StageContext, StageResult


def _looks_like_local_casc(path) -> bool:
    return path.exists() and (path / "Data").exists() and ((path / ".build.info").exists() or (path / "Data" / "config").exists())


def run_preflight(context: StageContext) -> StageResult:
    errors: list[str] = []
    source = context.project.retail_source
    errors.extend(source.validate())

    if source.mode == "local":
        client = source.local_client_root
        if client is None or not _looks_like_local_casc(client):
            errors.append(
                "local Retail CASC source is not populated or does not look valid: "
                f"{client or '<unset>'} (expected Data/ plus .build.info or Data/config/)"
            )

    errors.extend(context.race.validate())

    for path in (
        context.project.sources_root,
        context.project.retail_sources_root,
        context.project.retail_db2_root,
        context.project.retail_races_root,
        context.project.cache_root,
        context.project.casc_cache_root,
        context.project.workspace_root,
        context.project.extracted_root,
        context.project.converted_root,
        context.project.generated_root,
        context.project.packages_root,
        context.project.state_root,
        context.project.logs_root,
    ):
        path.mkdir(parents=True, exist_ok=True)

    if errors:
        return StageResult("preflight", "blocked", "; ".join(errors))
    if source.mode == "online":
        summary = f"project, race manifest, and online Retail source ({source.product}/{source.region}/{source.locale}) validated"
    else:
        summary = f"project, race manifest, and local Retail CASC source ({source.local_client_root}) validated"
    return StageResult("preflight", "complete", summary)
