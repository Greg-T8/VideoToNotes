# -------------------------------------------------------------------------
# Program: Save-StreamVideo.ps1
# Description: Download a video stream manifest (e.g. .mpd, .m3u8) and
#              produce a local video file using ffmpeg.
# Context: Exam-Notes-Generator - stream capture for non-YouTube sources
# Author: Greg Tate
# -------------------------------------------------------------------------

[CmdletBinding()]
param(
	[Parameter(Mandatory = $true, Position = 0,
		HelpMessage = 'URL to the video stream manifest (e.g. .mpd or .m3u8)')]
	[string]$ManifestUrl,

	[Parameter()]
	[string]$OutputPath = '.\staging',

	[Parameter(HelpMessage = 'Base name for the output file (without extension)')]
	[string]$FileName,

	[Parameter(HelpMessage = 'Output container format')]
	[ValidateSet('mp4', 'mkv', 'webm')]
	[string]$Format = 'mp4',

	[Parameter(HelpMessage = 'Use progressive/fragmented MP4 format for better streaming compatibility')]
	[switch]$Progressive,

	[Parameter(HelpMessage = 'Output as DASH package with encoding (creates directory with manifest and segments)')]
	[switch]$OutputDash,

	[Parameter(HelpMessage = 'Resume an incomplete DASH encoding from where it left off')]
	[switch]$Resume,

	[Parameter(HelpMessage = 'Optional HTTP headers passed to ffmpeg (e.g. Referer, User-Agent)')]
	[hashtable]$Headers,

	[Parameter(HelpMessage = 'Additional ffmpeg input arguments (applied before -i)')]
	[string[]]$ExtraInputArgs,

	[Parameter(HelpMessage = 'Additional ffmpeg output arguments (applied after -i)')]
	[string[]]$ExtraOutputArgs
)

$Main = {
	# Dot-source the helper functions
	. $Helpers

	# Validate ffmpeg is installed
	Confirm-Prerequisite

	# Ensure the output directory exists
	$resolvedOutput = Initialize-OutputFolder -Path $OutputPath

	# Determine the output file or directory path
	$outputFile = New-OutputFilePath `
		-OutputFolder $resolvedOutput `
		-ManifestUrl $ManifestUrl `
		-FileName $FileName `
		-Format $Format `
		-OutputDash:$OutputDash `
		-Resume:$Resume

	# Calculate resume offset when recovering from incomplete DASH encoding
	$resumeInfo = if ($OutputDash -and $Resume) {
		Get-ResumeOffset -ManifestPath $outputFile
	}
	else {
		$null
	}

	# Build the ffmpeg argument list
	$ffmpegArgs = Build-FfmpegArgument `
		-ManifestUrl $ManifestUrl `
		-OutputFile $outputFile `
		-Headers $Headers `
		-Progressive:$Progressive `
		-OutputDash:$OutputDash `
		-ResumeInfo $resumeInfo `
		-ExtraInputArgs $ExtraInputArgs `
		-ExtraOutputArgs $ExtraOutputArgs

	# Execute ffmpeg to download and mux the stream
	$workingDir = if ($OutputDash) { Split-Path $outputFile -Parent } else { $null }
	Invoke-Ffmpeg -Arguments $ffmpegArgs -WorkingDirectory $workingDir

	# Show result summary
	Show-Result -OutputFile $outputFile

	return @{
		OutputFile = $outputFile
	}
}

