#!/usr/bin/env bash
# VPS cron wrapper for the metadata-only Hermes handover refresh.
set -euo pipefail

HERMES_HOME_DIR="${HERMES_HOME:-/home/ai-admin/.hermes}"
RUNTIME_ROOT="${HERMES_RUNTIME_ROOT:-${HERMES_HOME_DIR}/hermes-agent}"

exec "${RUNTIME_ROOT}/venv/bin/python" \
  "${HERMES_HOME_DIR}/scripts/refresh_handover_sources.py" \
  --root "${HERMES_HOME_DIR}/knowledge/handover/2026-09-06" \
  --state-file "${HERMES_HOME_DIR}/state/handover-source-refresh.json" \
  --runtime-root "${RUNTIME_ROOT}"
