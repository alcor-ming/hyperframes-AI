$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$python = Join-Path $PSScriptRoot "runtime\python\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Bundled Python runtime is missing: $python"
}
& $python -B (Join-Path $PSScriptRoot ".studio\windows_runtime.py") @args
exit $LASTEXITCODE
