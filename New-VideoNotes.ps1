# -------------------------------------------------------------------------
# Program: New-VideoNotes.ps1
# Description: Generate study notes from video transcripts
# Context: Main entry point for the VideoToNotes tool
# Author: Greg Tate
# -------------------------------------------------------------------------

<#
.SYNOPSIS
    Generates structured notes from a YouTube video or existing files.

.DESCRIPTION
    This tool processes a video transcript and its corresponding index (table of
    contents) to produce a comprehensive markdown notes document.

    When provided with a YouTube URL, it will:
    1. Extract video metadata and chapter information (contents/index)
    2. Download and transcribe the audio to SRT format
    3. Process the transcript and index through the notes pipeline

    When provided with existing files, it uses them directly.

    The pipeline consists of these stages:
    - Transcribe: Download YouTube audio and transcribe (if URL provided)
    - Normalize: Convert varied index formats to consistent JSON structure
    - Chunk: Split transcript into ~20KB pieces for processing
    - Extract: Generate section notes from each chunk (parallel, LLM)
    - Merge: Combine and deduplicate partials by section (LLM)
    - Assemble: Build final markdown document

.PARAMETER YouTubeUrl
    YouTube video URL to transcribe and generate notes from.
    If provided, -Index and -Transcript are ignored.

.PARAMETER Index
    Path to the index file containing the table of contents with timestamps.
    Supports various formats (will be normalized by LLM).

.PARAMETER Transcript
    Path to the transcript file with timestamped content.

.PARAMETER Output
    Path for the generated notes file. Defaults to output/<VideoTitle>_Notes.md

.PARAMETER ExtractModel
    LLM model for extraction stage. Default: gpt-4.1-mini

.PARAMETER MergeModel
    LLM model for merge stage. Default: gpt-4.1-mini

.PARAMETER Language
    Language code for transcription. Default: en-US

.PARAMETER KeepIntermediateFiles
    Keep intermediate audio files after transcription.

.EXAMPLE
    .\New-VideoNotes.ps1 -YouTubeUrl "https://www.youtube.com/watch?v=VIDEO_ID"

.EXAMPLE
    .\New-VideoNotes.ps1 -Index "data\samples\contents.md" `
                        -Transcript "data\samples\transcript.srt"

.EXAMPLE
    .\New-VideoNotes.ps1 -YouTubeUrl "https://www.youtube.com/watch?v=VIDEO_ID" `
                        -Output "output\MyNotes.md" -ExtractModel "gpt-4o"
#>

[CmdletBinding(DefaultParameterSetName = 'YouTube')]
param(
	[Parameter(ParameterSetName = 'YouTube', Mandatory = $true, Position = 0,
		HelpMessage = "YouTube video URL to transcribe")]
	[string]$YouTubeUrl,

	[Parameter(ParameterSetName = 'Files', Mandatory = $true,
		HelpMessage = "Path to the index/TOC file")]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$Index,

	[Parameter(ParameterSetName = 'Files', Mandatory = $true,
		HelpMessage = "Path to the transcript file")]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$Transcript,

	[Parameter(HelpMessage = "Output path for generated notes")]
	[string]$Output,

	[Parameter(HelpMessage = "Model for extraction stage")]
	[string]$ExtractModel = "gpt-4.1-mini",

	[Parameter(HelpMessage = "Model for merge stage")]
	[string]$MergeModel = "gpt-4.1-mini",

	[Parameter(ParameterSetName = 'YouTube',
		HelpMessage = "Language code for transcription")]
	[string]$Language = "en-US",

	[Parameter(ParameterSetName = 'YouTube',
		HelpMessage = "Keep intermediate audio files")]
	[switch]$KeepIntermediateFiles
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

	# Verify GitHub CLI authentication for API access
	Confirm-GitHubAuth

	# Handle YouTube URL or file paths
	if ($YouTubeUrl) {
		# Transcribe from YouTube
		$transcriptionResult = Invoke-YouTubeWorkflow -Url $YouTubeUrl

		$script:IndexPath = $transcriptionResult.IndexPath
		$script:TranscriptPath = $transcriptionResult.TranscriptPath
		$script:DataFolder = $transcriptionResult.DataFolder
		$videoTitle = $transcriptionResult.VideoTitle
	}
	else {
		# Use provided files
		$script:IndexPath = Resolve-Path $Index
		$script:TranscriptPath = Resolve-Path $Transcript
		$script:DataFolder = Split-Path -Parent $script:IndexPath
		$videoTitle = Get-VideoTitle -IndexPath $script:IndexPath
	}

	# Determine output path from video title if not specified
	if (-not $Output) {
		$script:Output = Join-Path $PSScriptRoot "output\${videoTitle}_Notes.md"
	}
	else {
		$script:Output = $Output
	}

	# Create output directory if it doesn't exist
	$outputDir = Split-Path -Parent $script:Output
	if (-not (Test-Path $outputDir)) {
		New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
	}

	# Phase 3: Notes Generation Pipeline
	Show-Phase "PHASE 3: Notes Generation" "Normalize, extract, merge, and assemble notes"

	# Display current configuration
	Show-Configuration

	# Validate and setup Python virtual environment
	$pythonExe = Confirm-PythonEnvironment

	# Execute the Python notes generation pipeline
	Invoke-Pipeline -PythonExe $pythonExe

	# Display success message with output location
	Show-Success
}

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

