<#!
.SYNOPSIS
Maintains the private Windows-to-VPS Ollama SSH forward used by Hermes.

.DESCRIPTION
Runs only a loopback listener at 127.0.0.1:11435 and forwards it through the
existing `hostinger-vps` SSH alias to VPS loopback 127.0.0.1:11434. It never
opens Ollama publicly. The deployment copy is
C:\Hermes\ops\Start-HermesVpsOllamaTunnel.ps1; keep that scheduled-task
entry synchronized from this source-controlled implementation.
#>

$ErrorActionPreference = 'Stop'
$listenPort = 11435
$logPath = 'C:\Hermes\logs\vps-ollama-tunnel.log'
$ssh = (Get-Command ssh.exe -ErrorAction Stop).Source

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null
$existing = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $listenPort -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) tunnel already listening on $listenPort"
    exit 0
}

$arguments = @(
    '-N', '-T',
    '-o', 'BatchMode=yes',
    '-o', 'ExitOnForwardFailure=yes',
    '-o', 'ServerAliveInterval=30',
    '-o', 'ServerAliveCountMax=3',
    '-o', 'ConnectTimeout=8',
    '-L', '11435:127.0.0.1:11434',
    'hostinger-vps'
)

$delaySeconds = 5
$maximumDelaySeconds = 60
while ($true) {
    Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) starting private Ollama tunnel"
    try {
        & $ssh @arguments 2>&1 | ForEach-Object {
            Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) $_"
        }
        Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) tunnel exited with code $LASTEXITCODE; retrying in $delaySeconds seconds"
    }
    catch {
        Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) tunnel error: $($_.Exception.Message); retrying in $delaySeconds seconds"
    }

    if (Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $listenPort -State Listen -ErrorAction SilentlyContinue) {
        Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) listener restored by another trusted process; stopping wrapper"
        exit 0
    }

    Start-Sleep -Seconds $delaySeconds
    $delaySeconds = [Math]::Min($maximumDelaySeconds, $delaySeconds * 2)
}
