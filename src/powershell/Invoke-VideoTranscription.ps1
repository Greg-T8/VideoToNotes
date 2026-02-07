# -------------------------------------------------------------------------
# Program: Invoke-VideoTranscription.ps1
# Description: PowerShell wrapper that extracts audio from a local video
#              file and transcribes it using Azure Speech (spx) with
#              automatic selection of fast vs batch transcription based
#              on duration.
# Context: Exam-Notes-Generator - local video to SRT workflow
# Author: Greg Tate
# -------------------------------------------------------------------------

[CmdletBinding()]
param(
	[Parameter(Mandatory = $true, Position = 0,
		HelpMessage = 'Path to a local video file (e.g. .mp4, .mkv, .webm)')]
	[ValidateScript({ Test-Path $_ -PathType Leaf })]
	[string]$VideoFile,

	[Parameter()]
	[string]$OutputPath = '.\data',

	[Parameter()]
	[string]$Language = 'en-US',

	[Parameter()]
	[switch]$ForceBatch,

	[Parameter()]
	[switch]$KeepIntermediateFiles,

	[Parameter(HelpMessage = 'Output files directly to OutputPath without creating a subfolder')]
	[switch]$FlatOutput,

	[Parameter(HelpMessage = 'Enable speaker diarization to identify different speakers')]
	[switch]$Diarization
)

