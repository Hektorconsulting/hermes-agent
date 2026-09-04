"""Canonical, redacted knowledge bridge for Hermes and OpenClaw.

The bridge augments the existing VPS knowledge database instead of creating a
second store. It provides deterministic preflight and idempotent write-back.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:  # Works both as ``tools.shared_knowledge`` and direct tools/ CLI import.
    from tools.task_envelope import TaskEnvelope
except ModuleNotFoundError:  # pragma: no cover - exercised by direct CLI launch
    from task_envelope import TaskEnvelope

SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]\s*[^\s,;]+")
DEFAULT_DB = "/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db"


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return SECRET_RE.sub(lambda m: f"{m.group(1)}=[REDACTED]", value)
    if isinstance(value, dict):
        return {str(k): redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


class KnowledgeBridge:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path or os.environ.get("HERMES_KNOWLEDGE_DB", DEFAULT_DB))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _connection(self):
        conn = self._connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _migrate(self) -> None:
        with self._connection() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge_sources(
              source_id TEXT PRIMARY KEY, path TEXT NOT NULL, system TEXT NOT NULL,
              namespace TEXT NOT NULL, classification TEXT NOT NULL,
              sha256 TEXT, modified_utc TEXT, status TEXT NOT NULL,
              metadata_json TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS knowledge_sessions(
              session_id TEXT PRIMARY KEY, task_id TEXT, channel TEXT, agent_id TEXT,
              privacy_scope TEXT, archive_text TEXT NOT NULL, content_hash TEXT NOT NULL,
              status TEXT NOT NULL, created_at REAL NOT NULL, updated_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS knowledge_requirements(
              requirement_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, session_id TEXT,
              objective TEXT NOT NULL, namespace TEXT NOT NULL, status TEXT NOT NULL,
              payload_json TEXT NOT NULL, content_hash TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS knowledge_results(
              result_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, session_id TEXT,
              status TEXT NOT NULL, payload_json TEXT NOT NULL, content_hash TEXT NOT NULL,
              created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS knowledge_events(
              event_id TEXT PRIMARY KEY, task_id TEXT, event_type TEXT NOT NULL,
              payload_json TEXT NOT NULL, content_hash TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS knowledge_tasks(
              task_id TEXT PRIMARY KEY, parent_task_id TEXT, session_id TEXT,
              run_id TEXT NOT NULL, requested_by TEXT, assigned_to TEXT,
              channel TEXT, project TEXT, system_scope TEXT NOT NULL,
              privacy_scope TEXT NOT NULL, objective TEXT NOT NULL,
              context_refs_json TEXT NOT NULL, required_tools_json TEXT NOT NULL,
              execution_state TEXT NOT NULL, result_refs_json TEXT NOT NULL,
              provenance_json TEXT NOT NULL, created_at REAL NOT NULL,
              updated_at REAL NOT NULL);
            CREATE INDEX IF NOT EXISTS knowledge_req_task ON knowledge_requirements(task_id);
            CREATE INDEX IF NOT EXISTS knowledge_result_task ON knowledge_results(task_id);
            CREATE INDEX IF NOT EXISTS knowledge_event_task ON knowledge_events(task_id);
            CREATE INDEX IF NOT EXISTS knowledge_task_session ON knowledge_tasks(session_id);
            CREATE INDEX IF NOT EXISTS knowledge_task_state ON knowledge_tasks(execution_state);
            """)
            # Older canonical databases predate result namespaces.  Migrate
            # additively so existing results remain readable as system-scoped
            # history while new preflights cannot cross privacy boundaries.
            try:
                c.execute("ALTER TABLE knowledge_results ADD COLUMN namespace TEXT NOT NULL DEFAULT 'system'")
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
            c.execute("CREATE INDEX IF NOT EXISTS knowledge_result_namespace ON knowledge_results(namespace)")

    @staticmethod
    def _hash(value: Any) -> str:
        raw = json.dumps(redact(value), ensure_ascii=False, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()

    def register_source(self, source: dict[str, Any]) -> dict[str, Any]:
        source = redact(source)
        source_id = str(source.get("source_id") or self._hash(source)[:24])
        with self._connection() as c:
            c.execute("""INSERT INTO knowledge_sources
              (source_id,path,system,namespace,classification,sha256,modified_utc,status,metadata_json,created_at)
              VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source_id) DO UPDATE SET
              path=excluded.path,system=excluded.system,namespace=excluded.namespace,
              classification=excluded.classification,sha256=excluded.sha256,
              modified_utc=excluded.modified_utc,status=excluded.status,metadata_json=excluded.metadata_json""",
              (source_id, source.get("path", ""), source.get("system", "unknown"),
               source.get("namespace", "system"), source.get("classification", "unknown"),
               source.get("sha256"), source.get("modified_utc"), source.get("status", "DISCOVERED"),
               json.dumps(source, ensure_ascii=False), time.time()))
        return {"status": "PASS", "source_id": source_id}

    def _upsert_task(self, envelope: TaskEnvelope, *, now: float | None = None) -> None:
        now = now or time.time()
        data = envelope.to_dict()
        with self._connection() as c:
            c.execute(
                """INSERT INTO knowledge_tasks(
                  task_id,parent_task_id,session_id,run_id,requested_by,assigned_to,
                  channel,project,system_scope,privacy_scope,objective,
                  context_refs_json,required_tools_json,execution_state,result_refs_json,
                  provenance_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(task_id) DO UPDATE SET
                  parent_task_id=excluded.parent_task_id, session_id=excluded.session_id,
                  run_id=excluded.run_id, requested_by=excluded.requested_by,
                  assigned_to=excluded.assigned_to, channel=excluded.channel,
                  project=excluded.project, system_scope=excluded.system_scope,
                  privacy_scope=excluded.privacy_scope, objective=excluded.objective,
                  context_refs_json=excluded.context_refs_json,
                  required_tools_json=excluded.required_tools_json,
                  execution_state=excluded.execution_state,
                  result_refs_json=excluded.result_refs_json,
                  provenance_json=excluded.provenance_json, updated_at=excluded.updated_at""",
                (
                    data["task_id"], data["parent_task_id"], data["session_id"], data["run_id"],
                    data["requested_by"], data["assigned_to"], data["channel"], data["project"],
                    data["system_scope"], data["privacy_scope"], data["objective"],
                    json.dumps(data["context_refs"], ensure_ascii=False),
                    json.dumps(data["required_tools"], ensure_ascii=False), data["execution_state"],
                    json.dumps(data["result_refs"], ensure_ascii=False),
                    json.dumps(redact(data["provenance"]), ensure_ascii=False), now, now,
                ),
            )

    def preflight(self, request: dict[str, Any]) -> dict[str, Any]:
        request = redact(request)
        envelope = TaskEnvelope.from_mapping(request)
        self._upsert_task(envelope)
        query = " ".join(str(request.get(k, "")) for k in ("objective", "project", "system", "requested_scope"))
        terms = [t.lower() for t in re.findall(r"[\w-]{3,}", query)][:8]
        with self._connection() as c:
            reqs = c.execute("SELECT payload_json FROM knowledge_requirements WHERE namespace IN (?, 'global') ORDER BY created_at DESC LIMIT 20", (request.get("privacy_scope", "system"),)).fetchall()
            results = c.execute("SELECT payload_json FROM knowledge_results WHERE namespace IN (?, 'global') ORDER BY created_at DESC LIMIT 10", (request.get("privacy_scope", "system"),)).fetchall()
            sources = c.execute("SELECT source_id,path,system,namespace,status,sha256 FROM knowledge_sources WHERE namespace IN (?, 'global') ORDER BY modified_utc DESC LIMIT 40", (request.get("privacy_scope", "system"),)).fetchall()
            gaps = []
            if terms and "chunks_fts" in {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
                match = " OR ".join(terms)
                gaps = c.execute("SELECT corpus_path, snippet(chunks_fts, 0, '[', ']', '…', 16) FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT 12", (match,)).fetchall()
        return {"status": "PASS", "task_id": envelope.task_id, "session_id": envelope.session_id,
                "run_id": envelope.run_id, "task_envelope": envelope.to_dict(),
                "context_bundle": {"requirements": [json.loads(r[0]) for r in reqs], "recent_results": [json.loads(r[0]) for r in results], "sources": [dict(r) for r in sources], "matches": [dict(r) for r in gaps]},
                "current_state": self.status(),
                "known_requirements": [json.loads(r[0]) for r in reqs],
                "relevant_sources": [dict(r) for r in sources],
                "open_gaps": [],
                "conflicts": [],
                "allowed_tools": list(envelope.required_tools),
                "recommended_next_step": "Use the returned scoped context, then persist the completed result.",
                "privacy_constraints": ["redacted", "namespace_scoped", "historical_sources_are_not_current_truth"]}

    def writeback(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = redact(payload)
        envelope_input = dict(payload.get("task_envelope") or {})
        envelope_input.update({k: v for k, v in payload.items() if k in {
            "task_id", "parent_task_id", "session_id", "run_id", "requested_by",
            "assigned_to", "channel", "project", "system_scope", "privacy_scope",
            "objective", "context_refs", "required_tools", "execution_state",
            "result_refs", "provenance"
        }})
        envelope = TaskEnvelope.from_mapping(envelope_input)
        task_id = envelope.task_id
        session_id = envelope.session_id
        now = time.time()
        archive = payload.get("archive", payload.get("conversation", ""))
        archive_hash = self._hash(archive)
        self._upsert_task(envelope, now=now)
        with self._connection() as c:
            if session_id:
                c.execute("""INSERT INTO knowledge_sessions(
                  session_id,task_id,channel,agent_id,privacy_scope,archive_text,
                  content_hash,status,created_at,updated_at)
                  VALUES(?,?,?,?,?,?,?,?,?,?)
                  ON CONFLICT(session_id) DO UPDATE SET
                    task_id=excluded.task_id, channel=excluded.channel,
                    agent_id=excluded.agent_id, privacy_scope=excluded.privacy_scope,
                    archive_text=excluded.archive_text, content_hash=excluded.content_hash,
                    status=excluded.status, updated_at=excluded.updated_at""",
                    (session_id, task_id, envelope.channel, str(payload.get("agent_id") or envelope.assigned_to), envelope.privacy_scope, json.dumps(archive, ensure_ascii=False), archive_hash, "ARCHIVED", now, now))
            req = payload.get("requirement")
            if req:
                rid = str(req.get("requirement_id") or task_id + ":requirement")
                c.execute("INSERT OR IGNORE INTO knowledge_requirements VALUES(?,?,?,?,?,?,?,?,?)", (rid, task_id, session_id, req.get("objective", payload.get("objective", "")), req.get("namespace", payload.get("privacy_scope", "system")), req.get("status", "draft"), json.dumps(req, ensure_ascii=False), self._hash(req), now))
            result = payload.get("result")
            if result:
                rid = str(result.get("result_id") or task_id + ":result")
                c.execute("INSERT OR IGNORE INTO knowledge_results(result_id,task_id,session_id,namespace,status,payload_json,content_hash,created_at) VALUES(?,?,?,?,?,?,?,?)", (rid, task_id, session_id, result.get("namespace", payload.get("privacy_scope", "system")), result.get("status", "draft"), json.dumps(result, ensure_ascii=False), self._hash(result), now))
                c.execute("UPDATE knowledge_tasks SET execution_state=?, result_refs_json=?, updated_at=? WHERE task_id=?", (str(result.get("status") or "completed"), json.dumps([rid]), now, task_id))
            eid = str(payload.get("event_id") or task_id + ":event:" + self._hash(payload)[:24])
            c.execute("INSERT OR IGNORE INTO knowledge_events VALUES(?,?,?,?,?,?)", (eid, task_id, payload.get("event_type", "writeback"), json.dumps(payload, ensure_ascii=False), self._hash(payload), now))
        return {"status": "PASS", "task_id": task_id, "session_id": session_id, "run_id": envelope.run_id, "archived": bool(session_id), "redacted": True, "event_id": eid}

    def status(self) -> dict[str, Any]:
        with self._connection() as c:
            counts = {}
            for table in ("knowledge_sources", "knowledge_sessions", "knowledge_requirements", "knowledge_results", "knowledge_events", "knowledge_tasks"):
                counts[table] = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return {"status": "PASS", "canonical_db": str(self.db_path), "counts": counts, "redacted": True}
