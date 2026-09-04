#!/usr/bin/env python3
"""Build a redacted provenance manifest for operational knowledge sources."""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

SECRET_PARTS = {'.env', '.envrc', 'credentials', 'secrets', 'private_key', 'token'}
TEXT_SUFFIXES = {'.md','.txt','.json','.jsonl','.csv','.yaml','.yml','.toml','.xml','.py','.ps1','.sh','.sql','.ts','.tsx','.js','.jsx','.log'}

def classify(path: Path) -> tuple[str, str]:
    low = str(path).lower()
    if any(part in low for part in SECRET_PARTS): return 'excluded_secret_surface', 'secret-like path'
    if path.suffix.lower() in TEXT_SUFFIXES: return 'text', 'eligible for full parser read'
    return 'binary_or_unknown', 'metadata only'

def infer_system(path: Path, root: Path) -> str:
    value = str(path).lower()
    if 'platform-reuse-core' in value: return 'platform-reuse'
    if 'openclaw' in value: return 'openclaw'
    if 'rx16' in value or 'korrigieren' in value: return 'rx16'
    if 'adam' in value: return 'adam'
    if 'hermes' in value: return 'hermes'
    return 'unknown'

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', action='append', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    records = []
    for root_text in args.root:
        root = Path(root_text)
        if not root.exists():
            records.append({'path': str(root), 'system': 'unknown', 'status': 'MISSING_REFERENCED'})
            continue
        for path in root.rglob('*'):
            if not path.is_file() or any(x.lower() in {'.git','node_modules','__pycache__','venv','.venv','dist','build','cache','tmp','backups'} for x in path.parts): continue
            cls, reason = classify(path)
            stat = path.stat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if cls == 'text' else None
            system = infer_system(path, root)
            records.append({'source_id': hashlib.sha256(str(path).encode()).hexdigest()[:24], 'path': str(path), 'system': system, 'namespace': 'system', 'classification': cls, 'sha256': digest, 'modified_utc': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(), 'status': 'DISCOVERED' if cls != 'excluded_secret_surface' else 'OUT_OF_SCOPE', 'metadata': {'size_bytes': stat.st_size, 'reason': reason, 'read_status': 'metadata_only' if cls != 'text' else 'readable', 'provenance': 'filesystem_manifest', 'conflict_status': 'unclassified'}})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps({'generated_utc': datetime.now(timezone.utc).isoformat(), 'source_count': len(records), 'sources': records}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status':'PASS','source_count':len(records),'output':args.output}, ensure_ascii=False))
    return 0
if __name__ == '__main__': raise SystemExit(main())
