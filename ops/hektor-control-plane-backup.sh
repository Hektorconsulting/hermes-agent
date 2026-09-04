#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/home/ai-admin/backups}"
STAMP="$(date +%Y%m%d-%H%M%S)"
WORKDIR="$(mktemp -d /tmp/hektor-backup.XXXXXX)"
OUT="$BACKUP_DIR/hektor-control-plane-$STAMP.tar.gz"

cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

echo "Starting Hektor backup: $STAMP"

mkdir -p "$WORKDIR/configs" "$WORKDIR/dumps" "$WORKDIR/metadata"

cp /home/ai-admin/docker/npm/data/database.sqlite "$WORKDIR/npm-database.sqlite"
cp -a /home/ai-admin/hermes-data "$WORKDIR/hermes-data" 2>/dev/null || true
cp -a /home/ai-admin/infrastructure/hermes-ui "$WORKDIR/configs/hermes-ui"
cp -a /home/ai-admin/docker/npm/data/nginx "$WORKDIR/configs/npm-nginx"
cp -a /home/ai-admin/docker/npm/letsencrypt/live/hermes-openclaw "$WORKDIR/configs/hermes-openclaw-cert" 2>/dev/null || true
cp -a /home/ai-admin/docs "$WORKDIR/configs/docs" 2>/dev/null || true
cp -a /home/ai-admin/scripts "$WORKDIR/configs/scripts" 2>/dev/null || true
cp -a /home/ai-admin/knowledge/claude_codex_hermes_knowledge.db "$WORKDIR/shared-kb.sqlite3" 2>/dev/null || true

timeout 10s docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" > "$WORKDIR/metadata/docker-ps.txt" || true
timeout 10s docker network ls > "$WORKDIR/metadata/docker-networks.txt" || true
timeout 20s docker exec nginx-proxy-manager nginx -T > "$WORKDIR/metadata/nginx-rendered.conf" 2>/dev/null || true

if timeout 30s docker exec n8n-postgres pg_dumpall -U n8n > "$WORKDIR/dumps/n8n-postgres-pg-dumpall.sql" 2>"$WORKDIR/dumps/n8n-postgres.err"; then
  echo "Postgres dump captured"
else
  echo "Postgres dump failed; see dumps/n8n-postgres.err"
fi

vault_token_file=/home/ai-admin/.vault/root.token
if [ -r "$vault_token_file" ] && cat "$vault_token_file" | timeout 30s docker exec -i vault sh -c 'IFS= read -r VAULT_TOKEN; export VAULT_TOKEN; vault operator raft snapshot save /tmp/vault-snapshot.snap' > /dev/null 2>"$WORKDIR/dumps/vault-snapshot.err"; then
  docker cp vault:/tmp/vault-snapshot.snap "$WORKDIR/dumps/vault-snapshot.snap"
  docker exec vault rm -f /tmp/vault-snapshot.snap >/dev/null 2>&1 || true
  echo "Vault raft snapshot captured"
else
  echo "Vault raft snapshot skipped or failed; see dumps/vault-snapshot.err"
fi

tar -czf "$OUT" -C "$WORKDIR" .
chmod 600 "$OUT"

find "$BACKUP_DIR" -maxdepth 1 -name 'hektor-control-plane-*.tar.gz' -type f -printf '%T@ %p\n' \
  | sort -nr | awk 'NR>7 {print $2}' | xargs -r rm -f

echo "Backup complete: $OUT"
