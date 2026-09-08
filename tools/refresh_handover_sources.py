#!/usr/bin/env python3
"""Incrementally register a redacted Hermes handover mirror.

The tool is intentionally model-free.  It only records filename, stable source
identity, digest, timestamp, and classification in the shared-knowledge bridge.
Document bodies and secret values never enter its output or SQLite payloads.

It is suitable for a Hermes ``cron --no-agent`` job: unchanged runs write the
state file but emit no stdout, so they stay silent for the owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SOURCE_SUFFIXES = {".md", ".json"}
STATE_VERSION = 1


def _utc_iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def _stable_source_id(path: Path) -> str:
    normalized = str(path).replace("\\", "/").lower().encode("utf-8")
    return "handover-" + hashlib.sha256(normalized).hexdigest()[:24]


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": STATE_VERSION, "sources": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {"version": STATE_VERSION, "sources": {}}
    return value if isinstance(value, dict) else {"version": STATE_VERSION, "sources": {}}


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _bridge(runtime_root: Path):
    tools_dir = runtime_root / "tools"
    if not tools_dir.is_dir():
        raise RuntimeError(f"Hermes tools directory missing: {tools_dir}")
    sys.path.insert(0, str(tools_dir))
    from shared_knowledge.bridge import KnowledgeBridge  # type: ignore

    return KnowledgeBridge()


def _iter_documents(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.iterdir()
            if path.is_file()
            and path.suffix.lower() in SOURCE_SUFFIXES
            and path.name != "HERMES_VPS_HANDOVER_SOURCE_MANIFEST.json"
        ),
        key=lambda path: path.name.lower(),
    )


def run(root: Path, state_file: Path, runtime_root: Path, register: bool) -> dict[str, Any]:
    if not root.is_dir():
        raise RuntimeError(f"Handover root missing: {root}")

    previous = _load_state(state_file)
    previous_sources = previous.get("sources") if isinstance(previous.get("sources"), dict) else {}
    current_sources: dict[str, dict[str, Any]] = {}
    changed: list[str] = []
    bridge = _bridge(runtime_root) if register else None

    for document in _iter_documents(root):
        stat = document.stat()
        digest = _digest(document)
        name = document.name
        current_sources[name] = {"sha256": digest, "modified_utc": _utc_iso(stat.st_mtime)}
        if previous_sources.get(name, {}).get("sha256") != digest:
            changed.append(name)
        if bridge is not None:
            bridge.register_source(
                {
                    "source_id": _stable_source_id(document),
                    "path": str(document),
                    "system": "hermes",
                    "namespace": "system",
                    "classification": "READ_ALLOWED",
                    "sha256": digest,
                    "modified_utc": _utc_iso(stat.st_mtime),
                    "status": "VERIFIED",
                    "metadata": {
                        "redacted": True,
                        "handover_set": root.name,
                        "content_ingested": False,
                        "refresh": "metadata-only",
                    },
                }
            )

    missing = sorted(set(previous_sources) - set(current_sources))
    if bridge is not None:
        for name in missing:
            former = previous_sources.get(name, {})
            bridge.register_source(
                {
                    "source_id": "handover-" + hashlib.sha256(
                        str(root / name).replace("\\", "/").lower().encode("utf-8")
                    ).hexdigest()[:24],
                    "path": str(root / name),
                    "system": "hermes",
                    "namespace": "system",
                    "classification": "READ_ALLOWED",
                    "sha256": former.get("sha256"),
                    "modified_utc": _utc_iso(datetime.now(UTC).timestamp()),
                    "status": "MISSING",
                    "metadata": {"redacted": True, "handover_set": root.name, "refresh": "metadata-only"},
                }
            )

    _atomic_json_write(
        state_file,
        {
            "version": STATE_VERSION,
            "root": str(root),
            "refreshed_utc": _utc_iso(datetime.now(UTC).timestamp()),
            "sources": current_sources,
        },
    )
    return {
        "status": "PASS",
        "root": str(root),
        "source_count": len(current_sources),
        "changed": sorted(changed),
        "missing": missing,
        "registered": register,
        "redacted": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Mirrored redacted handover directory")
    parser.add_argument("--state-file", type=Path, required=True, help="Private metadata-only state file")
    parser.add_argument("--runtime-root", type=Path, required=True, help="Active Hermes source/runtime root")
    parser.add_argument("--no-register", action="store_true", help="Hash and persist state without SQLite writes")
    parser.add_argument("--always-report", action="store_true", help="Emit JSON even when no source changed")
    args = parser.parse_args()
    try:
        result = run(args.root, args.state_file, args.runtime_root, register=not args.no_register)
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc), "redacted": True}, ensure_ascii=False))
        return 1
    if args.always_report or result["changed"] or result["missing"]:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
