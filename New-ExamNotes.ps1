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

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

$Main = {
	# Dot-source the helper functions
	. $Helpers

	# Display application banner
	Show-Banner

	# Resolve and validate input paths
	$script:IndexPath = Resolve-Path $Index
	$script:TranscriptPath = Resolve-Path $Transcript

	# Determine output path from index filename if not specified
	if (-not $Output) {
		$videoTitle = Get-VideoTitle -IndexPath $script:IndexPath
		$script:Output = Join-Path $PSScriptRoot "output\${videoTitle}_Exam_Notes.md"
	}
	else {
		$script:Output = $Output
	}

	# Create output directory if it doesn't exist
	$outputDir = Split-Path -Parent $script:Output
	if (-not (Test-Path $outputDir)) {
		New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
	}

	# Display current configuration
	Show-Configuration

	# Validate and setup Python virtual environment
	$pythonExe = Confirm-PythonEnvironment
	Write-Host ""

	# Execute the Python notes generation pipeline
	Invoke-Pipeline -PythonExe $pythonExe

	# Display success message with output location
	Show-Success
}

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

$Helpers = {
	function Show-Stage {
		<#
        .SYNOPSIS
            Displays a formatted stage progress message.
        #>
		param(
			[string]$Stage,
			[string]$Message
		)

		Write-Host "[$Stage] " -ForegroundColor Cyan -NoNewline
		Write-Host $Message
	}

	function Show-Success {
		<#
        .SYNOPSIS
            Displays success completion banner.
        #>
		Write-Host ""
		Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
		Write-Host "✓ " -ForegroundColor Green -NoNewline
		Write-Host "Notes generated successfully!"
		Write-Host "  Output: $script:Output" -ForegroundColor Green
		Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
		Write-Host ""
	}

	function Show-Error {
		<#
        .SYNOPSIS
            Displays a formatted error message.
        #>
		param([string]$Message)

		Write-Host "✗ " -ForegroundColor Red -NoNewline
		Write-Host $Message
	}

	function Show-Banner {
		<#
        .SYNOPSIS
            Displays the application banner.
        #>
		Write-Host ""
		Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
		Write-Host "  Exam Notes Generator" -ForegroundColor Magenta
		Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
		Write-Host ""
	}

	function Show-Configuration {
		<#
        .SYNOPSIS
            Displays the current configuration settings.
        #>
		Write-Host "Configuration:" -ForegroundColor Yellow
		Write-Host "  Index:         $script:IndexPath"
		Write-Host "  Transcript:    $script:TranscriptPath"
		Write-Host "  Output:        $script:Output"
		Write-Host "  Extract Model: $ExtractModel"
		Write-Host "  Merge Model:   $MergeModel"
		Write-Host ""
	}

	function Confirm-PythonEnvironment {
		<#
        .SYNOPSIS
            Validates and sets up the Python virtual environment.
        .OUTPUTS
            Path to the Python executable in the virtual environment.
        #>
		$venvPath = Join-Path $PSScriptRoot ".venv"
		$venvPython = Join-Path $venvPath "Scripts\python.exe"
		$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"

		# Create virtual environment if it doesn't exist
		if (-not (Test-Path $venvPython)) {
			Show-Stage "Setup" "Creating Python virtual environment..."
			python -m venv $venvPath
			if ($LASTEXITCODE -ne 0) {
				throw "Failed to create virtual environment"
			}
			Write-Host "✓ " -ForegroundColor Green -NoNewline
			Write-Host "Virtual environment created"
		}

		# Install or update Python dependencies
		$pipPath = Join-Path $venvPath "Scripts\pip.exe"
		Show-Stage "Setup" "Checking Python dependencies..."
		& $pipPath install -q -r $requirementsPath
		if ($LASTEXITCODE -ne 0) {
			throw "Failed to install Python dependencies"
		}
		Write-Host "✓ " -ForegroundColor Green -NoNewline
		Write-Host "Dependencies verified"

		return $venvPython
	}

	function Get-VideoTitle {
		<#
        .SYNOPSIS
            Extracts a video title from the index file path.
        .PARAMETER IndexPath
            Path to the index file.
        .OUTPUTS
            Cleaned video title suitable for use as a filename.
        #>
		param([string]$IndexPath)

		$fileName = [System.IO.Path]::GetFileNameWithoutExtension($IndexPath)

		# Remove common prefixes like "Index - " or "TOC - "
		$title = $fileName -replace "^(Index|TOC|Contents)\s*[-_]\s*", ""

		# Clean up for use as filename
		$title = $title -replace "[^\w\s-]", "" -replace "\s+", "_"

		return $title
	}

	function Invoke-Pipeline {
		<#
        .SYNOPSIS
            Executes the Python notes generation pipeline.
        .PARAMETER PythonExe
            Path to the Python executable.
        #>
		param([string]$PythonExe)

		Show-Stage "Pipeline" "Starting notes generation..."
		Write-Host ""

		# Build Python command arguments
		$pythonArgs = @(
			"-m", "notes_generator.main",
			"--index", $script:IndexPath,
			"--transcript", $script:TranscriptPath,
			"--output", $script:Output,
			"--extract-model", $ExtractModel,
			"--merge-model", $MergeModel
		)

		# Set PYTHONPATH to include src/python
		$env:PYTHONPATH = Join-Path $PSScriptRoot "src\python"

		# Execute Python pipeline
		& $PythonExe @pythonArgs

		if ($LASTEXITCODE -ne 0) {
			throw "Pipeline failed with exit code $LASTEXITCODE"
		}
	}
}

# -------------------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------------------

try {
	Push-Location -Path $PSScriptRoot
	& $Main
}
catch {
	Write-Host ""
	Write-Host "✗ " -ForegroundColor Red -NoNewline
	Write-Host "Error: $_"
	Write-Host ""
	Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
	exit 1
}
finally {
	Pop-Location
}
