# -------------------------------------------------------------------------
# Program: Get-YouTubeContents.ps1
# Description: Extract video chapters and description contents from YouTube
# Context: Exam-Notes-Generator - extracts structured table of contents for note generation
# Author: Greg Tate
# -------------------------------------------------------------------------

[CmdletBinding()]
param(
	[Parameter(Mandatory = $true)]
	[string]$YouTubeUrl,

	[Parameter(Mandatory = $false)]
	[string]$OutputPath = "."
)

$Main = {
	# Dot-source the helper functions
	. $Helpers

	# Confirm prerequisites
	Confirm-Prerequisite -Command "yt-dlp" -InstallHint "winget install yt-dlp"

	# Get video metadata
	$metadata = Get-VideoMetadata -Url $YouTubeUrl

	# Extract contents structure
	$contents = Build-ContentsStructure -Metadata $metadata

	# Save output
	$result = Save-ContentsFile -Contents $contents -OutputPath $OutputPath -VideoTitle $metadata.title -UploadDate $metadata.upload_date

	return @{
		JsonPath   = $result.JsonPath
		MdPath     = $result.MdPath
		OutputPath = $result.OutputPath
		Title      = $metadata.title
		UploadDate = $metadata.upload_date
	}
}

$Helpers = {

	# Script-level cache for browser cookies argument
	$script:BrowserCookiesArg = $null

	function Get-BrowserCookiesArg {
		<#
		.SYNOPSIS
			Determines which browser to use for cookies (Chrome first, then Firefox fallback).
		#>
		if ($script:BrowserCookiesArg) {
			return $script:BrowserCookiesArg
		}

		# Try Chrome first
		$null = & yt-dlp --cookies-from-browser chrome --simulate --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 2>&1
		if ($LASTEXITCODE -eq 0) {
			$script:BrowserCookiesArg = "chrome"
			Write-Verbose "Using Chrome for YouTube cookies"
			return $script:BrowserCookiesArg
		}

		# Fall back to Firefox
		$script:BrowserCookiesArg = "firefox"
		Write-Verbose "Using Firefox for YouTube cookies (Chrome failed)"
		return $script:BrowserCookiesArg
	}

	function Confirm-Prerequisite {
		param([string]$Command, [string]$InstallHint)

		if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
			throw "Required tool '$Command' not found. Install with: $InstallHint"
		}
	}

	function Get-VideoMetadata {
		param([string]$Url)

		Write-Host "  [Step 1/2] " -ForegroundColor DarkCyan -NoNewline
		Write-Host "Fetching video metadata..." -ForegroundColor Cyan

		# Get JSON metadata from yt-dlp (capture stderr separately)
		# Use browser cookies to bypass YouTube bot detection (Chrome preferred, Firefox fallback)
		# Use --no-playlist to ensure only the single video is processed (not entire playlist)
		$browser = Get-BrowserCookiesArg
		$jsonOutput = & yt-dlp `
			--cookies-from-browser $browser `
			--dump-json `
			--no-download `
			--no-warnings `
			--no-playlist `
			$Url

		if ($LASTEXITCODE -ne 0) {
			throw "Failed to fetch video metadata. Exit code: $LASTEXITCODE"
		}

		# Join output lines if array and parse JSON
		$jsonString = if ($jsonOutput -is [array]) { $jsonOutput -join "`n" } else { $jsonOutput }
		$metadata = $jsonString | ConvertFrom-Json

		Write-Host "  Title: $($metadata.title)" -ForegroundColor Green
		Write-Host "  Duration: $(Format-Duration -Seconds $metadata.duration)" -ForegroundColor Green

		return $metadata
	}

	function Format-Duration {
		param([int]$Seconds)

		$ts = [TimeSpan]::FromSeconds($Seconds)
		if ($ts.Hours -gt 0) {
			return "{0}:{1:D2}:{2:D2}" -f $ts.Hours, $ts.Minutes, $ts.Seconds
		}
		return "{0}:{1:D2}" -f $ts.Minutes, $ts.Seconds
	}

	function ConvertTo-SafeFileName {
		<#
		.SYNOPSIS
			Converts a string to a safe file/folder name by removing invalid characters.
			Also removes parentheses which cause issues with SPX CLI.
		#>
		param([string]$Name)

		# Replace invalid file name characters with underscores
		$invalidChars = [System.IO.Path]::GetInvalidFileNameChars() -join ''
		$safeName = $Name -replace "[$([regex]::Escape($invalidChars))]", '_'

		# Also replace parentheses (cause issues with SPX CLI transcription)
		$safeName = $safeName -replace '[()]', '_'

		# Replace multiple underscores/spaces with single underscore
		$safeName = $safeName -replace '[\s_]+', '_'

		# Trim underscores from ends
		$safeName = $safeName.Trim('_')

		return $safeName
	}

	function Build-ContentsStructure {
		param($Metadata)

		$contents = @{
			title       = $Metadata.title
			channel     = $Metadata.channel
			duration    = $Metadata.duration
			url         = $Metadata.webpage_url
			uploadDate  = $Metadata.upload_date
			chapters    = @()
			description = $Metadata.description
		}

		# Always parse chapters from description to capture full detail
		Write-Host "  [Step 2/2] " -ForegroundColor DarkCyan -NoNewline
		Write-Host "Parsing timestamps from description..." -ForegroundColor Cyan
		$parsedChapters = @(Get-ChapterFromDescription -Description $Metadata.description)

		if ($parsedChapters.Count -gt 0) {
			Write-Host "Found $($parsedChapters.Count) timestamps in description" -ForegroundColor Green
			$contents.chaptersSource = "description"
			$contents.chapters = $parsedChapters
		}
		else {
			Write-Host "No timestamps found in description" -ForegroundColor Yellow
			$contents.chaptersSource = "none"
			$contents.chapters = @()
		}

		return $contents
	}

	function Format-Timestamp {
		param([int]$Seconds)

		$ts = [TimeSpan]::FromSeconds($Seconds)
		if ($ts.Hours -gt 0) {
			return "{0}:{1:D2}:{2:D2}" -f $ts.Hours, $ts.Minutes, $ts.Seconds
		}
		return "{0}:{1:D2}" -f $ts.Minutes, $ts.Seconds
	}

	function Remove-Emoji {
		param([string]$Text)

		# Remove emojis, symbols, and variation selectors
		$cleaned = $Text -replace '[\p{So}\p{Cs}\p{Cf}\p{Sk}\u2700-\u27BF\u2600-\u26FF\uFE00-\uFE0F]', ''

		# Clean up extra whitespace
		$cleaned = $cleaned -replace '\s+', ' '
		return $cleaned.Trim()
	}

	function Get-ChapterFromDescription {
		param([string]$Description)

		if ([string]::IsNullOrWhiteSpace($Description)) {
			return @()
		}

		$chapters = @()
		$lines = $Description -split "`n"

		# Regex patterns for timestamps
		$timestampPattern = '(?<timestamp>(?:\d{1,2}:)?\d{1,2}:\d{2})'

		# Pattern: timestamp at start
		$startPattern = "^[\s]*\(?$timestampPattern\)?[\s]*[-–—:\s]+[\s]*(?<title>.+)"

		# Pattern: emoji/bullet + parenthesized timestamp + title
		$emojiPattern = "^[\s]*[^\d\s]*[\s]*\(?\s*$timestampPattern\s*\)?[\s]*(?<title>.+)"

		# Pattern: title followed by timestamp
		$endPattern = "^[\s]*(?<title>.+?)[\s]*[-–—:\s]+[\s]*\(?$timestampPattern\)?[\s]*$"

		# Track section headings
		$currentSection = $null
		$lastLineWasEmpty = $false

		foreach ($line in $lines) {
			# Track empty lines
			if ([string]::IsNullOrWhiteSpace($line)) {
				$lastLineWasEmpty = $true
				continue
			}

			$trimmedLine = $line.Trim()
			$timestamp = $null
			$title = $null

			# Try matching timestamp at start
			if ($trimmedLine -match $startPattern) {
				$timestamp = $Matches['timestamp']
				$title = $Matches['title'].Trim()
			}
			# Try matching emoji + parenthesized timestamp pattern
			elseif ($trimmedLine -match $emojiPattern) {
				$timestamp = $Matches['timestamp']
				$title = $Matches['title'].Trim()
			}
			# Try matching timestamp at end
			elseif ($trimmedLine -match $endPattern) {
				$timestamp = $Matches['timestamp']
				$title = $Matches['title'].Trim()
			}

			if ($timestamp -and $title) {
				# This is a timestamped entry
				$title = $title -replace '^[\-\*•]\s*', ''
				$title = $title -replace '^\d+\.\s*', ''
				$title = Remove-Emoji -Text $title
				$title = $title.Trim()

				$seconds = Convert-TimestampToSecond -Timestamp $timestamp

				$chapterEntry = @{
					title     = $title
					startTime = $seconds
					timestamp = $timestamp
					level     = if ($currentSection) { 2 } else { 1 }
					children  = @()
					isSection = $false
				}

				if ($currentSection) {
					$currentSection.children += $chapterEntry
				}
				else {
					$chapters += $chapterEntry
				}

				$lastLineWasEmpty = $false
			}
			else {
				# No timestamp - check if it's a section heading
				$isLikelyHeading = (
					$lastLineWasEmpty -and
					$trimmedLine.Length -gt 0 -and
					$trimmedLine.Length -lt 50 -and
					$trimmedLine -notmatch '^https?://' -and
					$trimmedLine -notmatch '^\S+@\S+' -and
					$trimmedLine -notmatch '\.\s' -and
					$trimmedLine -match '^[A-Z⭐🔗✏️☁️►]'
				)

				if ($isLikelyHeading) {
					# New section heading
					$sectionTitle = Remove-Emoji -Text $trimmedLine
					$currentSection = @{
						title     = $sectionTitle
						startTime = $null
						timestamp = $null
						level     = 1
						children  = @()
						isSection = $true
					}
					$chapters += $currentSection
				}

				$lastLineWasEmpty = $false
			}
		}

		# Post-process: set section start times from first child
		foreach ($chapter in $chapters) {
			if ($chapter.isSection -and $chapter.children -and @($chapter.children).Count -gt 0) {
				$firstChild = $chapter.children | Sort-Object { $_.startTime } | Select-Object -First 1
				$chapter.startTime = $firstChild.startTime
				$chapter.timestamp = $firstChild.timestamp
			}
		}

		# Sort chapters by start time
		$chapters = $chapters | Where-Object { $_.startTime -ne $null } | Sort-Object { $_.startTime }

		# Sort children within each section
		foreach ($chapter in $chapters) {
			if ($chapter.children -and @($chapter.children).Count -gt 0) {
				$chapter.children = $chapter.children | Sort-Object { $_.startTime }
			}
		}

		# Calculate end times
		$allItems = @()
		foreach ($chapter in $chapters) {
			$allItems += $chapter
			if ($chapter.children) {
				$allItems += $chapter.children
			}
		}
		$allItems = @($allItems | Sort-Object { $_.startTime })

		for ($i = 0; $i -lt $allItems.Count; $i++) {
			if ($i -lt $allItems.Count - 1) {
				$allItems[$i].endTime = $allItems[$i + 1].startTime
			}
			else {
				$allItems[$i].endTime = $null
			}
		}

		return $chapters
	}

	function Convert-TimestampToSecond {
		param([string]$Timestamp)

		$parts = $Timestamp -split ':'
		$seconds = 0

		if ($parts.Count -eq 3) {
			$seconds = [int]$parts[0] * 3600 + [int]$parts[1] * 60 + [int]$parts[2]
		}
		elseif ($parts.Count -eq 2) {
			$seconds = [int]$parts[0] * 60 + [int]$parts[1]
		}

		return $seconds
	}

	function Save-ContentsFile {
		param($Contents, [string]$OutputPath, [string]$VideoTitle, [string]$UploadDate)

		# Format upload date for folder name (YYYYMMDD -> YYYY-MM-DD)
		$formattedDate = if ($UploadDate -match '^(\d{4})(\d{2})(\d{2})$') {
			"$($Matches[1])-$($Matches[2])-$($Matches[3])"
		}
		else {
			$UploadDate
		}

		# Create dated output folder name
		$datedFolderName = "$formattedDate-$(ConvertTo-SafeFileName -Name $VideoTitle)"
		$datedOutputPath = Join-Path $OutputPath $datedFolderName

		# Create output directory if needed
		if (-not (Test-Path $datedOutputPath)) {
			New-Item -ItemType Directory -Path $datedOutputPath -Force | Out-Null
		}

		# Save as JSON for structured processing
		$jsonPath = Join-Path $datedOutputPath "contents.json"
		$Contents | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
		Write-Host "Saved: $jsonPath" -ForegroundColor Green

		# Also save a human-readable markdown outline
		$mdPath = Join-Path $datedOutputPath "contents.md"
		$mdContent = Convert-ContentsToMarkdown -Contents $Contents
		$mdContent | Set-Content -Path $mdPath -Encoding UTF8
		Write-Host "Saved: $mdPath" -ForegroundColor Green

		return @{
			JsonPath   = $jsonPath
			MdPath     = $mdPath
			OutputPath = $datedOutputPath
		}
	}

	function Convert-ContentsToMarkdown {
		param($Contents)

		$sb = [System.Text.StringBuilder]::new()

		# Header
		[void]$sb.AppendLine("# $($Contents.title)")
		[void]$sb.AppendLine()
		[void]$sb.AppendLine("**Channel:** $($Contents.channel)")
		[void]$sb.AppendLine("**Duration:** $(Format-Duration -Seconds $Contents.duration)")
		[void]$sb.AppendLine("**URL:** $($Contents.url)")
		[void]$sb.AppendLine()

		# Table of Contents
		if ($Contents.chapters -and @($Contents.chapters).Count -gt 0) {
			[void]$sb.AppendLine("## Table of Contents")
			[void]$sb.AppendLine()
			[void]$sb.AppendLine("*Source: $($Contents.chaptersSource)*")
			[void]$sb.AppendLine()

			foreach ($chapter in $Contents.chapters) {
				Write-ChapterMarkdown -StringBuilder $sb -Chapter $chapter -Indent 0
			}
		}
		else {
			[void]$sb.AppendLine("*No chapters or timestamps found*")
		}

		return $sb.ToString()
	}

	function Write-ChapterMarkdown {
		param(
			[System.Text.StringBuilder]$StringBuilder,
			$Chapter,
			[int]$Indent
		)

		$prefix = "  " * $Indent
		$bullet = "-"

		[void]$StringBuilder.AppendLine("$prefix$bullet **[$($Chapter.timestamp)]** $($Chapter.title)")

		# Write children
		if ($Chapter.children -and @($Chapter.children).Count -gt 0) {
			foreach ($child in $Chapter.children) {
				Write-ChapterMarkdown -StringBuilder $StringBuilder -Chapter $child -Indent ($Indent + 1)
			}
		}
	}
}

# Execute main and return result
try {
	Push-Location -Path $PSScriptRoot
	& $Main
}
catch {
	Write-Error $_.Exception.Message
	exit 1
}
finally {
	Pop-Location
}
