[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SkillPath
)

$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$validator = 'C:\Users\Björn\.codex\skills\.system\skill-creator\scripts\quick_validate.py'

if (-not (Test-Path -LiteralPath $python)) {
    throw "Hermes project environment is missing: $python. Run 'uv sync --locked' from $projectRoot first. Do not use the portable Codex runtime for skill validation."
}
if (-not (Test-Path -LiteralPath $validator)) {
    throw "Codex skill validator was not found: $validator"
}

& $python -c 'import yaml; assert yaml.__version__ == "6.0.3"'
if ($LASTEXITCODE -ne 0) {
    throw 'Hermes project environment does not provide the pinned PyYAML dependency.'
}

& $python $validator (Resolve-Path -LiteralPath $SkillPath).Path
if ($LASTEXITCODE -ne 0) {
    throw "Skill validation failed for $SkillPath"
}
