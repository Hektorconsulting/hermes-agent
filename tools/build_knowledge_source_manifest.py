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
            if not path.is_file() or any(x in {'.git','node_modules','__pycache__'} for x in path.parts): continue
            cls, reason = classify(path)
            stat = path.stat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if cls == 'text' else None
            system = 'rx16' if 'korrigieren' in str(path).lower() else ('hermes' if 'autonomie-ki-orchestrierung' in str(path).lower() or 'hermes' in str(path).lower() else 'openclaw')
            records.append({'source_id': hashlib.sha256(str(path).encode()).hexdigest()[:24], 'path': str(path), 'system': system, 'namespace': 'system', 'classification': cls, 'sha256': digest, 'modified_utc': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(), 'status': 'DISCOVERED' if cls != 'excluded_secret_surface' else 'OUT_OF_SCOPE', 'metadata': {'size_bytes': stat.st_size, 'reason': reason}})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps({'generated_utc': datetime.now(timezone.utc).isoformat(), 'source_count': len(records), 'sources': records}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status':'PASS','source_count':len(records),'output':args.output}, ensure_ascii=False))
    return 0
if __name__ == '__main__': raise SystemExit(main())
