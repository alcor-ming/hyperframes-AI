param(
    [string]$SourceRepo = (Split-Path $PSScriptRoot),
    [Parameter(Mandatory = $true)][string]$Python
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
& $Python -B -m unittest discover -s (Join-Path $SourceRepo "tests") -p "test_root_deploy.py" -v
if ($LASTEXITCODE -ne 0) { throw "Native root installer checks failed" }
Write-Output "PASS: native Python managed-root transactions (fixture packages, not production acceptance)"