$Helpers = {
	function Invoke-YouTubeWorkflow {
		<#
        .SYNOPSIS
            Runs the full YouTube transcription workflow.
        .DESCRIPTION
            Downloads video, extracts contents/chapters, transcribes audio.
            All artifacts are stored in a single folder named after the video.
        #>
		param([string]$Url)

		Show-Phase "PHASE 1: YouTube Processing" "Download metadata, chapters, and audio"

		# Step 1: Extract contents/index from YouTube (to get video title first)
		Show-Stage "Contents" "Extracting video chapters and contents..."

		$contentsScript = Join-Path $PSScriptRoot "src\powershell\Get-YouTubeContents.ps1"

		# Create a temporary location for initial contents extraction
		$tempInitFolder = Join-Path $PSScriptRoot "data\.temp_init"
		if (Test-Path $tempInitFolder) {
			Remove-Item $tempInitFolder -Recurse -Force
		}
		New-Item -ItemType Directory -Path $tempInitFolder -Force | Out-Null

		# Run contents extraction to get video metadata
		# Get-YouTubeContents creates a dated subfolder: <upload_date>-<title>
		$contentsResult = & $contentsScript -YouTubeUrl $Url -OutputPath $tempInitFolder

		if ($LASTEXITCODE -ne 0) {
			Remove-Item $tempInitFolder -Recurse -Force -ErrorAction SilentlyContinue
			throw "Failed to extract video contents"
		}

		# Get the created output folder (dated subfolder)
		$contentsOutputFolder = $contentsResult.OutputPath
		$contentsJsonPath = $contentsResult.JsonPath

		# Get video title and upload date from contents
		$contentsJson = Get-Content $contentsJsonPath | ConvertFrom-Json
		$videoTitle = $contentsJson.title -replace '[\\/:*?"<>|]', '_' -replace '\s+', '_'
		$uploadDate = $contentsResult.UploadDate

		# Format upload date for folder name (YYYYMMDD -> YYYY-MM-DD)
		$formattedDate = if ($uploadDate -match '^(\d{4})(\d{2})(\d{2})$') {
			"$($Matches[1])-$($Matches[2])-$($Matches[3])"
		}
		else {
			$uploadDate
		}

		# Create the final data folder named with date and video title
		$dataFolderName = "$formattedDate-$videoTitle"
		$dataFolder = Join-Path $PSScriptRoot "data\$dataFolderName"
		if (Test-Path $dataFolder) {
			Write-Host "  Removing existing data folder..." -ForegroundColor DarkGray
			Remove-Item $dataFolder -Recurse -Force
		}

		# Move the entire dated folder to final location
		Move-Item $contentsOutputFolder $dataFolder -Force
		Remove-Item $tempInitFolder -Recurse -Force -ErrorAction SilentlyContinue

		$indexPath = Join-Path $dataFolder "contents.md"
		Write-Host "✓ " -ForegroundColor Green -NoNewline
		Write-Host "Contents extracted: $indexPath"

		# Step 2: Transcribe the video (directly to final data folder)
		Show-Phase "PHASE 2: Audio Transcription" "Download, optimize, and transcribe audio"
		Show-Stage "Transcribe" "Starting audio transcription..."

		$transcribeScript = Join-Path $PSScriptRoot "src\powershell\Invoke-YouTubeTranscription.ps1"

		$transcribeParams = @{
			YouTubeUrl = $Url
			OutputPath = $dataFolder
			Language   = $Language
			FlatOutput = $true
		}

		if ($KeepIntermediateFiles) {
			$transcribeParams['KeepIntermediateFiles'] = $true
		}

		# Run transcription script - pipe to Out-Null to prevent output pollution
		& $transcribeScript @transcribeParams | Out-Null

		if ($LASTEXITCODE -ne 0) {
			throw "Failed to transcribe video"
		}

		# Transcript file should be directly in the data folder now
		$transcriptFile = Join-Path $dataFolder "transcript.srt"
		if (-not (Test-Path $transcriptFile)) {
			throw "Transcript file not found at: $transcriptFile"
		}

		Write-Host "✓ " -ForegroundColor Green -NoNewline
		Write-Host "Transcription complete: $transcriptFile"

		return @{
			IndexPath      = $indexPath
			TranscriptPath = $transcriptFile
			VideoTitle     = $videoTitle
			DataFolder     = $dataFolder
		}
	}

	function Confirm-GitHubAuth {
		<#
        .SYNOPSIS
            Verifies GitHub CLI is authenticated for API access.
        .DESCRIPTION
            Checks that the user has run 'gh auth login' and has a valid token.
            Displays the authenticated account before proceeding.
        #>
		Show-Stage "Auth" "Checking GitHub CLI status..."

		# Check if gh CLI is installed
		$ghPath = Get-Command gh -ErrorAction SilentlyContinue
		if (-not $ghPath) {
			throw "GitHub CLI (gh) not found. Install from https://cli.github.com/"
		}

		# Get authentication status with account info
		$statusOutput = gh auth status 2>&1
		if ($LASTEXITCODE -ne 0) {
			Write-Host ""
			Write-Host $statusOutput -ForegroundColor DarkGray
			Write-Host ""
			throw "GitHub CLI not authenticated. Run 'gh auth login' first."
		}

		# Extract the logged-in account from status output
		$accountLine = $statusOutput | Select-String -Pattern "Logged in to .+ account (.+)" | Select-Object -First 1
		if ($accountLine) {
			$account = $accountLine.Matches.Groups[1].Value.Trim()
			Write-Host "✓ " -ForegroundColor Green -NoNewline
			Write-Host "Authenticated as: $account"
		}
		else {
			# Fallback: just show authenticated
			Write-Host "✓ " -ForegroundColor Green -NoNewline
			Write-Host "GitHub CLI authenticated"
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

		Write-Host ""
		Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
		Write-Host "  $Phase" -ForegroundColor Yellow
		if ($Description) {
			Write-Host "  $Description" -ForegroundColor DarkGray
		}
		Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
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
		Write-Host "  VideoToNotes" -ForegroundColor Magenta
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

		# Suppress all pip output including cache cleanup messages
		# Use --no-cache-dir to prevent async cache operations that print to console
		$null = & $pipPath install -q --disable-pip-version-check --no-cache-dir -r $requirementsPath 2>&1

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
            Extracts a video title from the index file or its parent folder.
        .PARAMETER IndexPath
            Path to the index file.
        .OUTPUTS
            Cleaned video title suitable for use as a filename.
        #>
		param([string]$IndexPath)

		$parentFolder = Split-Path -Parent $IndexPath
		$folderName = Split-Path -Leaf $parentFolder

		# Check if parent folder follows the dated naming pattern (YYYY-MM-DD-Title)
		if ($folderName -match '^\d{4}-\d{2}-\d{2}-(.+)$') {
			# Return the full folder name including date
			return $folderName -replace "[^\w\s-]", "" -replace "\s+", "_"
		}

		# Try to read title from contents.json if it exists
		$contentsJsonPath = Join-Path $parentFolder "contents.json"
		if (Test-Path $contentsJsonPath) {
			try {
				$contents = Get-Content $contentsJsonPath | ConvertFrom-Json
				if ($contents.title -and $contents.uploadDate) {
					$uploadDate = $contents.uploadDate
					$formattedDate = if ($uploadDate -match '^(\d{4})(\d{2})(\d{2})$') {
						"$($Matches[1])-$($Matches[2])-$($Matches[3])"
					}
					else {
						$uploadDate
					}
					$safeTitle = $contents.title -replace '[\\/:*?"<>|]', '_' -replace '\s+', '_'
					return "$formattedDate-$safeTitle"
				}
				elseif ($contents.title) {
					return $contents.title -replace '[\\/:*?"<>|]', '_' -replace '\s+', '_'
				}
			}
			catch {
				# Fall through to filename-based extraction
			}
		}

		# Fallback: use folder name or file name
		if ($folderName -and $folderName -ne "." -and $folderName -ne "data") {
			return $folderName -replace "[^\w\s-]", "" -replace "\s+", "_"
		}

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
			"--merge-model", $MergeModel,
			"--debug"
		)

		# Add debug-dir if we have a data folder from YouTube workflow
		if ($script:DataFolder) {
			$debugDir = Join-Path $script:DataFolder "debug"
			$pythonArgs += "--debug-dir", $debugDir
		}

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
