#!/usr/bin/env bash
set -euo pipefail

IPTABLES=/usr/sbin/iptables
IP6TABLES=/usr/sbin/ip6tables

log() {
  logger -t hermes-docker-exposure-guard -- "$*" 2>/dev/null || true
  printf '%s\n' "$*"
}

ensure_chain() {
  local bin="$1"
  "$bin" -w 5 -S DOCKER-USER >/dev/null 2>&1
}

ensure_rule() {
  local bin="$1"
  shift
  if ! "$bin" -w 5 -C DOCKER-USER "$@" >/dev/null 2>&1; then
    "$bin" -w 5 -I DOCKER-USER 1 "$@"
    log "installed $bin DOCKER-USER rule: $*"
  fi
}

if ensure_chain "$IPTABLES"; then
  # The two current NPM Docker networks may reach the OpenClaw gateway.
  # All other IPv4 traffic to the published gateway port is dropped.
  ensure_rule "$IPTABLES" -s 172.18.0.0/16 -p tcp --dport 18789 -j ACCEPT
  ensure_rule "$IPTABLES" -s 172.30.0.0/16 -p tcp --dport 18789 -j ACCEPT
  ensure_rule "$IPTABLES" -p tcp --dport 18789 -j DROP
  ensure_rule "$IPTABLES" -p tcp --dport 8082 -j DROP
  ensure_rule "$IPTABLES" -p tcp --dport 81 -j DROP
else
  log "DOCKER-USER IPv4 chain is not available yet"
fi

if ensure_chain "$IP6TABLES"; then
  # Docker currently publishes the administrative surfaces on IPv6 too.
  # No IPv6 private route is configured, so fail closed for these ports.
  ensure_rule "$IP6TABLES" -p tcp --dport 18789 -j DROP
  ensure_rule "$IP6TABLES" -p tcp --dport 8082 -j DROP
  ensure_rule "$IP6TABLES" -p tcp --dport 81 -j DROP
else
  log "DOCKER-USER IPv6 chain is not available yet"
fi

log "Docker exposure policy reconciled"
