import importlib.util
import pathlib


MODULE_PATH = pathlib.Path(__file__).parents[2] / "tools" / "vps_runtime_integrity.py"
SPEC = importlib.util.spec_from_file_location("vps_runtime_integrity", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_canonical_digest_is_deterministic():
    value = {"b": 2, "a": [1, True]}
    assert MODULE.digest(value) == MODULE.digest({"a": [1, True], "b": 2})


def test_parse_docker_names_supports_json_and_tabular_rows():
    payload = '\n'.join([
        '{"Names":"/alpha"}',
        '{"Name":"beta"}',
        'gamma\timage\tUp 1 minute',
    ])
    assert MODULE.parse_docker_names(payload) == ["alpha", "beta", "gamma"]


def test_compensation_plan_is_non_automatic():
    plan = MODULE.compensation_plan(["sqlite:current", "qdrant:x"], {"added": ["new"], "removed": []})
    assert {item["trigger"] for item in plan} == {"registry_drift", "qdrant_integrity_failure", "sqlite_integrity_failure"}
    assert all(item["automatic"] == "false" for item in plan)


def test_audit_chain_round_trip(tmp_path):
    path = tmp_path / "audit.jsonl"
    first = MODULE.append_audit(str(path), {"status": "PASS", "n": 1})
    second = MODULE.append_audit(str(path), {"status": "PASS", "n": 2})
    assert first["status"] == second["status"] == "PASS"
    chain = MODULE.verify_audit_chain(str(path))
    assert chain["status"] == "PASS"
    assert chain["events"] == 2
