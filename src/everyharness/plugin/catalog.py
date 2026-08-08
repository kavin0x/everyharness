"""Curated plugin catalog (local index for discovery)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogEntry:
    name: str
    pypi_name: str
    kind: str
    summary: str
    tags: tuple[str, ...] = ()


# Curated seed catalog; online index is a later-phase extension point.
CATALOG: tuple[CatalogEntry, ...] = (
    CatalogEntry(
        name="sample-harness",
        pypi_name="everyharness-sample",
        kind="harness",
        summary="Example harness plugin for documentation.",
        tags=("example", "docs"),
    ),
)


def search_catalog(query: str) -> list[CatalogEntry]:
    q = query.strip().lower()
    if not q:
        return list(CATALOG)
    results: list[CatalogEntry] = []
    for entry in CATALOG:
        haystack = " ".join([entry.name, entry.pypi_name, entry.summary, *entry.tags]).lower()
        if q in haystack:
            results.append(entry)
    return results


def get_catalog_entry(name: str) -> CatalogEntry | None:
    key = name.strip().lower()
    for entry in CATALOG:
        if entry.name.lower() == key or entry.pypi_name.lower() == key:
            return entry
    return None
