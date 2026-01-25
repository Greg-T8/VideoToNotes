<#
.SYNOPSIS
    Generates exam-focused study notes from video transcripts using GitHub Models API.

.DESCRIPTION
    This script wraps the Python exam notes generator, providing a PowerShell-native
    interface with parameter validation, prerequisite checking, and enhanced output.

.PARAMETER ContentsFile
    Path to the markdown file containing the table of contents with timestamps.

.PARAMETER TranscriptZip
    Path to the ZIP file containing transcript chunks (20KB each).

.PARAMETER OutputFile
    Path for the generated exam notes. Defaults to "exam_notes.md" in current directory.

.PARAMETER PromptsDir
    Directory containing prompt templates. Defaults to "./prompts" relative to script.

.PARAMETER Stage1Model
    Model for chunk processing (fast extraction). Default: openai/gpt-4.1-mini

.PARAMETER Stage2Model
    Model for section merging (quality reasoning). Default: deepseek/deepseek-r1-0528

.PARAMETER DryRun
    Show what would be processed without making API calls.

.PARAMETER Force
    Overwrite output file if it exists.

.EXAMPLE
    .\Generate-ExamNotes.ps1 -ContentsFile .\contents.md -TranscriptZip .\transcript.zip

.EXAMPLE
    .\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -OutputFile "AZ-104_Notes.md"

.EXAMPLE
    .\Generate-ExamNotes.ps1 .\contents.md .\transcript.zip -Stage1Model "openai/gpt-4.1" -Force

.NOTES
    Requires:
    - Python 3.11+
    - GitHub CLI (gh) authenticated
    - OpenAI Python package: pip install openai
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$ContentsFile,

    [Parameter(Mandatory, Position = 1)]
    [ValidateScript({ Test-Path $_ -PathType Leaf })]
    [string]$TranscriptZip,

    [Parameter(Position = 2)]
    [string]$OutputFile = "exam_notes.md",

    [Parameter()]
    [string]$PromptsDir,

    [Parameter()]
    [ValidateSet(
        "openai/gpt-4.1-mini",
        "openai/gpt-4.1",
        "openai/gpt-5-mini",
        "deepseek/deepseek-r1-0528",
        "deepseek/deepseek-v3-0324"
    )]
    [string]$Stage1Model = "openai/gpt-4.1-mini",

    [Parameter()]
    [ValidateSet(
        "deepseek/deepseek-r1-0528",
        "deepseek/deepseek-v3-0324",
        "openai/gpt-4.1",
        "openai/gpt-5-mini",
        "openai/o3-mini"
    )]
    [string]$Stage2Model = "deepseek/deepseek-r1-0528",

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$Force
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Default prompts directory relative to script location
if (-not $PromptsDir) {
    $PromptsDir = Join-Path $ScriptDir "prompts"
}

# Python script location
$PythonScript = Join-Path $ScriptDir "exam_notes_generator.py"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    
    $symbol = switch ($Type) {
        "Info"    { "ℹ️ " }
        "Success" { "✅" }
        "Warning" { "⚠️ " }
        "Error"   { "❌" }
        "Step"    { "▶️ " }
    }
    
    $color = switch ($Type) {
        "Info"    { "Cyan" }
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error"   { "Red" }
        "Step"    { "White" }
    }
    
    Write-Host "$symbol $Message" -ForegroundColor $color
}

function Test-Prerequisites {
    <#
    .SYNOPSIS
        Validates all prerequisites are met before running.
    #>
    
    $issues = @()
    
    # Check Python
    Write-Status "Checking Python..." -Type Step
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
                $issues += "Python 3.11+ required. Found: $pythonVersion"
            } else {
                Write-Status "Python: $pythonVersion" -Type Success
            }
        }
    } catch {
        $issues += "Python not found. Install from https://python.org"
    }
    
    # Check GitHub CLI
    Write-Status "Checking GitHub CLI..." -Type Step
    try {
        $null = & gh --version 2>&1
        
        # Check authentication
        $token = & gh auth token 2>&1
        if ($LASTEXITCODE -ne 0) {
            $issues += "GitHub CLI not authenticated. Run: gh auth login"
        } else {
            Write-Status "GitHub CLI: Authenticated" -Type Success
        }
    } catch {
        $issues += "GitHub CLI not found. Install from https://cli.github.com"
    }
    
    # Check OpenAI package
    Write-Status "Checking OpenAI package..." -Type Step
    $pipCheck = & python -c "import openai; print(openai.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $issues += "OpenAI package not installed. Run: pip install openai"
    } else {
        Write-Status "OpenAI package: v$pipCheck" -Type Success
    }
    
    # Check Python script exists
    if (-not (Test-Path $PythonScript)) {
        $issues += "Python script not found: $PythonScript"
    }
    
    # Check prompts directory
    if (-not (Test-Path $PromptsDir)) {
        $issues += "Prompts directory not found: $PromptsDir"
    } else {
        $requiredPrompts = @("chunk_process.md", "section_merge.md")
        foreach ($prompt in $requiredPrompts) {
            $promptPath = Join-Path $PromptsDir $prompt
            if (-not (Test-Path $promptPath)) {
                $issues += "Required prompt file not found: $promptPath"
            }
        }
    }
    
    # Check output file
    if ((Test-Path $OutputFile) -and -not $Force) {
        $issues += "Output file exists: $OutputFile (use -Force to overwrite)"
    }
    
    return $issues
}

