# -------------------------------------------------------------------------
# Program: New-ExamNotes.ps1
# Description: Generate exam-focused study notes from video transcripts
# Context: Main entry point for the Exam Notes Generator tool
# Author: Greg Tate
# -------------------------------------------------------------------------

<#
.SYNOPSIS
    Generates structured exam notes from a video transcript and index file.

.DESCRIPTION
    This tool processes a video transcript and its corresponding index (table of
    contents) to produce a comprehensive, exam-focused markdown notes document.

    The pipeline consists of these stages:
    - Normalize: Convert varied index formats to consistent JSON structure
    - Chunk: Split transcript into ~20KB pieces for processing
    - Extract: Generate section notes from each chunk (parallel, LLM)
    - Merge: Combine and deduplicate partials by section (LLM)
    - Assemble: Build final markdown document

.PARAMETER Index
    Path to the index file containing the table of contents with timestamps.
    Supports various formats (will be normalized by LLM).

.PARAMETER Transcript
    Path to the transcript file with timestamped content.

.PARAMETER Output
    Path for the generated notes file. Defaults to output/<VideoTitle>_Exam_Notes.md

.PARAMETER ExtractModel
    LLM model for extraction stage. Default: gpt-4.1-mini

.PARAMETER MergeModel
    LLM model for merge stage. Default: deepseek-r1

.PARAMETER SkipChunk
    Skip chunking if transcript is already chunked (provide ZIP path instead).

.EXAMPLE
    .\New-ExamNotes.ps1 -Index "data\samples\AI-900_FreeCodeCamp\Index - FreeCodeCamp.txt" `
                        -Transcript "data\samples\AI-900_FreeCodeCamp\Transcript - FreeCodeCamp.txt"

.EXAMPLE
    .\New-ExamNotes.ps1 -Index "path\to\index.txt" -Transcript "path\to\transcript.txt" `
                        -Output "output\MyNotes.md" -ExtractModel "gpt-4o"
#>

[CmdletBinding()]
param(
	[Parameter(Mandatory = $true, HelpMessage = "Path to the index/TOC file")]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$Index,

	[Parameter(Mandatory = $true, HelpMessage = "Path to the transcript file")]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$Transcript,

	[Parameter(HelpMessage = "Output path for generated notes")]
	[string]$Output,

	[Parameter(HelpMessage = "Model for extraction stage")]
	[string]$ExtractModel = "gpt-4.1-mini",

	[Parameter(HelpMessage = "Model for merge stage")]
	[string]$MergeModel = "deepseek-r1"
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Determine script root directory
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) {
	$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------

function Write-Stage {
	param([string]$Stage, [string]$Message)
	Write-Host "[$Stage] " -ForegroundColor Cyan -NoNewline
	Write-Host $Message
}

function Write-Success {
	param([string]$Message)
	Write-Host "✓ " -ForegroundColor Green -NoNewline
	Write-Host $Message
}

function Write-StageError {
	param([string]$Message)
	Write-Host "✗ " -ForegroundColor Red -NoNewline
	Write-Host $Message
}

function Test-PythonEnvironment {
	<#
    .SYNOPSIS
        Validates and sets up the Python virtual environment.
    #>
	$venvPath = Join-Path $ScriptRoot ".venv"
	$venvPython = Join-Path $venvPath "Scripts\python.exe"
	$requirementsPath = Join-Path $ScriptRoot "requirements.txt"

	# Check if venv exists
	if (-not (Test-Path $venvPython)) {
		Write-Stage "Setup" "Creating Python virtual environment..."
		python -m venv $venvPath
		if ($LASTEXITCODE -ne 0) {
			throw "Failed to create virtual environment"
		}
		Write-Success "Virtual environment created"
	}

	# Check if requirements need to be installed
	$pipPath = Join-Path $venvPath "Scripts\pip.exe"

	Write-Stage "Setup" "Checking Python dependencies..."
	& $pipPath install -q -r $requirementsPath
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to install Python dependencies"
	}
	Write-Success "Dependencies verified"

	return $venvPython
}

function Get-VideoTitle {
	<#
    .SYNOPSIS
        Extracts a video title from the index file path.
    #>
	param([string]$IndexPath)

	$fileName = [System.IO.Path]::GetFileNameWithoutExtension($IndexPath)

	# Remove common prefixes like "Index - " or "TOC - "
	$title = $fileName -replace "^(Index|TOC|Contents)\s*[-_]\s*", ""

	# Clean up for use as filename
	$title = $title -replace "[^\w\s-]", "" -replace "\s+", "_"

	return $title
}

# -------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------

try {
	Write-Host ""
	Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
	Write-Host "  Exam Notes Generator" -ForegroundColor Magenta
	Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
	Write-Host ""

	# Resolve paths to absolute
	$IndexPath = Resolve-Path $Index
	$TranscriptPath = Resolve-Path $Transcript

	# Determine output path if not specified
	if (-not $Output) {
		$videoTitle = Get-VideoTitle -IndexPath $IndexPath
		$Output = Join-Path $ScriptRoot "output\${videoTitle}_Exam_Notes.md"
	}

	# Ensure output directory exists
	$outputDir = Split-Path -Parent $Output
	if (-not (Test-Path $outputDir)) {
		New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
	}

	# Display configuration
	Write-Host "Configuration:" -ForegroundColor Yellow
	Write-Host "  Index:         $IndexPath"
	Write-Host "  Transcript:    $TranscriptPath"
	Write-Host "  Output:        $Output"
	Write-Host "  Extract Model: $ExtractModel"
	Write-Host "  Merge Model:   $MergeModel"
	Write-Host ""

	# Setup Python environment
	$pythonExe = Test-PythonEnvironment
	Write-Host ""

	# Run the Python pipeline
	Write-Stage "Pipeline" "Starting notes generation..."
	Write-Host ""

	$pythonArgs = @(
		"-m", "notes_generator.main",
		"--index", $IndexPath,
		"--transcript", $TranscriptPath,
		"--output", $Output,
		"--extract-model", $ExtractModel,
		"--merge-model", $MergeModel
	)

	# Set PYTHONPATH to include src/python
	$env:PYTHONPATH = Join-Path $ScriptRoot "src\python"

	# Execute Python pipeline
	& $pythonExe @pythonArgs

	if ($LASTEXITCODE -ne 0) {
		throw "Pipeline failed with exit code $LASTEXITCODE"
	}

	Write-Host ""
	Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
	Write-Success "Notes generated successfully!"
	Write-Host "  Output: $Output" -ForegroundColor Green
	Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
	Write-Host ""

	exit 0
}
catch {
	Write-Host ""
	Write-StageError "Error: $_"
	Write-Host ""
	Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
	exit 1
}
