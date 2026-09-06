# Hermes Platform-Reuse-Attestation-Reconciliation

Stand: 2026-09-06

## Befund

Der Platform-Reuse-MCP-Server kann in mehreren unabhängigen Prozessen laufen:

- als direkter Child-Prozess des Hermes-Gateways;
- als isolierter Hermes-One-shot-Prozess;
- als separat gestarteter Codex-MCP-Prozess.

Ein gemeinsamer Attestation-Outputpfad war dadurch nicht ausreichend isoliert.
Ein nicht vom Hermes-Gateway gestarteter Prozess konnte einen redigierten
`UNVERIFIED`-Nachweis in den gemeinsamen Report schreiben, obwohl das echte
Hermes-Child weiterhin korrekt attestiert war.

## Reparatur

Der MCP-Server schreibt einen `UNVERIFIED`-Report nur noch dann in den
Gateway-eigenen Output, wenn der Parent selbst als Hermes-Gateway attestiert
ist. Unattestierte Standalone-Probes dürfen den Gateway-Nachweis nicht
überschreiben.

Zusätzlich verwendet Hermes jetzt eigene, vom allgemeinen Codex-MCP getrennte
Pfade:

```text
C:\Hermes\state\platform-reuse-hermes-gateway-context.json
C:\Hermes\state\platform-reuse-hermes-gateway-attestation.json
```

Der ältere gemeinsame Pfad bleibt als historische Diagnosequelle erhalten,
wird aber nicht mehr als aktueller Hermes-Gateway-Nachweis verwendet.

## Tests und Live-Nachweis

- Attestation-Unittests: `5 tests`, `OK`.
- Hermes-Gateway nach kontrolliertem Reload: aktiv.
- Hermes-Gateway-PID: redigiert im aktuellen Context-File.
- Platform-Reuse-Adapter: direktes Hermes-Gateway-Child.
- `runtime_attestation_status`: `PASS`.
- `runtime_consumer`: `Hermes Gateway`.
- `direct_child`: `true`.
- `external_writes`: `false`.
- `consumer_readback_status`: `HUMAN_GATE_REQUIRED`, weil die vier
  erforderlichen Katalogwerkzeuge noch nicht in derselben echten Gateway-
  Sitzung aufgerufen wurden.

## Restpunkt

Die vier Werkzeuge

```text
platform_reuse_status
search_platform_reuse
platform_reuse_global_control_plane
platform_reuse_readiness
```

müssen noch durch eine echte Hermes-Gateway-Owner-Sitzung aufgerufen werden.
Ein isolierter Codex-MCP-Prozess oder ein One-shot-Subprozess gilt dafür nicht
als Ersatz.

Es wurden keine Secrets, Quelltextkörper, Geschäftsdaten oder externen
Nachrichten in den Nachweis geschrieben.
