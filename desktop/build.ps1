param([string]$Python = "", [string]$Output = "")
$ErrorActionPreference = "Stop"
$taskRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $taskRoot '.venv-desktop\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python)) { throw 'Create .venv-desktop and install desktop requirements first. See docs/Windows本地程序使用说明.md.' }
$taskArgs = @('-m', 'desktop.build')
if ($Output) { $taskArgs += @('--output', $Output) }
Set-Location -LiteralPath $taskRoot
& $Python @taskArgs
exit $LASTEXITCODE
