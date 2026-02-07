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
	[string]$OutputPath = '.\data',

	[Parameter(HelpMessage = 'Base name for the output file (without extension)')]
	[string]$FileName,

	[Parameter(HelpMessage = 'Output container format')]
	[ValidateSet('mp4', 'mkv', 'webm')]
	[string]$Format = 'mp4',

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

	# Determine the output file path
	$outputFile = New-OutputFilePath `
		-OutputFolder $resolvedOutput `
		-ManifestUrl $ManifestUrl `
		-FileName $FileName `
		-Format $Format

	# Build the ffmpeg argument list
	$ffmpegArgs = Build-FfmpegArgument `
		-ManifestUrl $ManifestUrl `
		-OutputFile $outputFile `
		-Headers $Headers `
		-ExtraInputArgs $ExtraInputArgs `
		-ExtraOutputArgs $ExtraOutputArgs

	# Execute ffmpeg to download and mux the stream
	Invoke-Ffmpeg -Arguments $ffmpegArgs

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
			Determines the full path for the output video file.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$OutputFolder,

			[Parameter(Mandatory)]
			[string]$ManifestUrl,

			[string]$FileName,

			[Parameter(Mandatory)]
			[string]$Format
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

		# Input source
		$args.Add('-i')
		$args.Add($ManifestUrl)

		# Default codec: copy (no re-encoding)
		$args.Add('-c')
		$args.Add('copy')

		# For MP4 format, add movflags to make files more resilient to incomplete downloads
		if ($OutputFile -match '\.mp4$') {
			$args.Add('-movflags')
			$args.Add('+faststart')
		}

		# Extra output arguments (after -i, before output file)
		if ($ExtraOutputArgs) {
			foreach ($a in $ExtraOutputArgs) { $args.Add($a) }
		}

		# Overwrite without prompting
		$args.Add('-y')

		# Output file
		$args.Add($OutputFile)

		return $args.ToArray()
	}

	function Invoke-Ffmpeg {
		<#
		.SYNOPSIS
			Runs ffmpeg with the given arguments, streaming output to the console.
		#>
		param(
			[Parameter(Mandatory)]
			[string[]]$Arguments
		)

		Write-Host '  Downloading stream...' -ForegroundColor Cyan
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
			Displays a summary of the downloaded video file.
		#>
		param(
			[Parameter(Mandatory)]
			[string]$OutputFile
		)

		$fileInfo = Get-Item $OutputFile
		$sizeMB = '{0:N1} MB' -f ($fileInfo.Length / 1MB)

		Write-Host ''
		Write-Host '  Download complete!' -ForegroundColor Green
		Write-Host "  File: $($fileInfo.FullName)" -ForegroundColor Green
		Write-Host "  Size: $sizeMB" -ForegroundColor Green
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
