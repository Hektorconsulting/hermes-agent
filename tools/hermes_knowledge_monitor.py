"""Stable, redacted file-state monitor used by the Hermes hourly refresh job.

The deployed runtime copy is C:\\Hermes\\scripts\\hermes_knowledge_monitor.py.
Keep this repository copy synchronized when the monitor contract changes.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOTS = {
    "hermes": Path(r"C:\Hermes"),
    "hermes_source": Path(r"C:\Hermes\hermes-agent"),
    "platform_reuse": Path(r"C:\Users\Björn\Documents\Codex\repos\platform-reuse-core"),
    "adam": Path(r"C:\Users\Björn\Documents\Codex\repos\ADAM"),
    "codex_home": Path(r"C:\Users\Björn\.codex"),
}
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".next", "dist", "build", "target", "cache", "caches", "tmp", "temp", "logs", "downloads", "state"}
SECRET_NAMES = {".env", ".env.local", ".env.production", "auth.json", "credentials.json"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdbx"}
MAX_FILES_PER_ROOT = 4000
MAX_REPORTED_CHANGES = 40
STATE_FILE = Path(r"C:\Hermes\state\hermes-knowledge-monitor-state.json")


def allowed(path: Path) -> bool:
    return path.name.lower() not in SECRET_NAMES and path.suffix.lower() not in SECRET_SUFFIXES and not any(part.lower() in SKIP_DIRS for part in path.parts)


def scan(root: Path) -> dict:
    files = []
    if not root.exists():
        return {"root": str(root), "status": "missing", "files": []}
    try:
        for path in root.rglob("*"):
            if len(files) >= MAX_FILES_PER_ROOT:
                break
            if not path.is_file() or not allowed(path):
                continue
            try:
                stat = path.stat()
                files.append({"path": str(path), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns})
            except OSError:
                continue
    except OSError:
        return {"root": str(root), "status": "unreadable", "files": []}
    files.sort(key=lambda item: item["path"].lower())
    return {"root": str(root), "status": "ok", "file_count": len(files), "files": files}


def main() -> None:
    try:
        previous = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}
    current = {label: scan(root) for label, root in ROOTS.items()}
    compact = {}
    next_state = {}
    for label, data in current.items():
        now = {item["path"]: {"size": item["size"], "mtime_ns": item["mtime_ns"]} for item in data.get("files", [])}
        before = previous.get(label, {})
        changed = sorted((path for path, meta in now.items() if before.get(path) != meta), key=str.lower)
        removed = sorted((path for path in before if path not in now), key=str.lower)
        compact[label] = {"root": data["root"], "status": data["status"], "file_count": data.get("file_count", 0), "changed_count": len(changed), "removed_count": len(removed), "changed_paths": changed[:MAX_REPORTED_CHANGES], "removed_paths": removed[:MAX_REPORTED_CHANGES], "paths_truncated": len(changed) > MAX_REPORTED_CHANGES or len(removed) > MAX_REPORTED_CHANGES}
        next_state[label] = now
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(next_state, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    temporary.replace(STATE_FILE)
    print(json.dumps({"kind": "hermes_incremental_knowledge_monitor", "version": 1, "redaction": "metadata_only; secret-like files excluded", "roots": compact}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
