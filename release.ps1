param(
    [Parameter(Position = 0)]
    [ValidateSet("verify", "install", "status", "rollback")]
    [string]$Command = "status",
    [string]$ReleaseRoot = (Join-Path $env:LOCALAPPDATA "HyperFramesAI"),
    [string]$WorkRoot = "D:\AI\AI+hyperframes"
)

$ErrorActionPreference = "Stop"

function Assert-Junction([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        $item = Get-Item -LiteralPath $Path -Force
        if ($item.LinkType -ne "Junction") {
            throw "Refusing to replace a real path: $Path"
        }
    }
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::OpenRead($Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Test-Release([string]$Root) {
    $manifestPath = Join-Path $Root ".release.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Release manifest is missing: $manifestPath"
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.target -ne "windows-x64") {
        throw "Unsupported release target: $($manifest.target)"
    }
    foreach ($entry in $manifest.files.PSObject.Properties) {
        $path = Join-Path $Root ($entry.Name.Replace("/", "\"))
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Release file is missing: $($entry.Name)"
        }
        if ((Get-Sha256 $path) -ne $entry.Value) {
            throw "Release file failed SHA256 verification: $($entry.Name)"
        }
    }
    return $manifest
}

function Set-Current([string]$Root, [string]$Destination) {
    $current = Join-Path $Root "current"
    $previous = Join-Path $Root "previous"
    $candidate = Join-Path $Root ".current-$PID"
    Assert-Junction $current
    Assert-Junction $previous
    if (Test-Path -LiteralPath $candidate) { Remove-Item -LiteralPath $candidate -Force }
    New-Item -ItemType Junction -Path $candidate -Target $Destination | Out-Null
    if (Test-Path -LiteralPath $previous) { Remove-Item -LiteralPath $previous -Force }
    if (Test-Path -LiteralPath $current) { Move-Item -LiteralPath $current -Destination $previous }
    try {
        Move-Item -LiteralPath $candidate -Destination $current
    } catch {
        if (Test-Path -LiteralPath $previous) { Move-Item -LiteralPath $previous -Destination $current }
        throw
    }
}

switch ($Command) {
    "verify" {
        $manifest = Test-Release $PSScriptRoot
        Write-Output $manifest.release
    }
    "install" {
        foreach ($name in @("active", "parked", "archive")) {
            $required = Join-Path $WorkRoot "works\$name"
            if (-not (Test-Path -LiteralPath $required -PathType Container)) {
                throw "Invalid WorkStore; missing: $required"
            }
        }
        $manifest = Test-Release $PSScriptRoot
        $releases = Join-Path $ReleaseRoot "releases"
        $destination = Join-Path $releases $manifest.release
        if (Test-Path -LiteralPath $destination) { throw "Release is already installed: $destination" }
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
        Get-ChildItem -LiteralPath $PSScriptRoot -Force | Copy-Item -Destination $destination -Recurse -Force
        & (Join-Path $destination "work.cmd") root set $WorkRoot
        if ($LASTEXITCODE -ne 0) { throw "WorkStore binding failed with exit code $LASTEXITCODE" }
        Set-Current $ReleaseRoot $destination
        Write-Output $destination
    }
    "rollback" {
        $current = Join-Path $ReleaseRoot "current"
        $previous = Join-Path $ReleaseRoot "previous"
        $swap = Join-Path $ReleaseRoot ".rollback-$PID"
        Assert-Junction $current
        Assert-Junction $previous
        if (-not (Test-Path -LiteralPath $current) -or -not (Test-Path -LiteralPath $previous)) {
            throw "Both current and previous releases are required for rollback"
        }
        Move-Item -LiteralPath $current -Destination $swap
        try {
            Move-Item -LiteralPath $previous -Destination $current
            Move-Item -LiteralPath $swap -Destination $previous
        } catch {
            if ((Test-Path -LiteralPath $current) -and -not (Test-Path -LiteralPath $previous)) {
                Move-Item -LiteralPath $current -Destination $previous
            }
            if (Test-Path -LiteralPath $swap) { Move-Item -LiteralPath $swap -Destination $current }
            throw
        }
        Write-Output (Get-Item -LiteralPath $current).Target
    }
    "status" {
        $result = [ordered]@{}
        foreach ($name in @("current", "previous")) {
            $path = Join-Path $ReleaseRoot $name
            Assert-Junction $path
            $result[$name] = if (Test-Path -LiteralPath $path) { (Get-Item -LiteralPath $path).Target } else { $null }
        }
        $result | ConvertTo-Json
    }
}
