#!/usr/bin/env python3
"""Import a manifest produced by build_knowledge_source_manifest.py."""
from __future__ import annotations
import json, sys
from shared_knowledge.bridge import KnowledgeBridge

def main() -> int:
    if len(sys.argv) != 2: raise SystemExit('usage: import_knowledge_source_manifest.py MANIFEST')
    data = json.loads(open(sys.argv[1], encoding='utf-8').read())
    bridge = KnowledgeBridge()
    imported = 0
    for source in data.get('sources', []):
        bridge.register_source(source)
        imported += 1
    print(json.dumps({'status':'PASS','imported':imported,'manifest_source_count':data.get('source_count')}, ensure_ascii=False))
    return 0
if __name__ == '__main__': raise SystemExit(main())
