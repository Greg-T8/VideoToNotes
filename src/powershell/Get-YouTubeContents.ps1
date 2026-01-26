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
	Save-ContentsFile -Contents $contents -OutputPath $OutputPath -VideoTitle $metadata.title

	return @{
		JsonPath = (Join-Path $OutputPath "contents.json")
		MdPath   = (Join-Path $OutputPath "contents.md")
		Title    = $metadata.title
	}
}

$Helpers = {

	function Confirm-Prerequisite {
		param([string]$Command, [string]$InstallHint)

		if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
			throw "Required tool '$Command' not found. Install with: $InstallHint"
		}
	}

	function Get-VideoMetadata {
		param([string]$Url)

		Write-Host "Fetching video metadata..." -ForegroundColor Cyan

		# Get JSON metadata from yt-dlp (capture stderr separately)
		$jsonOutput = & yt-dlp `
			--dump-json `
			--no-download `
			--no-warnings `
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
		Write-Host "Parsing timestamps from description..." -ForegroundColor Cyan
		$parsedChapters = Get-ChapterFromDescription -Description $Metadata.description

		if ($parsedChapters.Count -gt 0) {
			Write-Host "Found $($parsedChapters.Count) timestamps in description" -ForegroundColor Green
			$contents.chaptersSource = "description"
			$contents.chapters = $parsedChapters
		}
		else {
			Write-Host "No timestamps found in description" -ForegroundColor Yellow
			$contents.chaptersSource = "none"
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
			if ($chapter.isSection -and $chapter.children.Count -gt 0) {
				$firstChild = $chapter.children | Sort-Object { $_.startTime } | Select-Object -First 1
				$chapter.startTime = $firstChild.startTime
				$chapter.timestamp = $firstChild.timestamp
			}
		}

		# Sort chapters by start time
		$chapters = $chapters | Where-Object { $_.startTime -ne $null } | Sort-Object { $_.startTime }

		# Sort children within each section
		foreach ($chapter in $chapters) {
			if ($chapter.children -and $chapter.children.Count -gt 0) {
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
		$allItems = $allItems | Sort-Object { $_.startTime }

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
		param($Contents, [string]$OutputPath, [string]$VideoTitle)

		# Create output directory if needed
		if (-not (Test-Path $OutputPath)) {
			New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
		}

		# Save as JSON for structured processing
		$jsonPath = Join-Path $OutputPath "contents.json"
		$Contents | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
		Write-Host "Saved: $jsonPath" -ForegroundColor Green

		# Also save a human-readable markdown outline
		$mdPath = Join-Path $OutputPath "contents.md"
		$mdContent = Convert-ContentsToMarkdown -Contents $Contents
		$mdContent | Set-Content -Path $mdPath -Encoding UTF8
		Write-Host "Saved: $mdPath" -ForegroundColor Green

		return $jsonPath
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
		if ($Contents.chapters.Count -gt 0) {
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
		if ($Chapter.children -and $Chapter.children.Count -gt 0) {
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
