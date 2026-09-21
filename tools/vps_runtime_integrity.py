#!/usr/bin/env python3
"""Evidence-bounded VPS runtime, audit-chain, and restore verifier.

The verifier is intentionally read-only with respect to runtime services and
data.  The only optional write is an append-only, hash-chained JSONL audit
record when ``--record`` is supplied.  It never prints environment values,
tokens, credentials, cookies, or response bodies.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import shlex
import sqlite3
import subprocess
import sys
from typing import Any


DEFAULT_REGISTRY = "/home/ai-admin/.hermes/state/vps-only-registry.json"
DEFAULT_AUDIT = "/home/ai-admin/.hermes/state/runtime-integrity-audit.jsonl"
DEFAULT_KB = "/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db"
DEFAULT_QDRANT = "http://127.0.0.1:6333"
DEFAULT_MANIFESTS = (
    "/home/ai-admin/knowledge/semantic-index-manifest-20260921.json",
    "/home/ai-admin/knowledge/chunk-semantic-index-manifest-20260921.json",
)
CORE_UNITS = (
    "docker.service",
    "hermes-gateway.service",
    "hermes-whatsapp-bridge.service",
    "ollama.service",
    "openclaw-gateway.service",
)
COLLECTIONS = ("ai_auto_library_metadata_v1", "ai_auto_kb_chunks_v1")
COUNT_TABLES = ("knowledge_sources", "chunks", "chunks_fts", "knowledge_results", "knowledge_events")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
    else:
        raw = canonical(value)
    return hashlib.sha256(raw).hexdigest()


def run(argv: list[str], timeout: int = 20) -> dict[str, Any]:
    """Run a fixed executable without invoking a shell."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except Exception as exc:  # pragma: no cover - platform/runtime dependent
        return {"ok": False, "returncode": None, "error": type(exc).__name__}
    return {"ok": p.returncode == 0, "returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}


def read_json(path: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    p = pathlib.Path(path)
    if not p.is_file():
        return None, {"status": "FAIL", "reason": "missing", "path": path}
    try:
        raw = p.read_bytes()
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("top-level JSON is not an object")
        return value, {"status": "PASS", "path": path, "sha256": digest(raw), "bytes": len(raw)}
    except Exception as exc:
        return None, {"status": "FAIL", "reason": type(exc).__name__, "path": path}


def parse_docker_names(stdout: str) -> list[str]:
    names: list[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            name = str(row.get("Names") or row.get("Name") or "").lstrip("/")
        except json.JSONDecodeError:
            name = line.split("\t", 1)[0].strip().lstrip("/")
        if name:
            names.append(name)
    return sorted(set(names))


def registry_container_names(registry: dict[str, Any]) -> list[str]:
    raw = registry.get("containers", {})
    text = raw.get("stdout", "") if isinstance(raw, dict) else ""
    return sorted({line.split("\t", 1)[0].strip().lstrip("/") for line in text.splitlines() if line.strip()})


def sqlite_check(path: str) -> dict[str, Any]:
    p = pathlib.Path(path)
    if not p.is_file():
        return {"status": "FAIL", "path": path, "reason": "missing"}
    try:
        uri = "file:" + str(p).replace("\\", "/") + "?mode=ro"
        with sqlite3.connect(uri, uri=True, timeout=10) as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            counts: dict[str, int | None] = {}
            for table in COUNT_TABLES:
                try:
                    counts[table] = int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                except sqlite3.Error:
                    counts[table] = None
        return {
            "status": "PASS" if integrity == "ok" else "FAIL",
            "path": path,
            "sha256": digest(p.read_bytes()),
            "bytes": p.stat().st_size,
            "integrity": integrity,
            "counts": counts,
        }
    except Exception as exc:
        return {"status": "FAIL", "path": path, "reason": type(exc).__name__}


def file_check(path: str) -> dict[str, Any]:
    p = pathlib.Path(path)
    if p.suffix.lower() in {".sqlite", ".sqlite3", ".db"}:
        return sqlite_check(path)
    if not p.is_file():
        return {"status": "FAIL", "path": path, "reason": "missing"}
    result: dict[str, Any] = {"status": "PASS", "path": path, "bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}
    if p.suffix.lower() == ".json":
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            result.update(status="FAIL", reason=type(exc).__name__)
    return result


def qdrant_collection(base_url: str, collection: str) -> dict[str, Any]:
    response = run(["curl", "--fail", "--silent", "--show-error", "--max-time", "8", f"{base_url.rstrip('/')}/collections/{collection}"], timeout=12)
    if not response["ok"]:
        return {"status": "FAIL", "collection": collection, "reason": "unreachable"}
    try:
        result = json.loads(response["stdout"]).get("result", {})
        vectors = result.get("config", {}).get("params", {}).get("vectors", {})
        return {
            "status": "PASS" if result.get("status") == "green" else "FAIL",
            "collection": collection,
            "qdrant_status": result.get("status"),
            "points_count": result.get("points_count"),
            "vector_size": vectors.get("size"),
        }
    except Exception as exc:
        return {"status": "FAIL", "collection": collection, "reason": type(exc).__name__}


def systemd_check(unit: str) -> dict[str, Any]:
    response = run(["systemctl", "show", unit, "--property=ActiveState,SubState,MainPID", "--no-pager"], timeout=10)
    values: dict[str, str] = {}
    for line in response.get("stdout", "").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return {"status": "PASS" if response["ok"] and values.get("ActiveState") == "active" else "FAIL", "unit": unit, **values}


def last_audit_hash(path: str) -> str:
    p = pathlib.Path(path)
    if not p.is_file():
        return ""
    for line in reversed(p.read_text(encoding="utf-8").splitlines()):
        if line.strip():
            try:
                value = json.loads(line)
                return str(value.get("event_hash", ""))
            except json.JSONDecodeError:
                return ""
    return ""


def verify_audit_chain(path: str) -> dict[str, Any]:
    p = pathlib.Path(path)
    if not p.is_file():
        return {"status": "PASS", "path": path, "events": 0, "last_event_hash": ""}
    previous = ""
    events = 0
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            actual = str(event.pop("event_hash", ""))
            if event.get("previous_event_hash", "") != previous or not actual or digest(event) != actual:
                return {"status": "FAIL", "path": path, "events": events, "reason": "hash_chain_mismatch", "last_event_hash": previous}
            previous = actual
            events += 1
    except Exception as exc:
        return {"status": "FAIL", "path": path, "events": events, "reason": type(exc).__name__, "last_event_hash": previous}
    return {"status": "PASS", "path": path, "events": events, "last_event_hash": previous}


def append_audit(path: str, evidence: dict[str, Any]) -> dict[str, Any]:
    chain = verify_audit_chain(path)
    if chain["status"] != "PASS":
        return {"status": "FAIL", "path": path, "reason": "existing_audit_chain_invalid", "chain": chain}
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema_version": "runtime-integrity-audit-v1",
        "recorded_at_utc": utc_now(),
        "previous_event_hash": last_audit_hash(path),
        "evidence": evidence,
    }
    event["event_hash"] = digest(event)
    with p.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return {"status": "PASS", "path": str(p), "event_hash": event["event_hash"], "previous_event_hash": event["previous_event_hash"], "chain": verify_audit_chain(path)}


def compensation_plan(failures: list[str], drift: dict[str, list[str]]) -> list[dict[str, str]]:
    plan: list[dict[str, str]] = []
    if drift.get("added") or drift.get("removed"):
        plan.append({"trigger": "registry_drift", "action": "refresh_vps_registry_after_review", "automatic": "false"})
    if any(item.startswith("qdrant:") for item in failures):
        plan.append({"trigger": "qdrant_integrity_failure", "action": "rebuild_semantic_index_from_verified_manifest", "automatic": "false"})
    if any(item.startswith("sqlite:") for item in failures):
        plan.append({"trigger": "sqlite_integrity_failure", "action": "restore_only_from_verified_backup_then_retest", "automatic": "false"})
    if any(item.startswith("systemd:") for item in failures):
        plan.append({"trigger": "core_service_failure", "action": "scoped_service_recovery_with_health_gate", "automatic": "false"})
    return plan


def collect(args: argparse.Namespace) -> dict[str, Any]:
    registry, registry_read = read_json(args.registry)
    failures: list[str] = []
    if registry is None:
        failures.append("registry:read")
        registry = {}

    docker = run(["docker", "ps", "--format", "{{json .}}"], timeout=20)
    current_containers = parse_docker_names(docker.get("stdout", "")) if docker["ok"] else []
    expected_containers = registry_container_names(registry)
    drift = {
        "added": sorted(set(current_containers) - set(expected_containers)),
        "removed": sorted(set(expected_containers) - set(current_containers)),
    }
    if not docker["ok"]:
        failures.append("docker:read")
    if drift["added"] or drift["removed"]:
        failures.append("registry:containers")

    units = {unit: systemd_check(unit) for unit in CORE_UNITS}
    failures.extend(f"systemd:{unit}" for unit, result in units.items() if result["status"] != "PASS")

    qdrant = {collection: qdrant_collection(args.qdrant, collection) for collection in COLLECTIONS}
    failures.extend(f"qdrant:{collection}" for collection, result in qdrant.items() if result["status"] != "PASS")

    sqlite_current = sqlite_check(args.knowledge_db)
    if sqlite_current["status"] != "PASS":
        failures.append("sqlite:current")

    manifests = [file_check(path) for path in args.manifest]
    failures.extend(f"manifest:{result['path']}" for result in manifests if result["status"] != "PASS")

    backups = [file_check(path) for path in args.backup]
    failures.extend(f"backup:{result['path']}" for result in backups if result["status"] != "PASS")

    expected_qdrant = {
        "ai_auto_library_metadata_v1": registry.get("semantic_index", {}).get("points_count"),
        "ai_auto_kb_chunks_v1": registry.get("semantic_chunk_index", {}).get("points_count"),
    }
    for collection, expected in expected_qdrant.items():
        actual = qdrant.get(collection, {}).get("points_count")
        if expected is not None and actual != expected:
            failures.append(f"qdrant:{collection}:points")

    completeness = "PARTIAL" if registry.get("semantic_index", {}).get("requested_599_source_set", {}).get("status") == "UNRESOLVED" else "PASS"
    evidence = {
        "schema_version": "runtime-integrity-result-v1",
        "verified_at_utc": utc_now(),
        "host": registry.get("host"),
        "registry": registry_read,
        "docker": {"status": "PASS" if docker["ok"] else "FAIL", "container_count": len(current_containers)},
        "registry_drift": drift,
        "systemd": units,
        "qdrant": qdrant,
        "sqlite_current": sqlite_current,
        "manifests": manifests,
        "restore_verification": backups,
        "failures": sorted(set(failures)),
        "compensation_plan": compensation_plan(failures, drift),
        "integrity_status": "PASS" if not failures else "FAIL",
        "completeness_status": completeness,
    }
    evidence["audit_chain_before"] = verify_audit_chain(args.audit)
    if args.record:
        evidence["audit"] = append_audit(args.audit, evidence)
    else:
        evidence["audit"] = {"status": "NOT_RECORDED", "path": args.audit}
    return evidence


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry", default=DEFAULT_REGISTRY)
    p.add_argument("--audit", default=DEFAULT_AUDIT)
    p.add_argument("--knowledge-db", default=DEFAULT_KB)
    p.add_argument("--qdrant", default=DEFAULT_QDRANT)
    p.add_argument("--manifest", action="append", default=list(DEFAULT_MANIFESTS))
    p.add_argument("--backup", action="append", default=[])
    p.add_argument("--record", action="store_true")
    p.add_argument("--output", choices=("json", "summary"), default="json")
    return p


def main() -> int:
    args = parser().parse_args()
    result = collect(args)
    if args.output == "summary":
        print(f"integrity_status={result['integrity_status']} completeness_status={result['completeness_status']} failures={len(result['failures'])}")
        print(f"audit_status={result['audit']['status']} audit_path={result['audit']['path']}")
    else:
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if result["integrity_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