$Helpers = {

	function Confirm-Prerequisite {
		<#
		.SYNOPSIS
			Validates that ffmpeg is installed and accessible on the PATH.
		#>
		if (-not (Get-Command 'ffmpeg' -ErrorAction SilentlyContinue)) {
			throw "Required tool 'ffmpeg' is not installed or not in PATH. Install with: winget install ffmpeg"
		}

		Write-Verbose 'ffmpeg is available'
	}

	function Get-ResumeOffset {
		<#
		.SYNOPSIS
			Calculates the time offset to resume encoding from existing DASH segments.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$ManifestPath
		)

		$dashDir = Split-Path $ManifestPath -Parent

		if (-not (Test-Path $dashDir)) {
			return $null
		}

		# Find all video segment files (stream0 is typically video)
		$segments = Get-ChildItem -Path $dashDir -Filter 'chunk-stream0-*.m4s' -ErrorAction SilentlyContinue

		if (-not $segments -or $segments.Count -eq 0) {
			Write-Verbose 'No existing segments found, starting from beginning'
			return $null
		}

		# Extract segment numbers and find the highest
		$segmentNumbers = $segments | ForEach-Object {
			if ($_.Name -match 'chunk-stream0-(\d+)\.m4s') {
				[int]$matches[1]
			}
		} | Where-Object { $_ -ne $null }

		$lastSegment = ($segmentNumbers | Measure-Object -Maximum).Maximum
		$segmentCount = $segmentNumbers.Count

		# Each segment is 6 seconds (default seg_duration)
		$segmentDuration = 6
		$resumeSeconds = $segmentCount * $segmentDuration

		Write-Host "  Found $segmentCount existing segments (last: $lastSegment)" -ForegroundColor Yellow
		Write-Host "  Resuming from $resumeSeconds seconds..." -ForegroundColor Yellow

		return @{
			StartTime     = $resumeSeconds
			StartSegment  = $lastSegment + 1
			SegmentCount  = $segmentCount
		}
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

	function New-OutputFilePath {
		<#
		.SYNOPSIS
			Determines the full path for the output video file or DASH directory.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$OutputFolder,

			[Parameter(Mandatory)]
			[string]$ManifestUrl,

			[string]$FileName,

			[Parameter(Mandatory)]
			[string]$Format,

			[switch]$OutputDash,

			[switch]$Resume
		)

		# Derive a file name from the manifest URL if none provided
		if (-not $FileName) {
			$uri = [System.Uri]::new($ManifestUrl)
			$baseName = [System.IO.Path]::GetFileNameWithoutExtension($uri.Segments[-1])

			# Fall back to a timestamp-based name when the URL path is not descriptive
			if ([string]::IsNullOrWhiteSpace($baseName) -or $baseName -eq 'manifest') {
				$baseName = 'stream_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
			}

			# Sanitise invalid filename characters
			$invalidChars = [System.IO.Path]::GetInvalidFileNameChars() -join ''
			$FileName = $baseName -replace "[$([regex]::Escape($invalidChars))]", '_'
		}

		# For DASH output, create a directory and return the manifest path
		if ($OutputDash) {
			$dashDir = Join-Path $OutputFolder $FileName

			# Check if directory already exists
			if (Test-Path $dashDir) {
				if (-not $Resume) {
					$stem = $FileName
					$counter = 1

					while (Test-Path $dashDir) {
						$dashDir = Join-Path $OutputFolder "${stem}_${counter}"
						$counter++
					}

					Write-Warning "Directory already exists. Saving as: $(Split-Path $dashDir -Leaf)"
				}
				else {
					Write-Verbose "Resuming encoding in existing directory: $dashDir"
				}
			}

			# Create the DASH output directory (if not resuming)
			if (-not (Test-Path $dashDir)) {
				New-Item -ItemType Directory -Path $dashDir -Force | Out-Null
				Write-Verbose "Created DASH output directory: $dashDir"
			}

			return Join-Path $dashDir 'manifest.mpd'
		}

		$outputFile = Join-Path $OutputFolder "$FileName.$Format"

		# Guard against accidental overwrites
		if (Test-Path $outputFile) {
			$stem = $FileName
			$counter = 1

			while (Test-Path $outputFile) {
				$outputFile = Join-Path $OutputFolder "${stem}_${counter}.$Format"
				$counter++
			}

			Write-Warning "File already exists. Saving as: $(Split-Path $outputFile -Leaf)"
		}

		return $outputFile
	}

	function Build-FfmpegArgument {
		<#
		.SYNOPSIS
			Constructs the ffmpeg argument array for downloading a stream manifest.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$ManifestUrl,

			[Parameter(Mandatory)]
			[string]$OutputFile,

			[hashtable]$Headers,

			[switch]$Progressive,

			[switch]$OutputDash,

			[hashtable]$ResumeInfo,

			[string[]]$ExtraInputArgs,

			[string[]]$ExtraOutputArgs
		)

		$args = [System.Collections.Generic.List[string]]::new()

		# Global flags: overwrite prompt already handled, hide banner
		$args.Add('-hide_banner')

		# Append optional HTTP headers
		if ($Headers -and $Headers.Count -gt 0) {
			$headerString = ($Headers.GetEnumerator() |
					ForEach-Object { "$($_.Key): $($_.Value)" }) -join "`r`n"
			$args.Add('-headers')
			$args.Add($headerString)
		}

		# Allow the manifest protocol (DASH / HLS)
		$args.Add('-allowed_extensions')
		$args.Add('ALL')

		# Extra input arguments (before -i)
		if ($ExtraInputArgs) {
			foreach ($a in $ExtraInputArgs) { $args.Add($a) }
		}

		# Add resume offset when continuing incomplete encoding
		if ($ResumeInfo -and $ResumeInfo.StartTime -gt 0) {
			$args.Add('-ss')
			$args.Add($ResumeInfo.StartTime.ToString())
		}

		# Input source
		$args.Add('-i')
		$args.Add($ManifestUrl)

		if ($OutputDash) {
			# Map video and audio streams
			$args.Add('-map')
			$args.Add('0:v:0')
			$args.Add('-map')
			$args.Add('0:a:0')

			# Video encoding: H.264 with consistent keyframes for DASH
			$args.Add('-c:v')
			$args.Add('libx264')
			$args.Add('-preset')
			$args.Add('veryfast')
			$args.Add('-crf')
			$args.Add('21')
			$args.Add('-g')
			$args.Add('180')
			$args.Add('-keyint_min')
			$args.Add('180')
			$args.Add('-sc_threshold')
			$args.Add('0')

			# Audio encoding: AAC
			$args.Add('-c:a')
			$args.Add('aac')
			$args.Add('-b:a')
			$args.Add('128k')

			# DASH format configuration
			$args.Add('-f')
			$args.Add('dash')
			$args.Add('-seg_duration')
			$args.Add('6')
			$args.Add('-use_template')
			$args.Add('1')
			$args.Add('-use_timeline')
			$args.Add('1')
			$args.Add('-adaptation_sets')
			$args.Add('id=0,streams=v id=1,streams=a')

			# Configure segment numbering when resuming
			if ($ResumeInfo -and $ResumeInfo.StartSegment) {
				$args.Add('-media_seg_name')
				$args.Add('chunk-stream$RepresentationID$-$Number%05d$.m4s')
				$args.Add('-init_seg_name')
				$args.Add('init-stream$RepresentationID$.m4s')
				$args.Add('-start_number')
				$args.Add($ResumeInfo.StartSegment.ToString())
			}
		}
		else {
			# Default codec: copy (no re-encoding)
			$args.Add('-c')
			$args.Add('copy')

			# For MP4 format, configure movflags for progressive/streaming support
			if ($OutputFile -match '\.mp4$') {
				$args.Add('-movflags')
				if ($Progressive) {
					# Fragmented MP4 for better streaming compatibility
					$args.Add('+frag_keyframe+empty_moov+default_base_moof')
				}
				else {
					# Standard progressive MP4 with moov atom at the start
					$args.Add('+faststart')
				}
			}
		}

		# Extra output arguments (after -i, before output file)
		if ($ExtraOutputArgs) {
			foreach ($a in $ExtraOutputArgs) { $args.Add($a) }
		}

		# Overwrite without prompting
		$args.Add('-y')

		# Output file (use basename only for DASH, ffmpeg will be run from the DASH directory)
		if ($OutputDash) {
			$args.Add([System.IO.Path]::GetFileName($OutputFile))
		}
		else {
			$args.Add($OutputFile)
		}

		return $args.ToArray()
	}

	function Invoke-Ffmpeg {
		<#
		.SYNOPSIS
			Runs ffmpeg with the given arguments, streaming output to the console.
		#>
		param(
			[Parameter(Mandatory)]
			[string[]]$Arguments,

			[string]$WorkingDirectory
		)

		$action = if ($Arguments -contains '-f' -and $Arguments -contains 'dash') {
			'Encoding to DASH package...'
		}
		else {
			'Downloading stream...'
		}

		Write-Host "  $action" -ForegroundColor Cyan
		Write-Verbose "ffmpeg $($Arguments -join ' ')"

		# Start ffmpeg as a process so we can capture both stdout and stderr
		$processInfo = [System.Diagnostics.ProcessStartInfo]::new()
		$processInfo.FileName = 'ffmpeg'
		$processInfo.Arguments = ($Arguments | ForEach-Object {
				if ($_ -match '\s') { "`"$_`"" } else { $_ }
			}) -join ' '
		$processInfo.RedirectStandardError = $true
		$processInfo.RedirectStandardOutput = $true
		$processInfo.UseShellExecute = $false
		$processInfo.CreateNoWindow = $true

		# Set working directory for DASH output to ensure segments go in the right place
		if ($WorkingDirectory) {
			$processInfo.WorkingDirectory = $WorkingDirectory
			Write-Verbose "Working directory: $WorkingDirectory"
		}

		$process = [System.Diagnostics.Process]::Start($processInfo)

		# Collect all stderr output for error reporting
		$stderrLines = [System.Collections.Generic.List[string]]::new()

		# ffmpeg writes progress to stderr
		while (-not $process.StandardError.EndOfStream) {
			$line = $process.StandardError.ReadLine()
			$stderrLines.Add($line)

			# Show progress lines (contain 'time=') and error/warning lines
			if ($line -match 'time=' -or $line -match 'Error|Warning') {
				Write-Host "`r  $line" -NoNewline -ForegroundColor DarkGray
			}
		}

		$process.WaitForExit()

		# Clear the progress line
		Write-Host ''

		if ($process.ExitCode -ne 0) {
			# Get last 20 lines of stderr for error context
			$errorContext = $stderrLines | Select-Object -Last 20 | Out-String
			throw "ffmpeg exited with code $($process.ExitCode).`n`nError output:`n$errorContext"
		}

		Write-Verbose 'ffmpeg completed successfully'
	}

	function Show-Result {
		<#
		.SYNOPSIS
			Displays a summary of the downloaded video file or DASH package.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$OutputFile
		)

		$fileInfo = Get-Item $OutputFile

		# Check if this is a DASH manifest (output is a directory)
		if ($fileInfo -is [System.IO.DirectoryInfo] -or $OutputFile -match 'manifest\.mpd$') {
			$dashDir = if ($fileInfo -is [System.IO.DirectoryInfo]) {
				$fileInfo.FullName
			}
			else {
				Split-Path $OutputFile -Parent
			}

			$manifestPath = Join-Path $dashDir 'manifest.mpd'
			$totalSize = (Get-ChildItem $dashDir -Recurse -File |
					Measure-Object -Property Length -Sum).Sum
			$sizeMB = '{0:N1} MB' -f ($totalSize / 1MB)
			$fileCount = (Get-ChildItem $dashDir -File).Count

			Write-Host ''
			Write-Host '  DASH package complete!' -ForegroundColor Green
			Write-Host "  Manifest: $manifestPath" -ForegroundColor Green
			Write-Host "  Directory: $dashDir" -ForegroundColor Green
			Write-Host "  Total size: $sizeMB ($fileCount files)" -ForegroundColor Green
		}
		else {
			$sizeMB = '{0:N1} MB' -f ($fileInfo.Length / 1MB)

			Write-Host ''
			Write-Host '  Download complete!' -ForegroundColor Green
			Write-Host "  File: $($fileInfo.FullName)" -ForegroundColor Green
			Write-Host "  Size: $sizeMB" -ForegroundColor Green
		}
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
