<#
.SYNOPSIS
    Install the extend-slides skill into a personal or project-level skills directory.

.DESCRIPTION
    The repository root IS the skill folder (its name must match "name" in SKILL.md).
    This script mirrors SKILL.md, references/, assets/, scripts/ and README.md into
    <skills root>\extend-slides.

    IMPORTANT - keep this file ASCII-only.
    Windows PowerShell 5.1 reads .ps1 files using the system ANSI code page unless the
    file carries a UTF-8 BOM. Non-ASCII text in this script would be decoded wrongly and
    break parsing. That is why all messages below are in English.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope personal
    Install into the personal skills root (.copilot / .workbuddy / .agents / .claude).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope project -ProjectPath D:\MyCourse
    Install into D:\MyCourse\.github\skills\extend-slides.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope both -ProjectPath D:\MyCourse -Force
    Install into both roots; -Force allows overwriting a target that has no SKILL.md.
#>
[CmdletBinding()]
param(
    [ValidateSet('personal', 'project', 'both')]
    [string]$Scope = 'personal',

    [string]$ProjectPath = (Get-Location).Path,

    [string]$PersonalRoot = '',

    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$SkillName = 'extend-slides'
$Source = Split-Path -Parent $PSScriptRoot

# ---------- Validate source repository ----------
if (-not (Test-Path (Join-Path $Source 'SKILL.md'))) {
    throw "SKILL.md not found in $Source. Make sure this script lives in the skill's scripts folder."
}

$sourceFolderName = Split-Path -Leaf $Source
$skillFile = Join-Path $Source 'SKILL.md'
$nameLine = Select-String -Path $skillFile -Pattern '^name:\s*(\S+)' | Select-Object -First 1
$declaredName = if ($nameLine) { $nameLine.Matches[0].Groups[1].Value.Trim('''"') } else { '' }

if ($declaredName -ne $sourceFolderName) {
    Write-Warning "Folder name '$sourceFolderName' does not match name '$declaredName' in SKILL.md. The skill may not be discovered."
}

# ---------- Resolve personal skills root ----------
function Resolve-PersonalRoot {
    param([string]$Explicit)
    if ($Explicit) { return $Explicit }

    $candidates = @(
        (Join-Path $env:USERPROFILE '.copilot\skills'),
        (Join-Path $env:USERPROFILE '.workbuddy\skills'),
        (Join-Path $env:USERPROFILE '.agents\skills'),
        (Join-Path $env:USERPROFILE '.claude\skills')
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $candidates[0]
}

# ---------- Install ----------
function Install-SkillTo {
    param([string]$Root, [string]$Label)

    $destination = Join-Path $Root $SkillName

    if (Test-Path $destination) {
        $hasSkillFile = Test-Path (Join-Path $destination 'SKILL.md')
        if (-not $hasSkillFile -and -not $Force) {
            Write-Warning "Target exists but is not a valid skill folder: $destination. Use -Force to overwrite. Skipped."
            return
        }
    } else {
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
    }

    $robocopyArgs = @(
        $Source, $destination,
        '/MIR',
        '/XD', '.git', '.venv', 'venv', '.vscode', 'node_modules',
        '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache',
        '/XF', '*.log', '*.pyc',
        '/NFL', '/NDL', '/NJH', '/NJS', '/NP', '/R:2', '/W:1'
    )

    $result = Start-Process -FilePath 'robocopy' -ArgumentList $robocopyArgs -Wait -PassThru -NoNewWindow
    if ($result.ExitCode -ge 8) {
        Write-Error "Sync to $destination failed (robocopy exit code $($result.ExitCode))."
        return
    }

    Write-Host "[$Label] installed: $destination" -ForegroundColor Green
}

$installed = @()

if ($Scope -in @('personal', 'both')) {
    $personalRoot = Resolve-PersonalRoot -Explicit $PersonalRoot
    if (-not (Test-Path $personalRoot)) {
        New-Item -ItemType Directory -Path $personalRoot -Force | Out-Null
        Write-Host "Created personal skills root: $personalRoot"
    }
    Install-SkillTo -Root $personalRoot -Label 'personal'
    $installed += $personalRoot
}

if ($Scope -in @('project', 'both')) {
    if (-not (Test-Path $ProjectPath)) {
        throw "Project path does not exist: $ProjectPath"
    }
    $projectSkills = Join-Path $ProjectPath '.github\skills'
    if (-not (Test-Path $projectSkills)) {
        New-Item -ItemType Directory -Path $projectSkills -Force | Out-Null
    }
    Install-SkillTo -Root $projectSkills -Label 'project'
    $installed += $projectSkills
}

Write-Host ''
Write-Host 'Done. Next steps:' -ForegroundColor Cyan
foreach ($root in $installed) {
    Write-Host "  - Verify file exists: $(Join-Path $root "$SkillName\SKILL.md")"
}
Write-Host '  - Run "Developer: Reload Window" in VS Code, then type "/" and check that extend-slides appears.'
Write-Host '  - If it does not trigger automatically, check that the SKILL.md description contains the keywords you used.'
