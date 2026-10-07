$ErrorActionPreference = 'Stop'
$exportInfo = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'latest-export.json') -Raw | ConvertFrom-Json
$exportPath = [IO.Path]::GetFullPath($exportInfo.output)
$archivePath = "$exportPath.zip"
if (Test-Path -LiteralPath $archivePath) { throw 'Archive already exists' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($exportPath, $archivePath, [IO.Compression.CompressionLevel]::Optimal, $false)
$expectedHashes = @{}
foreach ($line in (Get-Content -LiteralPath (Join-Path $exportPath 'SHA256SUMS.txt'))) {
    if ($line -match '^([a-f0-9]{64})  (.+)$') { $expectedHashes[$Matches[2]] = $Matches[1] }
}
$archive = [IO.Compression.ZipFile]::OpenRead($archivePath)
$checked = 0
try {
    foreach ($entry in $archive.Entries) {
        $entryName = $entry.FullName.Replace('\', '/')
        if ($entryName.EndsWith('/')) { continue }
        if ($entryName -eq 'SHA256SUMS.txt') { continue }
        if (-not $expectedHashes.ContainsKey($entryName)) { throw "Unexpected archive entry: $entryName" }
        $stream = $entry.Open()
        $sha = [Security.Cryptography.SHA256]::Create()
        try { $actual = [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
        finally { $sha.Dispose(); $stream.Dispose() }
        if ($actual -ne $expectedHashes[$entryName]) { throw "Archive hash mismatch: $entryName" }
        $checked++
    }
    if ($checked -ne $expectedHashes.Count) { throw 'Archive is missing expected entries' }
} finally { $archive.Dispose() }
$archiveHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
"$archiveHash  $([IO.Path]::GetFileName($archivePath))" | Set-Content -LiteralPath "$archivePath.sha256" -Encoding ascii
$verification = [ordered]@{ archive = $archivePath; archive_bytes = (Get-Item -LiteralPath $archivePath).Length; sha256 = $archiveHash; verified_entries = $checked; passed = $true; verified_at = [DateTime]::UtcNow.ToString('o') }
$verification | ConvertTo-Json | Set-Content -LiteralPath "$archivePath.validation.json" -Encoding utf8
$verification | ConvertTo-Json -Compress
