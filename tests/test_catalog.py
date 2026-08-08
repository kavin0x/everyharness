"""Plugin catalog search tests."""

from everyharness.plugin.catalog import get_catalog_entry, search_catalog


def test_search_catalog_finds_builtin_tabular():
    results = search_catalog("tabular")
    assert any(e.name == "tabular" for e in results)


def test_search_catalog_finds_llm():
    results = search_catalog("llm")
    assert any(e.name == "llm" for e in results)


def test_get_catalog_entry_sample():
    entry = get_catalog_entry("everyharness-sample")
    assert entry is not None
    assert entry.kind == "harness"


def test_search_empty_returns_all():
    assert len(search_catalog("")) >= 10
