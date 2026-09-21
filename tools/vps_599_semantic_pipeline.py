"""Fail-closed orchestration for the explicit 599-source semantic pipeline.

The pipeline validates the owner-supplied selector first.  The existing VPS
semantic indexer is invoked only after the selector has exactly 599 unique
source IDs with references and provenance.  With ``--plan-only`` it prepares
the normalized ledger without touching Qdrant or SQLite; without a valid
selector it never starts the indexer.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from source_set_contract import DEFAULT_EXPECTED_COUNT, validate, write_json
except ImportError:  # pragma: no cover - supports package-style imports in tests
    from tools.source_set_contract import DEFAULT_EXPECTED_COUNT, validate, write_json


SCHEMA_VERSION = "vps-599-semantic-pipeline-v1"


def build_indexer_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(args.semantic_indexer),
        "--ledger",
        str(args.normalized_ledger),
        "--db",
        str(args.db),
        "--qdrant-url",
        args.qdrant_url,
        "--collection",
        args.collection,
        "--model",
        args.model,
        "--manifest",
        str(args.index_manifest),
        "--backup-root",
        str(args.backup_root),
    ]
    return command


def run_pipeline(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    contract = validate(
        args.selector,
        expected_count=args.expected_count,
        content_root=args.content_root,
    )
    pipeline: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "selector": str(args.selector),
        "contract_manifest": str(args.contract_manifest),
        "normalized_ledger": str(args.normalized_ledger),
        "index_manifest": str(args.index_manifest),
        "expected_count": args.expected_count,
        "contract_status": contract["status"],
        "status": "BLOCKED_SELECTOR" if contract["status"] != "PASS" else "READY",
        "indexer": {"status": "NOT_STARTED"},
    }
    write_json(args.contract_manifest, contract)
    if contract["status"] != "PASS":
        pipeline["errors"] = contract["errors"]
        write_json(args.pipeline_manifest, pipeline)
        return 2, pipeline

    write_json(
        args.normalized_ledger,
        {
            "schema_version": "vps-source-set-ledger-v1",
            "source_set_id": contract["source_set_id"],
            "expected_count": contract["expected_count"],
            "items": contract["items"],
        },
    )
    if args.plan_only:
        pipeline["status"] = "READY"
        pipeline["indexer"] = {"status": "PLAN_ONLY", "command_ready": True}
        write_json(args.pipeline_manifest, pipeline)
        return 0, pipeline

    completed = subprocess.run(
        build_indexer_command(args),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    index_status = "PASS" if completed.returncode == 0 else "FAIL"
    pipeline["status"] = index_status
    pipeline["indexer"] = {
        "status": index_status,
        "exit_code": completed.returncode,
        "manifest": str(args.index_manifest),
    }
    if completed.stderr.strip():
        pipeline["indexer"]["stderr_present"] = True
    write_json(args.pipeline_manifest, pipeline)
    return completed.returncode, pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector", type=Path, required=True)
    parser.add_argument("--contract-manifest", type=Path, required=True)
    parser.add_argument("--normalized-ledger", type=Path, required=True)
    parser.add_argument("--pipeline-manifest", type=Path, required=True)
    parser.add_argument("--index-manifest", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--backup-root", type=Path, required=True)
    parser.add_argument("--semantic-indexer", type=Path, required=True)
    parser.add_argument("--content-root", type=Path)
    parser.add_argument("--qdrant-url", default="http://127.0.0.1:6333")
    parser.add_argument("--collection", default="ai_auto_library_metadata_v1")
    parser.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    parser.add_argument("--expected-count", type=int, default=DEFAULT_EXPECTED_COUNT)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)
    if args.expected_count <= 0:
        raise SystemExit("expected-count must be positive")
    code, result = run_pipeline(args)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
