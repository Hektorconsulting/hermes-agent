import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / "tools" / "source_set_contract.py"
SPEC = importlib.util.spec_from_file_location("source_set_contract", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _items(count=599):
    return [
        {
            "source_id": f"source:{index:04d}",
            "source_ref": f"library://source/{index:04d}",
            "provenance": "owner-selector-test",
            "name": f"Source {index:04d}",
        }
        for index in range(count)
    ]


def _write_selector(path, items):
    path.write_text(
        json.dumps(
            {"schema_version": "owner-selector-v1", "source_set_id": "test-599", "expected_count": 599, "items": items},
            indent=2,
        ),
        encoding="utf-8",
    )


def test_exact_599_selector_is_deterministic_and_metadata_only(tmp_path):
    selector = tmp_path / "selector.json"
    _write_selector(selector, _items())
    first = MODULE.validate(selector)
    second = MODULE.validate(selector)
    assert first["status"] == "PASS"
    assert first["observed_count"] == first["unique_count"] == 599
    assert first["metadata_only_count"] == 599
    assert first["source_ids_sha256"] == second["source_ids_sha256"]
    assert all(item["content_available_on_vps"] is False for item in first["items"])


def test_wrong_count_and_duplicate_id_fail_closed(tmp_path):
    selector = tmp_path / "selector.json"
    items = _items(598)
    items.append(dict(items[0]))
    _write_selector(selector, items)
    result = MODULE.validate(selector)
    assert result["status"] == "FAIL"
    assert any(error.startswith("duplicate_source_ids:") for error in result["errors"])
    assert "item_count:599!=599" not in result["errors"]


def test_missing_provenance_and_reference_are_rejected(tmp_path):
    selector = tmp_path / "selector.json"
    items = _items()
    items[0].pop("source_ref")
    items[0].pop("provenance")
    _write_selector(selector, items)
    result = MODULE.validate(selector)
    assert result["status"] == "FAIL"
    assert "source:0000:missing_reference" in result["errors"]
    assert "source:0000:missing_provenance" in result["errors"]