$Main = {
	# Dot-source the helper functions
	. $Helpers

	# Validate required tools are installed
	Confirm-Prerequisite

	# Get video metadata from the local file
	$videoInfo = Get-VideoInfo -FilePath $VideoFile

	# Determine output folder based on FlatOutput mode
	if ($FlatOutput) {
		$outputFolder = Initialize-OutputFolder -Path $OutputPath
	}
	else {
		$outputFolder = Initialize-OutputFolder `
			-Path (Join-Path $OutputPath $videoInfo.SafeTitle)
	}

	# Extract and optimise audio for Azure Speech processing
	$optimizedAudio = Convert-VideoToSpeechAudio `
		-VideoFile $VideoFile `
		-OutputFolder $outputFolder

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
			-DurationSeconds $durationSeconds `
			-Diarization:$Diarization
	}
	else {
		$srtFile = Invoke-FastTranscription `
			-AudioFile $optimizedAudio `
			-OutputFolder $outputFolder `
			-Language $Language `
			-Diarization:$Diarization
	}

	# Clean up intermediate files if not keeping them
	if (-not $KeepIntermediateFiles) {
		Remove-IntermediateFile -Folder $outputFolder
	}

	# Show result summary
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
			@{ Name = 'ffmpeg'; InstallHint = 'winget install ffmpeg' },
			@{ Name = 'ffprobe'; InstallHint = 'Included with ffmpeg' },
			@{ Name = 'spx'; InstallHint = 'dotnet tool install --global Microsoft.CognitiveServices.Speech.CLI' }
		)

		foreach ($tool in $requiredTools) {
			if (-not (Get-Command $tool.Name -ErrorAction SilentlyContinue)) {
				throw "Required tool '$($tool.Name)' is not installed or not in PATH. Install with: $($tool.InstallHint)"
			}

			Write-Verbose "$($tool.Name) is available"
		}
	}

	function Get-VideoInfo {
		<#
		.SYNOPSIS
			Retrieves metadata about a local video file using ffprobe.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$FilePath
		)

		Write-Host 'Fetching video information...' -ForegroundColor Cyan

		# Resolve to absolute path
		$resolvedPath = (Resolve-Path $FilePath).Path
		$fileItem = Get-Item $resolvedPath

		# Get duration via ffprobe
		$durationOutput = ffprobe `
			-v error `
			-show_entries format=duration `
			-of default=noprint_wrappers=1:nokey=1 `
			$resolvedPath 2>&1

		$duration = 0
		if ($durationOutput -match '^\d+(\.\d+)?$') {
			$duration = [double]$durationOutput
		}

		# Derive a safe title from the file name (without extension)
		$baseName = [System.IO.Path]::GetFileNameWithoutExtension($fileItem.Name)
		$safeTitle = $baseName -replace '[\\/:*?"<>|()]', '_' -replace '\s+', '_'

		$info = @{
			Title     = $baseName
			SafeTitle = $safeTitle
			Duration  = $duration
			FilePath  = $resolvedPath
			SizeMB    = '{0:N1}' -f ($fileItem.Length / 1MB)
		}

		Write-Host "  Video:    $($info.Title)" -ForegroundColor White
		Write-Host "  Duration: $([timespan]::FromSeconds($info.Duration).ToString('hh\:mm\:ss'))" -ForegroundColor White
		Write-Host "  Size:     $($info.SizeMB) MB" -ForegroundColor White

		return $info
	}

	function Initialize-OutputFolder {
		<#
		.SYNOPSIS
			Ensures the output directory exists and returns the resolved path.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$Path
		)

		if (-not (Test-Path $Path)) {
			New-Item -ItemType Directory -Path $Path -Force | Out-Null
			Write-Verbose "Created output folder: $Path"
		}

		return (Resolve-Path $Path).Path
	}

	function Convert-VideoToSpeechAudio {
		<#
		.SYNOPSIS
			Extracts audio from a video file and converts it to the optimal
			format for Azure Speech processing (16 kHz mono WAV).
		#>
		param(
			[Parameter(Mandatory)]
			[string]$VideoFile,

			[Parameter(Mandatory)]
			[string]$OutputFolder
		)

		Write-Host '  [Step 1/2] ' -ForegroundColor DarkCyan -NoNewline
		Write-Host 'Extracting and optimising audio for speech recognition...' -ForegroundColor Cyan

		$outputFile = Join-Path $OutputFolder 'audio_optimized.wav'

		# Extract audio and convert to 16 kHz mono WAV in a single pass
		ffmpeg `
			-hide_banner `
			-i $VideoFile `
			-vn `
			-ar 16000 `
			-ac 1 `
			-sample_fmt s16 `
			-y `
			$outputFile 2>&1 |
			ForEach-Object {
				$line = $_.ToString()

				# Show progress and error lines only
				if ($line -match 'time=|Error|Warning') {
					Write-Host "`r  $line" -NoNewline -ForegroundColor DarkGray
				}
			}

		# Clear the progress line
		Write-Host ''

		if ($LASTEXITCODE -ne 0) {
			throw 'ffmpeg failed to extract and convert audio.'
		}

		$sizeMB = '{0:N1} MB' -f ((Get-Item $outputFile).Length / 1MB)
		Write-Host "  Optimised audio: $outputFile ($sizeMB)" -ForegroundColor Green

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
			Performs fast transcription using the spx transcribe command.
			Used for audio files under 2 hours and 300 MB.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$AudioFile,

			[Parameter(Mandatory)]
			[string]$OutputFolder,

			[Parameter()]
			[string]$Language = 'en-US',

			[Parameter()]
			[switch]$Diarization
		)

		Write-Host '  [Step 2/2] ' -ForegroundColor DarkCyan -NoNewline
		Write-Host 'Starting fast transcription...' -ForegroundColor Cyan

		$srtFile = Join-Path $OutputFolder 'transcript.srt'

		# Build spx arguments
		$spxArgs = @(
			'transcribe'
			'--file', $AudioFile
			'--language', $Language
			'--output-srt-file', $srtFile
		)

		if ($Diarization) {
			$spxArgs += '--diarization'
			Write-Verbose 'Speaker diarization enabled'
		}

		# Capture output and show only header lines (not the full transcript text)
		$spxOutput = & spx $spxArgs 2>&1

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
		Write-Host '  ...transcribing...' -ForegroundColor DarkGray

		if ($LASTEXITCODE -ne 0) {
			throw 'spx transcribe failed.'
		}

		Write-Host "  Fast transcription complete: $srtFile" -ForegroundColor Green
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
			[string]$Language = 'en-US',

			[Parameter()]
			[double]$DurationSeconds,

			[Parameter()]
			[switch]$Diarization
		)

		Write-Host '  [Step 2/2] ' -ForegroundColor DarkCyan -NoNewline
		Write-Host 'Starting batch transcription...' -ForegroundColor Cyan

		# Split into 1-hour chunks
		$chunkDurationSeconds = 3600
		$chunks = Split-AudioIntoChunk `
			-AudioFile $AudioFile `
			-OutputFolder $OutputFolder `
			-ChunkDurationSeconds $chunkDurationSeconds

		$srtFiles = @()

		foreach ($chunk in $chunks) {
			Write-Host "  Transcribing chunk: $($chunk.Name)" -ForegroundColor Yellow

			$chunkSrt = $chunk.FullName -replace '\.wav$', '.srt'

			# Build spx arguments for chunk
			$spxArgs = @(
				'transcribe'
				'--file', $chunk.FullName
				'--language', $Language
				'--output-srt-file', $chunkSrt
			)

			if ($Diarization) {
				$spxArgs += '--diarization'
			}

			# Use fast transcription for each chunk
			$null = & spx $spxArgs 2>&1

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
		$finalSrt = Join-Path $OutputFolder 'transcript.srt'
		Merge-SrtFile -SrtFiles $srtFiles -OutputFile $finalSrt

		Write-Host "  Batch transcription complete: $finalSrt" -ForegroundColor Green
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

		Write-Host '  Splitting audio into chunks...' -ForegroundColor Cyan

		$chunkFolder = Join-Path $OutputFolder 'chunks'
		if (-not (Test-Path $chunkFolder)) {
			New-Item -ItemType Directory -Path $chunkFolder -Force | Out-Null
		}

		$chunkPattern = Join-Path $chunkFolder 'chunk_%03d.wav'

		# Split audio into segments
		ffmpeg `
			-i $AudioFile `
			-f segment `
			-segment_time $ChunkDurationSeconds `
			-c copy `
			-y `
			$chunkPattern 2>&1 | Out-Null

		if ($LASTEXITCODE -ne 0) {
			throw 'ffmpeg failed to split audio into chunks.'
		}

		$chunks = Get-ChildItem -Path $chunkFolder -Filter 'chunk_*.wav' |
			Sort-Object Name

		Write-Host "  Created $($chunks.Count) audio chunks" -ForegroundColor Green
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

		Write-Host '  Merging SRT files...' -ForegroundColor Cyan

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

		Write-Host "  Merged $($subtitleIndex - 1) subtitle entries" -ForegroundColor Green
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

		return '{0:D2}:{1:D2}:{2:D2},{3:D3}' -f $hours, $minutes, $seconds, $ms
	}

	function Remove-IntermediateFile {
		<#
		.SYNOPSIS
			Removes intermediate files created during processing.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$Folder
		)

		Write-Host '  Cleaning up intermediate files...' -ForegroundColor Cyan

		# Remove optimised audio
		Get-ChildItem -Path $Folder -Filter 'audio_optimized.*' |
			Remove-Item -Force -ErrorAction SilentlyContinue

		# Remove chunks folder
		$chunksFolder = Join-Path $Folder 'chunks'
		if (Test-Path $chunksFolder) {
			Remove-Item -Path $chunksFolder -Recurse -Force -ErrorAction SilentlyContinue
		}

		Write-Verbose 'Intermediate files removed'
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
		Write-Host 'TRANSCRIPTION COMPLETE' -ForegroundColor Green
		Write-Host '========================================' -ForegroundColor Cyan
		Write-Host "Video:    $($VideoInfo.Title)"
		Write-Host "Duration: $([timespan]::FromSeconds($VideoInfo.Duration).ToString('hh\:mm\:ss'))"
		Write-Host "Output:   $SrtFile"
		Write-Host "========================================`n" -ForegroundColor Cyan
	}
}

try {
	$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
	Push-Location -Path $scriptRoot
	& $Main
}
finally {
	Pop-Location
}
