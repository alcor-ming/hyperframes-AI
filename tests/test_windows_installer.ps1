param([string]$SourceRepo = (Split-Path $PSScriptRoot))
$ErrorActionPreference = "Stop"
$root = Join-Path ([System.IO.Path]::GetTempPath()) ("hf installer " + [char]0x4e2d + [char]0x6587 + " " + [guid]::NewGuid().ToString("N"))
$installHome = Join-Path $root "installed"
$store = Join-Path $root "workstore"

function Assert($Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function New-Package([string]$Id, [bool]$Candidate, [int]$DoctorExit = 0) {
    $package = Join-Path $root $Id
    New-Item -ItemType Directory -Path $package -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $SourceRepo "release.ps1") -Destination $package
    [System.IO.File]::WriteAllText((Join-Path $package "work.cmd"), "@echo off`r`nexit /b $DoctorExit`r`n")
    $files = [ordered]@{}
    foreach ($name in @("release.ps1", "work.cmd")) {
        $files[$name] = (Get-FileHash -LiteralPath (Join-Path $package $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    @{ schema_version = 3; release = $Id; target = "windows-x64"; channel = $(if ($Candidate) { "candidate" } else { "stable" }); files = $files } |
        ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $package ".release.json") -Encoding UTF8
    return $package
}

try {
    foreach ($name in @("active", "parked", "archive")) {
        New-Item -ItemType Directory -Path (Join-Path $store "works\$name") -Force | Out-Null
    }
    $first = New-Package "harness-2026.09.1" $false
    & (Join-Path $first "release.ps1") install -ReleaseRoot $installHome -WorkRoot $store
    $second = New-Package "harness-2026.09.2" $false
    & (Join-Path $second "release.ps1") install -ReleaseRoot $installHome
    $current = @((Get-Item -LiteralPath (Join-Path $installHome "current")).Target)[0]
    Assert ($current -eq (Join-Path $installHome "releases\harness-2026.09.2")) "Stable installation did not select the second release"
    $configBefore = [System.IO.File]::ReadAllText((Join-Path $installHome "config\local.json"))
    $candidate = New-Package "candidate-test" $true
    & (Join-Path $candidate "release.ps1") install-candidate -ReleaseRoot $installHome
    Assert (@((Get-Item -LiteralPath (Join-Path $installHome "current")).Target)[0] -eq $current) "Candidate changed current"
    Assert ([System.IO.File]::ReadAllText((Join-Path $installHome "config\local.json")) -eq $configBefore) "Candidate changed config"
    $extra = Join-Path $candidate "unexpected.txt"
    [System.IO.File]::WriteAllText($extra, "not in the frozen product")
    $rejected = $false
    try { & (Join-Path $candidate "release.ps1") verify } catch { $rejected = $true }
    Assert $rejected "Unmanifested bytes were accepted"
    Remove-Item -LiteralPath $extra
    $failed = New-Package "candidate-failed" $true 7
    $rejected = $false
    try { & (Join-Path $failed "release.ps1") install-candidate -ReleaseRoot $installHome } catch { $rejected = $true }
    Assert $rejected "Runtime failure was accepted"
    Assert (-not (Test-Path -LiteralPath (Join-Path $installHome "candidates\candidate-failed"))) "Partial package was marked installed"
    Assert ([System.IO.File]::ReadAllText((Join-Path $installHome "config\local.json")) -eq $configBefore) "Failed candidate changed config"
    $lock = [System.IO.File]::Open((Join-Path $installHome ".install.lock"), "Open", "ReadWrite", "None")
    try {
        $rejected = $false
        try { & (Join-Path $candidate "release.ps1") workspace -ReleaseRoot $installHome } catch { $rejected = $true }
        Assert $rejected "Concurrent writer was not rejected"
    } finally { $lock.Dispose() }
    & (Join-Path $second "release.ps1") rollback -ReleaseRoot $installHome
    Assert (@((Get-Item -LiteralPath (Join-Path $installHome "current")).Target)[0] -eq (Join-Path $installHome "releases\harness-2026.09.1")) "Rollback did not select previous"
    Add-Content -LiteralPath (Join-Path $installHome "releases\harness-2026.09.2\work.cmd") -Value "rem tampered"
    $rejected = $false
    try { & (Join-Path $second "release.ps1") rollback -ReleaseRoot $installHome } catch { $rejected = $true }
    Assert $rejected "Corrupt rollback was accepted"
    Assert (@((Get-Item -LiteralPath (Join-Path $installHome "current")).Target)[0] -eq (Join-Path $installHome "releases\harness-2026.09.1")) "Failed rollback changed current"
    [System.IO.Directory]::Delete((Join-Path $installHome "previous"))
    New-Item -ItemType Directory -Path (Join-Path $installHome "previous") | Out-Null
    $otherStore = Join-Path $root "another workstore"
    foreach ($name in @("active", "parked", "archive")) {
        New-Item -ItemType Directory -Path (Join-Path $otherStore "works\$name") -Force | Out-Null
    }
    $third = New-Package "harness-2026.09.3" $false
    $rejected = $false
    try { & (Join-Path $third "release.ps1") install -ReleaseRoot $installHome -WorkRoot $otherStore } catch { $rejected = $true }
    Assert $rejected "Real previous directory was replaced"
    Assert ([System.IO.File]::ReadAllText((Join-Path $installHome "config\local.json")) -eq $configBefore) "Failed pointer switch lost the old WorkStore config"
    $errors = $null; $tokens = $null
    [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $installHome "workspace\start.ps1"), [ref]$tokens, [ref]$errors) | Out-Null
    Assert ($errors.Count -eq 0) "Generated workspace launcher is invalid"
    Write-Output "PASS: native installer transactions, channel isolation, lock, rollback and generated launcher (mock runtime)"
} finally {
    # Remove junctions first; never recurse into their targets through a link.
    foreach ($name in @("current", "previous")) {
        $link = Join-Path $installHome $name
        if (Test-Path -LiteralPath $link) { [System.IO.Directory]::Delete($link) }
    }
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
