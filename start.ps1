param([string]$Python = "")
$ErrorActionPreference = "Stop"
$taskRoot = $PSScriptRoot
if (-not $Python) {
    $taskVenv = Join-Path $taskRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $taskVenv) { $Python = $taskVenv }
    else { $Python = (Get-Command python -ErrorAction Stop).Source }
}
Set-Location -LiteralPath (Join-Path $taskRoot 'backend')
& $Python preflight.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python main.py
exit $LASTEXITCODE

