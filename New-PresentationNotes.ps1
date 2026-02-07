# -------------------------------------------------------------------------
# Program: New-PresentationNotes.ps1
# Description: Generate study notes from a slide presentation (PDF) with
#              an accompanying video recording
# Context: Main entry point for the PresentationNotes pipeline
# Author: Greg Tate
# -------------------------------------------------------------------------

<#
.SYNOPSIS
    Generates structured notes from a slide presentation and its video recording.

.DESCRIPTION
    This tool processes a PDF slide deck and its accompanying video to produce
    a comprehensive markdown notes document with embedded slide images.

    The pipeline stages:
    1. Extract:    Render PDF pages as images and extract text per slide (Python)
    2. Transcribe: Extract audio from the video and transcribe via Azure Speech
    3. Align:      Map transcript segments to slides using LLM
    4. Annotate:   Generate detailed notes per slide using LLM
    5. Assemble:   Build final markdown with embedded slide images

    The video can be provided as a local file or as a stream URL. If neither
    is provided, a pre-existing SRT transcript file must be supplied.

.PARAMETER PdfFile
    Path to the PDF slide presentation.

.PARAMETER VideoFile
    Path to a local video file (e.g. .mp4, .mkv, .webm).
    If provided, audio will be extracted and transcribed.

.PARAMETER StreamUrl
    URL to a video stream manifest (e.g. .mpd, .m3u8).
    The stream will be downloaded and then transcribed.

.PARAMETER Transcript
    Path to a pre-existing SRT transcript file.
    Use this if you already have a transcript and don't need transcription.

.PARAMETER Output
    Path for the generated notes file.
    Defaults to output/<PdfTitle>_Presentation_Notes.md

.PARAMETER Model
    LLM model for alignment and annotation stages.
    Default: gpt-4.1-mini

.PARAMETER Language
    Language code for transcription. Default: en-US

.PARAMETER Dpi
    DPI for PDF rendering. Higher values produce sharper images.
    Default: 200

.PARAMETER KeepIntermediateFiles
    Keep intermediate audio files after transcription.

.EXAMPLE
    .\New-PresentationNotes.ps1 -PdfFile "slides.pdf" -VideoFile "recording.mp4"

.EXAMPLE
    .\New-PresentationNotes.ps1 -PdfFile "slides.pdf" `
                                -StreamUrl "https://example.com/manifest.mpd"

.EXAMPLE
    .\New-PresentationNotes.ps1 -PdfFile "slides.pdf" `
                                -Transcript "existing_transcript.srt"
#>

