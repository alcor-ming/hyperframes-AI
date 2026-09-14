param(
    [Parameter(Position = 0)]
    [ValidateSet("verify", "verify-root", "status", "deploy", "rollback", "recover")]
    [string]$Command = "status",
    [string]$Root,
    [string]$Config
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$arguments = @("-B", (Join-Path $PSScriptRoot ".studio\root_deploy.py"), $Command, "--package", $PSScriptRoot)
if ($Root) { $arguments += @("--root", $Root) }
if ($Config) { $arguments += @("--config", $Config) }
if ($Command -in @("deploy", "rollback", "recover") -and $Root -and
    [System.IO.Path]::GetFullPath($Root).TrimEnd('\') -eq $PSScriptRoot.TrimEnd('\')) {
    throw "Run updates/recovery from an unpacked package outside the deployed root"
}
& (Join-Path $PSScriptRoot "runtime\python\python.exe") @arguments
if ($LASTEXITCODE -ne 0) { throw "Root deployment failed (exit $LASTEXITCODE)" }
