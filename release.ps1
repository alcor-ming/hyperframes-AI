param(
    [Parameter(Position = 0)]
    [ValidateSet("verify", "install", "install-candidate", "workspace", "status", "rollback")]
    [string]$Command = "status",
    [string]$ReleaseRoot = (Join-Path $env:LOCALAPPDATA "HyperFramesAI"),
    [string]$WorkRoot,
    [string]$CheckWork,
    [string]$Variant = "main"
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
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.target -ne "windows-x64") {
        throw "Unsupported release target: $($manifest.target)"
    }
    if ($manifest.release -notmatch '^(harness-[0-9]{4}\.[0-9]{2}\.[0-9]+|candidate-[a-zA-Z0-9][a-zA-Z0-9._-]*)$') {
        throw "Invalid installation ID"
    }
    foreach ($entry in $manifest.files.PSObject.Properties) {
        if ([System.IO.Path]::IsPathRooted($entry.Name) -or $entry.Name -match '(^|[/\\])\.\.([/\\]|$)' -or $entry.Name.Contains(':')) {
            throw "Unsafe release file path: $($entry.Name)"
        }
        $path = Join-Path $Root ($entry.Name.Replace("/", "\"))
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Release file is missing: $($entry.Name)"
        }
        if ((Get-Sha256 $path) -ne $entry.Value) {
            throw "Release file failed SHA256 verification: $($entry.Name)"
        }
    }
    if ($manifest.schema_version -ge 3) {
        $allowed = @{}
        foreach ($entry in $manifest.files.PSObject.Properties) { $allowed[$entry.Name.Replace("/", "\")] = $true }
        $allowed[".release.json"] = $true
        foreach ($item in Get-ChildItem -LiteralPath $Root -Force -Recurse) {
            if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw "Links are not allowed inside an immutable package: $($item.FullName)" }
            $relative = $item.FullName.Substring($Root.TrimEnd('\').Length + 1)
            if (-not $item.PSIsContainer -and -not $allowed.ContainsKey($relative)) { throw "Unmanifested package file: $relative" }
        }
    }
    return $manifest
}

function Get-LocalConfig {
    $configPath = Join-Path $ReleaseRoot "config\local.json"
    $config = if (Test-Path -LiteralPath $configPath) { Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json } else { [PSCustomObject]@{} }
    if (-not $WorkRoot) {
        $WorkRoot = $config.work_root
        if (-not $WorkRoot) {
            $legacy = Join-Path $ReleaseRoot "current\.studio\.runtime\work-root"
            if (Test-Path -LiteralPath $legacy) { $WorkRoot = (Get-Content -LiteralPath $legacy -Raw -Encoding UTF8).Trim() }
        }
    }
    if (-not $WorkRoot) { throw "First installation requires -WorkRoot <existing WorkStore>" }
    foreach ($name in @("active", "parked", "archive")) {
        if (-not (Test-Path -LiteralPath (Join-Path $WorkRoot "works\$name") -PathType Container)) {
            throw "Invalid WorkStore; missing works\$name"
        }
    }
    $config | Add-Member -NotePropertyName work_root -NotePropertyValue ([System.IO.Path]::GetFullPath($WorkRoot)) -Force
    return $config
}

function Save-LocalConfig($Config) {
    $configPath = Join-Path $ReleaseRoot "config\local.json"
    New-Item -ItemType Directory -Path (Split-Path $configPath) -Force | Out-Null
    $temporary = "$configPath.$PID.tmp"
    [System.IO.File]::WriteAllText($temporary, ($Config | ConvertTo-Json -Depth 20), (New-Object System.Text.UTF8Encoding $false))
    if (Test-Path -LiteralPath $configPath) {
        $backup = "$temporary.backup"
        [System.IO.File]::Replace($temporary, $configPath, $backup)
        Remove-Item -LiteralPath $backup -Force
    } else {
        [System.IO.File]::Move($temporary, $configPath)
    }
}

function Test-NativeRuntime([string]$Root, $Config, [bool]$CheckCompatibility) {
    $env:HYPERFRAMES_AI_HOME = $ReleaseRoot
    $env:HYPERFRAMES_AI_WORK_ROOT = $Config.work_root
    Remove-Item Env:\HYPERFRAMES_AI_SESSION -ErrorAction SilentlyContinue
    & (Join-Path $Root "work.cmd") doctor
    if ($LASTEXITCODE -ne 0) { throw "Native runtime check failed; current was not changed" }
    if ($CheckCompatibility -and $CheckWork) {
        $env:HYPERFRAMES_AI_ROOT = $Root
        $env:HYPERFRAMES_AI_CONFIG = Join-Path $ReleaseRoot "config\local.json"
        $env:HYPERFRAMES_AI_WORK_ROOT = $Config.work_root
        $env:HYPERFRAMES_AI_REVIEW = "0"
        & (Join-Path $Root "runtime\python\python.exe") -B (Join-Path $Root ".studio\work.py") --work $CheckWork --variant $Variant status
        if ($LASTEXITCODE -ne 0) { throw "Work read compatibility failed; current was not changed" }
    } elseif ($CheckCompatibility) {
        Write-Warning "Work/Variant read compatibility is unverified; use -CheckWork <id> -Variant <id>"
    }
}

function Set-Workspace {
    $workspace = Join-Path $ReleaseRoot "workspace"
    New-Item -ItemType Directory -Path $workspace -Force | Out-Null
    $launcher = @'
param([string]$Candidate, [string]$ReviewRoot)
$ErrorActionPreference = "Stop"
$installHome = Split-Path $PSScriptRoot
if ($Candidate) {
    if ($Candidate -notmatch '^candidate-[a-zA-Z0-9][a-zA-Z0-9._-]*$') { throw "Invalid candidate ID" }
    $selected = Join-Path $installHome "candidates\$Candidate"
} else {
    $link = Get-Item -LiteralPath (Join-Path $installHome "current") -Force
    if ($link.LinkType -ne "Junction") { throw "current must be an installed release junction" }
    $selected = @($link.Target)[0]
}
$env:HYPERFRAMES_AI_HOME = $installHome
Remove-Item Env:\HYPERFRAMES_AI_SESSION -ErrorAction SilentlyContinue
$arguments = @("session", "start")
if ($ReviewRoot) { $arguments += @("--review-root", $ReviewRoot) }
& (Join-Path $selected "work.cmd") @arguments
exit $LASTEXITCODE
'@
    [System.IO.File]::WriteAllText((Join-Path $workspace "start.ps1"), $launcher, (New-Object System.Text.UTF8Encoding $false))
    $rules = @'
# Windows Creation Workbench

Start each new conversation with `./start.ps1`. For a candidate use `./start.ps1 -Candidate <id> -ReviewRoot <isolated WorkStore>`.
The command prints a pinned session directory. Read its AGENTS.md and use that session's absolute work.cmd for every subsequent command. Do not run start again or change versions mid-conversation.
Read Skills only from that session's installed release. Never edit installed Harness or public components. Work-local layout, Slots and timing are creation; new effect internals are WSL development requests.
After an upgrade start a new conversation. Existing sessions retain their actual release, Skills and runtime.
'@
    [System.IO.File]::WriteAllText((Join-Path $workspace "AGENTS.md"), $rules, (New-Object System.Text.UTF8Encoding $false))
    Write-Output $workspace
}

function Set-Current([string]$Root, [string]$Destination) {
    $current = Join-Path $Root "current"
    $previous = Join-Path $Root "previous"
    $suffix = [guid]::NewGuid().ToString("N")
    $candidate = Join-Path $Root ".current-$suffix"
    $backup = Join-Path $Root ".previous-$suffix"
    Assert-Junction $current
    Assert-Junction $previous
    New-Item -ItemType Junction -Path $candidate -Target $Destination | Out-Null
    $movedCurrent = $false
    try {
        if (Test-Path -LiteralPath $previous) { Move-Item -LiteralPath $previous -Destination $backup }
        if (Test-Path -LiteralPath $current) {
            Move-Item -LiteralPath $current -Destination $previous
            $movedCurrent = $true
        }
        Move-Item -LiteralPath $candidate -Destination $current
    } catch {
        if ($movedCurrent -and -not (Test-Path -LiteralPath $current)) { Move-Item -LiteralPath $previous -Destination $current }
        if (Test-Path -LiteralPath $backup) { Move-Item -LiteralPath $backup -Destination $previous }
        throw
    } finally {
        if (Test-Path -LiteralPath $candidate) { Remove-Item -LiteralPath $candidate -Force }
    }
    if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
}

$lock = $null
try {
if ($Command -in @("install", "install-candidate", "workspace", "rollback")) {
    New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null
    try {
        $lock = [System.IO.File]::Open((Join-Path $ReleaseRoot ".install.lock"), [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    } catch { throw "Another install or rollback is active: $ReleaseRoot" }
}
switch ($Command) {
    "verify" {
        $manifest = Test-Release $PSScriptRoot
        Write-Output $manifest.release
    }
    { $_ -in @("install", "install-candidate") } {
        $manifest = Test-Release $PSScriptRoot
        $candidate = $manifest.channel -eq "candidate"
        if ($candidate -ne ($Command -eq "install-candidate")) { throw "Installation command does not match package channel" }
        $config = Get-LocalConfig
        $existingConfig = Join-Path $ReleaseRoot "config\local.json"
        if ($candidate -and (Test-Path -LiteralPath $existingConfig)) {
            $existing = Get-Content -LiteralPath $existingConfig -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($existing.work_root -ne $config.work_root) { throw "Candidate install cannot change the production WorkStore binding" }
        }
        $releases = Join-Path $ReleaseRoot $(if ($candidate) { "candidates" } else { "releases" })
        $destination = Join-Path $releases $manifest.release
        if (Test-Path -LiteralPath $destination) { throw "Release is already installed: $destination" }
        $staging = Join-Path $releases (".install-" + [guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Path $staging -Force | Out-Null
        Get-ChildItem -LiteralPath $PSScriptRoot -Force | Copy-Item -Destination $staging -Recurse -Force
        Test-Release $staging | Out-Null
        Test-NativeRuntime $staging $config (-not $candidate)
        Move-Item -LiteralPath $staging -Destination $destination
        $oldConfig = if (Test-Path -LiteralPath $existingConfig) { Get-Content -LiteralPath $existingConfig -Raw -Encoding UTF8 | ConvertFrom-Json } else { $null }
        if (-not $candidate -or -not $oldConfig) { Save-LocalConfig $config }
        try {
            if (-not $candidate) { Set-Current $ReleaseRoot $destination }
        } catch {
            if ($oldConfig) { Save-LocalConfig $oldConfig }
            elseif (Test-Path -LiteralPath $existingConfig) { Remove-Item -LiteralPath $existingConfig -Force }
            throw
        }
        Set-Workspace
        Write-Output $destination
    }
    "workspace" { Set-Workspace }
    "rollback" {
        $current = Join-Path $ReleaseRoot "current"
        $previous = Join-Path $ReleaseRoot "previous"
        $swap = Join-Path $ReleaseRoot ".rollback-$PID"
        Assert-Junction $current
        Assert-Junction $previous
        if (-not (Test-Path -LiteralPath $current) -or -not (Test-Path -LiteralPath $previous)) {
            throw "Both current and previous releases are required for rollback"
        }
        $target = @((Get-Item -LiteralPath $previous -Force).Target)[0]
        Test-Release $target | Out-Null
        Test-NativeRuntime $target (Get-LocalConfig) $true
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
} finally {
    if ($lock) { $lock.Dispose() }
}