[CmdletBinding(DefaultParameterSetName = 'LocalVideo')]
param(
	[Parameter(Mandatory = $true, Position = 0,
		HelpMessage = 'Path to the PDF slide presentation')]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$PdfFile,

	[Parameter(ParameterSetName = 'LocalVideo', Mandatory = $true,
		HelpMessage = 'Path to a local video file')]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$VideoFile,

	[Parameter(ParameterSetName = 'Stream', Mandatory = $true,
		HelpMessage = 'URL to a video stream manifest (.mpd, .m3u8)')]
	[string]$StreamUrl,

	[Parameter(ParameterSetName = 'ExistingTranscript', Mandatory = $true,
		HelpMessage = 'Path to a pre-existing SRT transcript file')]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$Transcript,

	[Parameter(HelpMessage = 'Output path for generated notes')]
	[string]$Output,

	[Parameter(HelpMessage = 'Model for alignment and annotation')]
	[string]$Model = 'gpt-4.1-mini',

	[Parameter(HelpMessage = 'Language code for transcription')]
	[string]$Language = 'en-US',

	[Parameter(HelpMessage = 'DPI for PDF rendering')]
	[int]$Dpi = 200,

	[Parameter(HelpMessage = 'Keep intermediate audio files')]
	[switch]$KeepIntermediateFiles
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

$Main = {
	# Dot-source the helper functions
	. $Helpers

	# Display application banner
	Show-Banner

	# Verify GitHub CLI authentication for API access
	Confirm-GitHubAuth

	# Resolve the PDF path and derive a title
	$pdfResolved = Resolve-Path $PdfFile
	$pdfTitle = Get-PdfTitle -PdfPath $pdfResolved

	# Set up the staging folder for all intermediate files
	$safeName = ConvertTo-SafeFileName -Name $pdfTitle
	$script:StagingFolder = Join-Path $PSScriptRoot "staging\$safeName"

	if (-not (Test-Path $script:StagingFolder)) {
		New-Item -ItemType Directory -Path $script:StagingFolder -Force | Out-Null
	}

	# Phase 1: Transcription (unless a transcript was provided)
	if ($Transcript) {
		# Use existing transcript
		$script:TranscriptPath = Resolve-Path $Transcript
		Write-Host "Using existing transcript: $script:TranscriptPath" -ForegroundColor Green
	}
	elseif ($StreamUrl) {
		# Download stream then transcribe
		$script:TranscriptPath = Invoke-StreamWorkflow `
			-Url $StreamUrl `
			-StagingFolder $script:StagingFolder
	}
	else {
		# Transcribe from local video file
		$script:TranscriptPath = Invoke-VideoWorkflow `
			-VideoPath $VideoFile `
			-StagingFolder $script:StagingFolder
	}

	# Determine output path from PDF title if not specified
	if (-not $Output) {
		$script:Output = Join-Path $PSScriptRoot "output\${safeName}_Presentation_Notes.md"
	}
	else {
		$script:Output = $Output
	}

	# Create output directory if it doesn't exist
	$outputDir = Split-Path -Parent $script:Output
	if (-not (Test-Path $outputDir)) {
		New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
	}

	# Phase 2: Notes Generation Pipeline
	Show-Phase 'PHASE 2: Presentation Notes' 'Extract slides, align transcript, generate notes'

	# Display current configuration
	Show-Configuration -PdfPath $pdfResolved -Title $pdfTitle

	# Validate and setup Python virtual environment
	$pythonExe = Confirm-PythonEnvironment

	# Execute the Python presentation notes pipeline
	Invoke-Pipeline `
		-PythonExe $pythonExe `
		-PdfPath $pdfResolved `
		-Title $pdfTitle

	# Display success message with output location
	Show-Success
}

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

$Helpers = {

	function Invoke-VideoWorkflow {
		<#
		.SYNOPSIS
			Transcribes audio from a local video file.
		#>
		param(
			[string]$VideoPath,
			[string]$StagingFolder
		)

		Show-Phase 'PHASE 1: Video Transcription' 'Extract audio and transcribe'

		$transcribeScript = Join-Path $PSScriptRoot 'src\powershell\Invoke-VideoTranscription.ps1'

		$result = & $transcribeScript `
			-VideoFile $VideoPath `
			-OutputPath $StagingFolder `
			-Language $Language `
			-FlatOutput `
			-KeepIntermediateFiles:$KeepIntermediateFiles

		if ($LASTEXITCODE -ne 0) {
			throw 'Video transcription failed'
		}

		return $result.SrtFile
	}

	function Invoke-StreamWorkflow {
		<#
		.SYNOPSIS
			Downloads a video stream, then transcribes the audio.
		#>
		param(
			[string]$Url,
			[string]$StagingFolder
		)

		Show-Phase 'PHASE 1a: Stream Download' 'Downloading video stream'

		# Download the stream to a local file
		$saveScript = Join-Path $PSScriptRoot 'src\powershell\Save-StreamVideo.ps1'

		$downloadResult = & $saveScript `
			-ManifestUrl $Url `
			-OutputPath $StagingFolder `
			-Format 'mp4'

		if ($LASTEXITCODE -ne 0) {
			throw 'Stream download failed'
		}

		$downloadedVideo = $downloadResult.OutputFile

		Show-Phase 'PHASE 1b: Transcription' 'Transcribing downloaded video'

		# Transcribe the downloaded video
		$transcribeScript = Join-Path $PSScriptRoot 'src\powershell\Invoke-VideoTranscription.ps1'

		$result = & $transcribeScript `
			-VideoFile $downloadedVideo `
			-OutputPath $StagingFolder `
			-Language $Language `
			-FlatOutput `
			-KeepIntermediateFiles:$KeepIntermediateFiles

		if ($LASTEXITCODE -ne 0) {
			throw 'Video transcription failed'
		}

		return $result.SrtFile
	}

	function Get-PdfTitle {
		<#
		.SYNOPSIS
			Derives a human-readable title from a PDF filename.
		#>
		param([string]$PdfPath)

		$baseName = [System.IO.Path]::GetFileNameWithoutExtension($PdfPath)

		# Clean up common filename patterns
		$title = $baseName -replace '_', ' ' -replace '-', ' '

		# Collapse multiple spaces
		$title = $title -replace '\s+', ' '

		return $title.Trim()
	}

	function ConvertTo-SafeFileName {
		<#
		.SYNOPSIS
			Converts a string to a safe filename by replacing invalid characters.
		#>
		param([string]$Name)

		# Replace invalid file name characters with underscores
		$invalidChars = [System.IO.Path]::GetInvalidFileNameChars() -join ''
		$safeName = $Name -replace "[$([regex]::Escape($invalidChars))]", '_'

		# Replace spaces and multiple underscores
		$safeName = $safeName -replace '[\s_]+', '_'

		# Trim underscores from ends
		$safeName = $safeName.Trim('_')

		return $safeName
	}

	function Confirm-GitHubAuth {
		<#
		.SYNOPSIS
			Verifies GitHub CLI is authenticated for API access.
		#>
		Show-Stage 'Auth' 'Checking GitHub CLI status...'

		# Check if gh CLI is installed
		$ghPath = Get-Command gh -ErrorAction SilentlyContinue
		if (-not $ghPath) {
			throw 'GitHub CLI (gh) not found. Install from https://cli.github.com/'
		}

		# Get authentication status
		$statusOutput = gh auth status 2>&1
		if ($LASTEXITCODE -ne 0) {
			Write-Host ''
			Write-Host $statusOutput -ForegroundColor DarkGray
			Write-Host ''
			throw "GitHub CLI not authenticated. Run 'gh auth login' first."
		}

		# Extract the logged-in account
		$accountLine = $statusOutput |
			Select-String -Pattern 'Logged in to .+ account (.+)' |
			Select-Object -First 1

		if ($accountLine) {
			$account = $accountLine.Matches.Groups[1].Value.Trim()
			Write-Host '✓ ' -ForegroundColor Green -NoNewline
			Write-Host "Authenticated as: $account"
		}
		else {
			Write-Host '✓ ' -ForegroundColor Green -NoNewline
			Write-Host 'GitHub CLI authenticated'
		}
	}

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

	function Show-Phase {
		<#
		.SYNOPSIS
			Displays a major phase header with visual separation.
		#>
		param(
			[string]$Phase,
			[string]$Description
		)

		Write-Host ''
		Write-Host '───────────────────────────────────────────────────────────────' -ForegroundColor DarkGray
		Write-Host "  $Phase" -ForegroundColor Yellow
		if ($Description) {
			Write-Host "  $Description" -ForegroundColor DarkGray
		}
		Write-Host '───────────────────────────────────────────────────────────────' -ForegroundColor DarkGray
	}

	function Show-Success {
		<#
		.SYNOPSIS
			Displays success completion banner.
		#>
		Write-Host ''
		Write-Host '═══════════════════════════════════════════════════════════════' -ForegroundColor Green
		Write-Host '✓ ' -ForegroundColor Green -NoNewline
		Write-Host 'Presentation notes generated successfully!'
		Write-Host "  Output: $script:Output" -ForegroundColor Green
		Write-Host '═══════════════════════════════════════════════════════════════' -ForegroundColor Green
		Write-Host ''
	}

	function Show-Banner {
		<#
		.SYNOPSIS
			Displays the application banner.
		#>
		Write-Host ''
		Write-Host '═══════════════════════════════════════════════════════════════' -ForegroundColor Magenta
		Write-Host '  PresentationNotes' -ForegroundColor Magenta
		Write-Host '═══════════════════════════════════════════════════════════════' -ForegroundColor Magenta
		Write-Host ''
	}

	function Show-Configuration {
		<#
		.SYNOPSIS
			Displays the current configuration settings.
		#>
		param(
			[string]$PdfPath,
			[string]$Title
		)

		Write-Host 'Configuration:' -ForegroundColor Yellow
		Write-Host "  PDF:         $PdfPath"
		Write-Host "  Title:       $Title"
		Write-Host "  Transcript:  $script:TranscriptPath"
		Write-Host "  Output:      $script:Output"
		Write-Host "  Model:       $Model"
		Write-Host "  DPI:         $Dpi"
		Write-Host ''
	}

	function Confirm-PythonEnvironment {
		<#
		.SYNOPSIS
			Validates and sets up the Python virtual environment.
		.OUTPUTS
			Path to the Python executable in the virtual environment.
		#>
		$venvPath = Join-Path $PSScriptRoot '.venv'
		$venvPython = Join-Path $venvPath 'Scripts\python.exe'
		$requirementsPath = Join-Path $PSScriptRoot 'requirements.txt'

		# Create virtual environment if it doesn't exist
		if (-not (Test-Path $venvPython)) {
			Show-Stage 'Setup' 'Creating Python virtual environment...'
			python -m venv $venvPath
			if ($LASTEXITCODE -ne 0) {
				throw 'Failed to create virtual environment'
			}
			Write-Host '✓ ' -ForegroundColor Green -NoNewline
			Write-Host 'Virtual environment created'
		}

		# Install or update Python dependencies
		$pipPath = Join-Path $venvPath 'Scripts\pip.exe'
		Show-Stage 'Setup' 'Checking Python dependencies...'

		# Suppress pip output
		$null = & $pipPath install -q --disable-pip-version-check --no-cache-dir -r $requirementsPath 2>&1

		if ($LASTEXITCODE -ne 0) {
			throw 'Failed to install Python dependencies'
		}
		Write-Host '✓ ' -ForegroundColor Green -NoNewline
		Write-Host 'Dependencies verified'

		return $venvPython
	}

	function Invoke-Pipeline {
		<#
		.SYNOPSIS
			Executes the Python presentation notes pipeline.
		#>
		param(
			[string]$PythonExe,
			[string]$PdfPath,
			[string]$Title
		)

		Show-Stage 'Pipeline' 'Starting presentation notes generation...'
		Write-Host ''

		# Build Python command arguments
		$pythonArgs = @(
			'-m', 'presentation_notes.main',
			'--pdf', $PdfPath,
			'--transcript', $script:TranscriptPath,
			'--output', $script:Output,
			'--model', $Model,
			'--title', $Title,
			'--dpi', $Dpi,
			'--debug'
		)

		# Set debug directory in the staging folder
		$debugDir = Join-Path $script:StagingFolder 'debug'
		$pythonArgs += '--debug-dir', $debugDir

		# Set PYTHONPATH to include src/python
		$env:PYTHONPATH = Join-Path $PSScriptRoot 'src\python'

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
	Write-Host ''
	Write-Host '✗ ' -ForegroundColor Red -NoNewline
	Write-Host "Error: $_"
	Write-Host ''
	Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
	exit 1
}
finally {
	Pop-Location
}
