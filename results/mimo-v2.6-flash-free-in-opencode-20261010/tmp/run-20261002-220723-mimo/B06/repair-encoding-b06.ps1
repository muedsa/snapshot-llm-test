# repair-encoding-b06.ps1 -- PS5.1 Invoke-WebRequest decoded UTF-8 bodies as Latin-1
# (response had no charset), so some saved research/doc files are double-encoded:
# file bytes = UTF-8( Latin1( realUTF8 ) ).  Round-trip them into a sibling *.fixed
# file; the ORIGINAL files are never modified or deleted.
$ErrorActionPreference = 'Stop'
$dir = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B06')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$lat = [Text.Encoding]::GetEncoding(28591)

$targets = @()
$targets += Get-ChildItem (Join-Path $dir 'research') -File
$targets += Get-ChildItem (Join-Path $dir 'docs') -File

$fixed = 0; $skipped = 0
foreach ($f in $targets) {
  $raw = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
  $bad = 0
  foreach ($ch in $raw.ToCharArray()) { if ([int]$ch -ge 0x80 -and [int]$ch -le 0x9F) { $bad++ } }
  if ($bad -eq 0) { $skipped++; continue }        # no C1 controls => already correctly decoded
  $recovered = [Text.Encoding]::UTF8.GetString($lat.GetBytes($raw))
  $cjk = 0
  foreach ($ch in $recovered.ToCharArray()) { if ([int]$ch -gt 0x4E00 -and [int]$ch -lt 0x9FFF) { $cjk++ } }
  $out = Join-Path $f.DirectoryName ($f.Name + '.fixed')
  [IO.File]::WriteAllText($out, $recovered, $utf8)
  $fixed++
  if ($cjk -eq 0) { "  WARN no CJK after round-trip: $($f.Name)" }
}
"scanned = $($targets.Count)  repaired -> .fixed = $fixed  skipped = $skipped"
