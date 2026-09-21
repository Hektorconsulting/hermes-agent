"""Validate and normalize an explicitly supplied semantic source set.

The 599-source requirement is intentionally fail-closed.  This tool never
guesses a subset from a larger registry and never reads source bodies.  It
only validates the owner-supplied selector metadata, records deterministic
provenance, and emits a ledger that the existing VPS semantic indexer can
consume once the source payloads are available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "vps-source-set-contract-v1"
DEFAULT_EXPECTED_COUNT = 599
REFERENCE_FIELDS = ("source_ref", "path", "uri", "url")
PROVENANCE_FIELDS = ("provenance", "source", "authority")
SAFE_ITEM_FIELDS = {
    "source_id",
    "source_ref",
    "path",
    "uri",
    "url",
    "name",
    "project_id",
    "classification",
    "mime_type",
    "reason",
    "authority",
    "source",
    "provenance",
    "sha256",
    "version",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_selector(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"schema_version": "unversioned"}, payload
    if not isinstance(payload, dict):
        raise ValueError("selector must be a JSON object or array")
    items = payload.get("items", payload.get("sources"))
    if not isinstance(items, list):
        raise ValueError("selector must contain an items or sources list")
    return payload, items


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _content_available(reference: str, content_root: Path | None) -> bool:
    if not reference or content_root is None:
        return False
    if reference.startswith(("http://", "https://", "s3://", "gs://")):
        return False
    path = Path(reference)
    if not path.is_absolute():
        path = content_root / path
    # Existence only: this contract deliberately never reads source bodies.
    return path.is_file()


def validate(
    selector_path: Path,
    *,
    expected_count: int = DEFAULT_EXPECTED_COUNT,
    content_root: Path | None = None,
) -> dict[str, Any]:
    metadata, raw_items = load_selector(selector_path)
    errors: list[str] = []
    source_set_id = _text(metadata.get("source_set_id"))
    if not source_set_id:
        errors.append("missing:source_set_id")

    declared_count = metadata.get("expected_count", expected_count)
    if declared_count != expected_count:
        errors.append(f"declared_expected_count:{declared_count}!={expected_count}")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            errors.append(f"item_{index}:not_object")
            continue
        # Keep the emitted manifest bounded to provenance/index metadata.  Do
        # not copy arbitrary selector fields (which could contain credentials,
        # cookies, or unrelated source-body material).
        item = {key: raw[key] for key in SAFE_ITEM_FIELDS if key in raw}
        source_id = _text(item.get("source_id"))
        if not source_id:
            errors.append(f"item_{index}:missing_source_id")
            continue
        if source_id in seen:
            duplicate_ids.add(source_id)
        seen.add(source_id)
        reference = next((_text(item.get(field)) for field in REFERENCE_FIELDS if _text(item.get(field))), "")
        provenance = next((_text(item.get(field)) for field in PROVENANCE_FIELDS if _text(item.get(field))), "")
        if not reference:
            errors.append(f"{source_id}:missing_reference")
        if not provenance:
            errors.append(f"{source_id}:missing_provenance")
        item["source_id"] = source_id
        item["source_ref"] = reference
        item["provenance"] = provenance
        item["content_available_on_vps"] = _content_available(reference, content_root)
        normalized.append(item)

    if len(raw_items) != expected_count:
        errors.append(f"item_count:{len(raw_items)}!={expected_count}")
    if duplicate_ids:
        errors.append("duplicate_source_ids:" + ",".join(sorted(duplicate_ids)))

    normalized.sort(key=lambda row: row["source_id"])
    ids = [row["source_id"] for row in normalized]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_now(),
        "selector": str(selector_path),
        "selector_sha256": sha256_file(selector_path),
        "source_set_id": source_set_id or None,
        "expected_count": expected_count,
        "observed_count": len(raw_items),
        "unique_count": len(set(ids)),
        "source_ids_sha256": digest(ids),
        "content_available_on_vps": sum(1 for row in normalized if row["content_available_on_vps"]),
        "metadata_only_count": sum(1 for row in normalized if not row["content_available_on_vps"]),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "items": normalized,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--normalized-ledger", type=Path)
    parser.add_argument("--content-root", type=Path)
    parser.add_argument("--expected-count", type=int, default=DEFAULT_EXPECTED_COUNT)
    args = parser.parse_args(argv)
    if args.expected_count <= 0:
        raise SystemExit("expected-count must be positive")

    try:
        result = validate(
            args.selector,
            expected_count=args.expected_count,
            content_root=args.content_root,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "selector": str(args.selector),
            "status": "FAIL",
            "errors": [f"{type(exc).__name__}:{exc}"],
        }
    write_json(args.manifest, result)
    if args.normalized_ledger and result.get("status") == "PASS":
        write_json(
            args.normalized_ledger,
            {
                "schema_version": "vps-source-set-ledger-v1",
                "source_set_id": result["source_set_id"],
                "expected_count": result["expected_count"],
                "items": result["items"],
            },
        )
    print(json.dumps({key: value for key, value in result.items() if key != "items"}, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
