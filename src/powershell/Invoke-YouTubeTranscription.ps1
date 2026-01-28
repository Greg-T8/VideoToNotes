# -------------------------------------------------------------------------
# Program: Invoke-YouTubeTranscription.ps1
# Description: PowerShell wrapper that downloads YouTube audio and
#              transcribes it using Azure Speech (spx) with automatic
#              selection of fast vs batch transcription based on duration.
# Context: Exam-Notes-Generator - YouTube to SRT workflow
# Author: Greg Tate
# -------------------------------------------------------------------------

[CmdletBinding()]
param(
	[Parameter(Mandatory = $true, Position = 0)]
	[string]$YouTubeUrl,

	[Parameter()]
	[string]$OutputPath = ".\data",

	[Parameter()]
	[string]$Language = "en-US",

	[Parameter()]
	[switch]$ForceBatch,

	[Parameter()]
	[switch]$KeepIntermediateFiles,

	[Parameter(HelpMessage = "Output files directly to OutputPath without creating a subfolder")]
	[switch]$FlatOutput
)

$Main = {
	# Dot-source the helper functions
	. $Helpers

	# Validate required tools are installed
	Confirm-Prerequisite

	# Get video metadata
	$videoInfo = Get-YouTubeVideoInfo -Url $YouTubeUrl

	# Determine output folder based on FlatOutput mode
	if ($FlatOutput) {
		# Output directly to the specified path
		$outputFolder = $OutputPath
		if (-not (Test-Path $outputFolder)) {
			New-Item -ItemType Directory -Path $outputFolder -Force | Out-Null
		}
	}
	else {
		# Create subfolder named after the video
		$outputFolder = Initialize-OutputFolder -VideoInfo $videoInfo -BasePath $OutputPath
	}

	# Download audio from YouTube
	$downloadedAudio = Get-YouTubeAudio -Url $YouTubeUrl -OutputFolder $outputFolder

	# Optimize audio for Azure Speech processing
	$optimizedAudio = Convert-AudioForSpeech -InputFile $downloadedAudio -OutputFolder $outputFolder

	# Get audio duration to determine transcription method
	$durationSeconds = Get-AudioDuration -AudioFile $optimizedAudio

	# Transcribe using appropriate method based on duration
	# Fast transcription limit: 2 hours (7200 seconds) and 300 MB
	$fileSizeMB = (Get-Item $optimizedAudio).Length / 1MB
	$useBatch = $ForceBatch -or ($durationSeconds -gt 7200) -or ($fileSizeMB -gt 300)

	if ($useBatch) {
		$srtFile = Invoke-BatchTranscription `
			-AudioFile $optimizedAudio `
			-OutputFolder $outputFolder `
			-Language $Language `
			-DurationSeconds $durationSeconds
	}
	else {
		$srtFile = Invoke-FastTranscription `
			-AudioFile $optimizedAudio `
			-OutputFolder $outputFolder `
			-Language $Language
	}

	# Clean up intermediate files if not keeping them
	if (-not $KeepIntermediateFiles) {
		Remove-IntermediateFile -Folder $outputFolder -KeepSrt $true
	}

	# Output result
	Show-TranscriptionResult -SrtFile $srtFile -VideoInfo $videoInfo

	return @{
		SrtFile      = $srtFile
		OutputFolder = $outputFolder
		VideoInfo    = $videoInfo
	}
}

$Helpers = {

	function Confirm-Prerequisite {
		<#
        .SYNOPSIS
            Validates that all required tools are installed and accessible.
        #>
		$requiredTools = @(
			@{ Name = 'yt-dlp'; Command = 'yt-dlp --version' },
			@{ Name = 'ffmpeg'; Command = 'ffmpeg -version' },
			@{ Name = 'spx'; Command = 'spx --version' }
		)

		foreach ($tool in $requiredTools) {
			try {
				$null = Invoke-Expression $tool.Command 2>&1
				Write-Verbose "$($tool.Name) is available"
			}
			catch {
				throw "Required tool '$($tool.Name)' is not installed or not in PATH."
			}
		}
	}

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

	function Get-YouTubeVideoInfo {
		<#
        .SYNOPSIS
            Retrieves metadata about a YouTube video.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$Url
		)

		Write-Host "Fetching video information..." -ForegroundColor Cyan

		# Get video metadata as JSON (suppress warnings to avoid polluting JSON)
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
		$info = $jsonString | ConvertFrom-Json

		return @{
			Id         = $info.id
			Title      = $info.title
			Duration   = $info.duration
			Channel    = $info.channel
			UploadDate = $info.upload_date
			SafeTitle  = $info.title -replace '[\\/:*?"<>|()]', '_' -replace '\s+', '_'
		}
	}

	function Initialize-OutputFolder {
		<#
        .SYNOPSIS
            Creates the output folder structure for the transcription.
        #>
		param(
			[Parameter(Mandatory)]
			[hashtable]$VideoInfo,

			[Parameter(Mandatory)]
			[string]$BasePath
		)

		# Create folder name from sanitized title
		$folderName = $VideoInfo.SafeTitle
		$outputFolder = Join-Path $BasePath $folderName

		if (-not (Test-Path $outputFolder)) {
			New-Item -ItemType Directory -Path $outputFolder -Force | Out-Null
			Write-Verbose "Created output folder: $outputFolder"
		}

		return $outputFolder
	}

	function Get-YouTubeAudio {
		<#
        .SYNOPSIS
            Downloads audio from a YouTube video using yt-dlp.
        .NOTES
            YouTube's SABR streaming blocks direct audio format downloads.
            We try audio-only formats first, then fall back to format 18
            (360p mp4 with audio) which uses progressive streaming.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$Url,

			[Parameter(Mandatory)]
			[string]$OutputFolder
		)

		Write-Host "  [Step 1/3] " -ForegroundColor DarkCyan -NoNewline
		Write-Host "Downloading audio from YouTube..." -ForegroundColor Cyan

		$outputTemplate = Join-Path $OutputFolder "source_audio.%(ext)s"

		# Try audio-only formats first, fall back to format 18 (360p with audio)
		# Format 18 uses progressive streaming which bypasses SABR restrictions
		# See: https://github.com/yt-dlp/yt-dlp/issues/12482
		# Use --progress to show single-line progress, --quiet to suppress other noise
		# Then filter to show only key status lines
		# Use browser cookies to bypass YouTube bot detection (Chrome preferred, Firefox fallback)
		$browser = Get-BrowserCookiesArg
		$ytOutput = yt-dlp `
			--cookies-from-browser $browser `
			-f "140/251/bestaudio/18" `
			--extract-audio `
			--audio-format wav `
			--output $outputTemplate `
			--no-playlist `
			--newline `
			$Url 2>&1

		# Filter and display only important lines (skip repetitive download progress)
		$ytOutput | ForEach-Object {
			$line = $_.ToString()
			# Show: 100% complete, destination, extraction, deletion, errors/warnings
			if ($line -match '100%|Destination:|ExtractAudio|Deleting|ERROR|WARNING|FixupM4a') {
				Write-Host $line
			}
		}

		if ($LASTEXITCODE -ne 0) {
			throw "yt-dlp failed to download audio."
		}

		# Find the downloaded file
		$audioFile = Get-ChildItem -Path $OutputFolder -Filter "source_audio.*" |
		Select-Object -First 1

		if (-not $audioFile) {
			throw "Audio file not found after download."
		}

		$audioPath = $audioFile.FullName
		Write-Host "Downloaded: $($audioFile.Name)" -ForegroundColor Green
		return $audioPath
	}

	function Convert-AudioForSpeech {
		<#
        .SYNOPSIS
            Converts audio to optimal format for Azure Speech processing.
            Azure Speech works best with 16kHz mono WAV.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$InputFile,

			[Parameter(Mandatory)]
			[string]$OutputFolder
		)

		Write-Host "  [Step 2/3] " -ForegroundColor DarkCyan -NoNewline
		Write-Host "Optimizing audio for speech recognition..." -ForegroundColor Cyan

		$outputFile = Join-Path $OutputFolder "audio_optimized.wav"

		# Convert to 16kHz mono WAV
		ffmpeg `
			-i $InputFile `
			-ar 16000 `
			-ac 1 `
			-sample_fmt s16 `
			-y `
			$outputFile 2>&1 | Out-Null

		if ($LASTEXITCODE -ne 0) {
			throw "ffmpeg failed to convert audio."
		}

		Write-Host "Optimized audio: $outputFile" -ForegroundColor Green
		return $outputFile
	}

	function Get-AudioDuration {
		<#
        .SYNOPSIS
            Gets the duration of an audio file in seconds using ffprobe.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$AudioFile
		)

		$durationOutput = ffprobe `
			-v error `
			-show_entries format=duration `
			-of default=noprint_wrappers=1:nokey=1 `
			$AudioFile 2>&1

		$duration = [double]$durationOutput
		Write-Verbose "Audio duration: $duration seconds"

		return $duration
	}

	function Invoke-FastTranscription {
		<#
        .SYNOPSIS
            Performs fast transcription using spx transcribe command.
            Used for audio files under 2 hours and 300 MB.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$AudioFile,

			[Parameter(Mandatory)]
			[string]$OutputFolder,

			[Parameter()]
			[string]$Language = "en-US"
		)

		Write-Host "  [Step 3/3] " -ForegroundColor DarkCyan -NoNewline
		Write-Host "Starting fast transcription..." -ForegroundColor Cyan

		$srtFile = Join-Path $OutputFolder "transcript.srt"

		# Capture output and show only header lines (not the full transcript text)
		$spxOutput = spx transcribe `
			--file $AudioFile `
			--language $Language `
			--output-srt-file $srtFile 2>&1

		# Display only the SPX header/config lines, not the transcript content
		$headerLines = 0
		$maxHeaderLines = 12
		$spxOutput | ForEach-Object {
			$line = $_.ToString()
			# Show SPX banner, config lines (indented with spaces), and stop after header
			if ($line -match '^SPX|^Copyright|^\s{2}\w+\.' -and $headerLines -lt $maxHeaderLines) {
				Write-Host $line
				$headerLines++
			}
		}
		Write-Host "  ...transcribing..." -ForegroundColor DarkGray

		if ($LASTEXITCODE -ne 0) {
			throw "spx transcribe failed."
		}

		Write-Host "Fast transcription complete: $srtFile" -ForegroundColor Green
		return $srtFile
	}

	function Invoke-BatchTranscription {
		<#
        .SYNOPSIS
            Performs batch transcription for long audio files.
            Splits audio into chunks if necessary and merges results.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$AudioFile,

			[Parameter(Mandatory)]
			[string]$OutputFolder,

			[Parameter()]
			[string]$Language = "en-US",

			[Parameter()]
			[double]$DurationSeconds
		)

		Write-Host "  [Step 3/3] " -ForegroundColor DarkCyan -NoNewline
		Write-Host "Starting batch transcription..." -ForegroundColor Cyan

		# Split into 1-hour chunks
		$chunkDurationSeconds = 3600
		$chunks = Split-AudioIntoChunk `
			-AudioFile $AudioFile `
			-OutputFolder $OutputFolder `
			-ChunkDurationSeconds $chunkDurationSeconds

		$srtFiles = @()

		foreach ($chunk in $chunks) {
			Write-Host "Transcribing chunk: $($chunk.Name)" -ForegroundColor Yellow

			$chunkSrt = $chunk.FullName -replace '\.wav$', '.srt'

			# Use fast transcription for each chunk (suppress output to avoid polluting return value)
			$null = spx transcribe `
				--file $chunk.FullName `
				--language $Language `
				--output-srt-file $chunkSrt 2>&1

			if ($LASTEXITCODE -ne 0) {
				throw "Transcription failed for chunk: $($chunk.Name). Exit code: $LASTEXITCODE"
			}

			# Verify the SRT file was actually created
			if (-not (Test-Path $chunkSrt)) {
				throw "SRT file was not created for chunk: $($chunk.Name). File expected at: $chunkSrt"
			}

			$srtFiles += @{
				File       = $chunkSrt
				ChunkIndex = [int]($chunk.Name -replace '\D', '')
				OffsetMs   = [int]($chunk.Name -replace '\D', '') * $chunkDurationSeconds * 1000
			}
		}

		# Merge all SRT files into one
		$finalSrt = Join-Path $OutputFolder "transcript.srt"
		Merge-SrtFile -SrtFiles $srtFiles -OutputFile $finalSrt

		Write-Host "Batch transcription complete: $finalSrt" -ForegroundColor Green
		return $finalSrt
	}

	function Split-AudioIntoChunk {
		<#
        .SYNOPSIS
            Splits a long audio file into smaller chunks using ffmpeg.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$AudioFile,

			[Parameter(Mandatory)]
			[string]$OutputFolder,

			[Parameter()]
			[int]$ChunkDurationSeconds = 3600
		)

		Write-Host "Splitting audio into chunks..." -ForegroundColor Cyan

		$chunkFolder = Join-Path $OutputFolder "chunks"
		if (-not (Test-Path $chunkFolder)) {
			New-Item -ItemType Directory -Path $chunkFolder -Force | Out-Null
		}

		$chunkPattern = Join-Path $chunkFolder "chunk_%03d.wav"

		# Split audio into segments
		ffmpeg `
			-i $AudioFile `
			-f segment `
			-segment_time $ChunkDurationSeconds `
			-c copy `
			-y `
			$chunkPattern 2>&1 | Out-Null

		if ($LASTEXITCODE -ne 0) {
			throw "ffmpeg failed to split audio into chunks."
		}

		$chunks = Get-ChildItem -Path $chunkFolder -Filter "chunk_*.wav" |
		Sort-Object Name

		Write-Host "Created $($chunks.Count) audio chunks" -ForegroundColor Green
		return $chunks
	}

	function Merge-SrtFile {
		<#
        .SYNOPSIS
            Merges multiple SRT files into a single file with adjusted timestamps.
        #>
		param(
			[Parameter(Mandatory)]
			[array]$SrtFiles,

			[Parameter(Mandatory)]
			[string]$OutputFile
		)

		Write-Host "Merging SRT files..." -ForegroundColor Cyan

		$subtitleIndex = 1
		$mergedContent = @()

		# Sort by chunk index
		$sortedFiles = $SrtFiles | Sort-Object { $_.ChunkIndex }

		foreach ($srtInfo in $sortedFiles) {
			if (-not (Test-Path $srtInfo.File)) {
				throw "SRT file not found during merge: $($srtInfo.File). Batch transcription is incomplete."
			}

			$content = Get-Content $srtInfo.File -Raw
			$blocks = $content -split '\r?\n\r?\n' | Where-Object { $_.Trim() }

			foreach ($block in $blocks) {
				$lines = $block -split '\r?\n'

				if ($lines.Count -ge 3) {
					# Parse timestamp line
					if ($lines[1] -match '^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$') {
						$startTime = Convert-SrtTimestampToMillisecond -Timestamp $Matches[1]
						$endTime = Convert-SrtTimestampToMillisecond -Timestamp $Matches[2]

						# Add offset for this chunk
						$adjustedStart = $startTime + $srtInfo.OffsetMs
						$adjustedEnd = $endTime + $srtInfo.OffsetMs

						$newTimestamp = "$(Convert-MillisecondToSrtTimestamp -Milliseconds $adjustedStart) --> $(Convert-MillisecondToSrtTimestamp -Milliseconds $adjustedEnd)"

						# Build new subtitle block
						$textLines = $lines[2..($lines.Count - 1)] -join "`n"
						$mergedContent += "$subtitleIndex`n$newTimestamp`n$textLines"
						$subtitleIndex++
					}
				}
			}
		}

		# Write merged content
		$mergedContent -join "`n`n" | Set-Content -Path $OutputFile -Encoding UTF8

		Write-Host "Merged $($subtitleIndex - 1) subtitle entries" -ForegroundColor Green
	}

	function Convert-SrtTimestampToMillisecond {
		<#
        .SYNOPSIS
            Converts SRT timestamp format to milliseconds.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$Timestamp
		)

		if ($Timestamp -match '^(\d{2}):(\d{2}):(\d{2}),(\d{3})$') {
			$hours = [int]$Matches[1]
			$minutes = [int]$Matches[2]
			$seconds = [int]$Matches[3]
			$milliseconds = [int]$Matches[4]

			return ($hours * 3600000) + ($minutes * 60000) + ($seconds * 1000) + $milliseconds
		}

		return 0
	}

	function Convert-MillisecondToSrtTimestamp {
		<#
        .SYNOPSIS
            Converts milliseconds to SRT timestamp format.
        #>
		param(
			[Parameter(Mandatory)]
			[long]$Milliseconds
		)

		# Cast to integers to ensure format specifier works correctly
		$hours = [int][math]::Floor($Milliseconds / 3600000)
		$remaining = $Milliseconds % 3600000
		$minutes = [int][math]::Floor($remaining / 60000)
		$remaining = $remaining % 60000
		$seconds = [int][math]::Floor($remaining / 1000)
		$ms = [int]($remaining % 1000)

		return "{0:D2}:{1:D2}:{2:D2},{3:D3}" -f $hours, $minutes, $seconds, $ms
	}

	function Remove-IntermediateFile {
		<#
        .SYNOPSIS
            Removes intermediate files created during processing.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$Folder,

			[Parameter()]
			[bool]$KeepSrt = $true
		)

		Write-Host "Cleaning up intermediate files..." -ForegroundColor Cyan

		# Remove source audio
		Get-ChildItem -Path $Folder -Filter "source_audio.*" | Remove-Item -Force -ErrorAction SilentlyContinue

		# Remove optimized audio
		Get-ChildItem -Path $Folder -Filter "audio_optimized.*" | Remove-Item -Force -ErrorAction SilentlyContinue

		# Remove chunks folder
		$chunksFolder = Join-Path $Folder "chunks"
		if (Test-Path $chunksFolder) {
			Remove-Item -Path $chunksFolder -Recurse -Force -ErrorAction SilentlyContinue
		}

		Write-Verbose "Intermediate files removed"
	}

	function Show-TranscriptionResult {
		<#
        .SYNOPSIS
            Displays the final transcription result to the user.
        #>
		param(
			[Parameter(Mandatory)]
			[string]$SrtFile,

			[Parameter(Mandatory)]
			[hashtable]$VideoInfo
		)

		Write-Host "`n========================================" -ForegroundColor Cyan
		Write-Host "TRANSCRIPTION COMPLETE" -ForegroundColor Green
		Write-Host "========================================" -ForegroundColor Cyan
		Write-Host "Video:    $($VideoInfo.Title)"
		Write-Host "Channel:  $($VideoInfo.Channel)"
		Write-Host "Duration: $([timespan]::FromSeconds($VideoInfo.Duration).ToString('hh\:mm\:ss'))"
		Write-Host "Output:   $SrtFile"
		Write-Host "========================================`n" -ForegroundColor Cyan

		return $SrtFile
	}
}

try {
	Push-Location -Path $PSScriptRoot
	& $Main
}
finally {
	Pop-Location
}