function Get-TranscriptInfo {
    <#
    .SYNOPSIS
        Extracts information about the transcript ZIP without processing.
    #>
    param([string]$ZipPath)
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $chunks = $zip.Entries | Where-Object { 
            $_.Name -match '\.(txt|md)$' -and $_.Length -gt 0 
        }
        
        $totalSize = ($chunks | Measure-Object -Property Length -Sum).Sum
        
        return @{
            ChunkCount = $chunks.Count
            TotalSizeKB = [math]::Round($totalSize / 1KB, 1)
            Files = $chunks.Name
        }
    } finally {
        $zip.Dispose()
    }
}

function Get-ContentsInfo {
    <#
    .SYNOPSIS
        Parses the contents file to extract section count.
    #>
    param([string]$ContentsPath)
    
    $content = Get-Content $ContentsPath -Raw
    $lines = $content -split "`n"
    
    # Extract title
    $title = ($lines | Where-Object { $_ -match "^# " } | Select-Object -First 1) -replace "^# ", ""
    
    # Count sections by heading level
    $level2 = ($lines | Where-Object { $_ -match "^## " }).Count
    $level3 = ($lines | Where-Object { $_ -match "^### " }).Count
    $level4 = ($lines | Where-Object { $_ -match "^#### " }).Count
    
    return @{
        Title = $title.Trim()
        Level2Sections = $level2
        Level3Sections = $level3
        Level4Sections = $level4
        TotalSections = $level2 + $level3 + $level4
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Banner
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           📚 Exam Notes Generator                            ║" -ForegroundColor Cyan
Write-Host "║           Using GitHub Models API                            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""
$issues = Test-Prerequisites

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Status "Prerequisites check failed:" -Type Error
    foreach ($issue in $issues) {
        Write-Host "   • $issue" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Status "All prerequisites met!" -Type Success
Write-Host ""

# Analyze inputs
Write-Host "Analyzing inputs..." -ForegroundColor Yellow
Write-Host ""

$contentsInfo = Get-ContentsInfo -ContentsPath $ContentsFile
Write-Status "Contents: $($contentsInfo.Title)" -Type Info
Write-Host "   Sections: $($contentsInfo.TotalSections) total ($($contentsInfo.Level2Sections) L2, $($contentsInfo.Level3Sections) L3, $($contentsInfo.Level4Sections) L4)"

$transcriptInfo = Get-TranscriptInfo -ZipPath $TranscriptZip
Write-Status "Transcript: $($transcriptInfo.ChunkCount) chunks ($($transcriptInfo.TotalSizeKB) KB)" -Type Info

# Estimate API usage
$estimatedStage1 = $transcriptInfo.ChunkCount
$estimatedStage2 = [math]::Min($contentsInfo.TotalSections, $transcriptInfo.ChunkCount * 2)
$estimatedTotal = $estimatedStage1 + $estimatedStage2

Write-Host ""
Write-Host "Estimated API usage:" -ForegroundColor Yellow
Write-Host "   Stage 1 ($Stage1Model): ~$estimatedStage1 requests"
Write-Host "   Stage 2 ($Stage2Model): ~$estimatedStage2 requests"
Write-Host "   Total: ~$estimatedTotal premium requests"
Write-Host ""

# Dry run - stop here
if ($DryRun) {
    Write-Status "Dry run complete. No API calls made." -Type Warning
    Write-Host ""
    Write-Host "To process, run without -DryRun flag." -ForegroundColor Gray
    exit 0
}

# Confirm before proceeding
$confirm = Read-Host "Proceed with generation? (Y/n)"
if ($confirm -and $confirm -notmatch "^[Yy]") {
    Write-Status "Cancelled by user." -Type Warning
    exit 0
}

Write-Host ""

# Build Python arguments
$pythonArgs = @(
    $PythonScript
    (Resolve-Path $ContentsFile).Path
    (Resolve-Path $TranscriptZip).Path
    "--output", $OutputFile
    "--prompts", $PromptsDir
    "--stage1-model", $Stage1Model
    "--stage2-model", $Stage2Model
)

# Execute Python script
Write-Status "Starting generation..." -Type Step
Write-Host ""

$startTime = Get-Date

try {
    & python @pythonArgs
    
    if ($LASTEXITCODE -ne 0) {
        throw "Python script exited with code $LASTEXITCODE"
    }
    
    $duration = (Get-Date) - $startTime
    
    Write-Host ""
    Write-Status "Generation complete!" -Type Success
    Write-Host ""
    Write-Host "   Output: $((Resolve-Path $OutputFile).Path)" -ForegroundColor Green
    Write-Host "   Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor Gray
    Write-Host "   Size: $([math]::Round((Get-Item $OutputFile).Length / 1KB, 1)) KB" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Status "Generation failed: $_" -Type Error
    exit 1
}