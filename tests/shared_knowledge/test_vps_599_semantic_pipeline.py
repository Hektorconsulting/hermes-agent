import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "tools" / "vps_599_semantic_pipeline.py"
SPEC = importlib.util.spec_from_file_location("vps_599_semantic_pipeline", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _selector(path, count=599):
    items = [
        {
            "source_id": f"source:{index:04d}",
            "source_ref": f"library://source/{index:04d}",
            "provenance": "synthetic-pipeline-test",
        }
        for index in range(count)
    ]
    path.write_text(
        json.dumps({"source_set_id": "pipeline-test", "expected_count": 599, "items": items}),
        encoding="utf-8",
    )


def _args(tmp_path, selector):
    return [
        "--selector", str(selector),
        "--contract-manifest", str(tmp_path / "contract.json"),
        "--normalized-ledger", str(tmp_path / "ledger.json"),
        "--pipeline-manifest", str(tmp_path / "pipeline.json"),
        "--index-manifest", str(tmp_path / "index.json"),
        "--db", str(tmp_path / "knowledge.db"),
        "--backup-root", str(tmp_path / "backups"),
        "--semantic-indexer", str(tmp_path / "indexer.py"),
        "--plan-only",
    ]


def test_plan_only_requires_and_prepares_exact_599(tmp_path):
    selector = tmp_path / "selector.json"
    _selector(selector)
    assert MODULE.main(_args(tmp_path, selector)) == 0
    contract = json.loads((tmp_path / "contract.json").read_text(encoding="utf-8"))
    ledger = json.loads((tmp_path / "ledger.json").read_text(encoding="utf-8"))
    pipeline = json.loads((tmp_path / "pipeline.json").read_text(encoding="utf-8"))
    assert contract["status"] == "PASS"
    assert len(ledger["items"]) == 599
    assert pipeline["status"] == "READY"
    assert pipeline["indexer"]["status"] == "PLAN_ONLY"


def test_invalid_selector_blocks_indexer_and_writes_no_ledger(tmp_path):
    selector = tmp_path / "selector.json"
    _selector(selector, count=598)
    assert MODULE.main(_args(tmp_path, selector)) == 2
    pipeline = json.loads((tmp_path / "pipeline.json").read_text(encoding="utf-8"))
    assert pipeline["status"] == "BLOCKED_SELECTOR"
    assert pipeline["indexer"]["status"] == "NOT_STARTED"
    assert not (tmp_path / "ledger.json").exists()
