# A16 - extract the exact attribute names this task relies on out of the REAL
# retained documentation bytes (A15 fetched these two pages from
# https://snapshot.muedsa.com ; they are reused here rather than re-requested).
# Output: tmp/.../A16/doc-excerpts.md
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$ENC = New-Object Text.UTF8Encoding($false)

$srcs = @(
  @{ tag = 'container'; path = 'tmp\run-20261002-220723-mimo\A15\doc-container-widget.html'; url = 'https://snapshot.muedsa.com/widgets/layout/container/' },
  @{ tag = 'parser';    path = 'tmp\run-20261002-220723-mimo\A15\doc-parser-tags.html';      url = 'https://snapshot.muedsa.com/reference/parser-tags/' }
)
$needles = @('borderRadius', 'Positioned', 'fontStyle', 'fontSize', 'fontFamily', 'letterSpacing',
             'Snapshot', 'Stack', 'width', 'height', 'color', 'border')

$out = @()
$out += '# A16 - documentation excerpts actually consulted'
$out += ''
$out += 'Sources are the retained bytes fetched from snapshot.muedsa.com during this run'
$out += '(same run_id, same URLs). Reused for A16 without issuing a duplicate HTTP request,'
$out += 'per the suite rule that a cached result may be cited but not counted as a new request.'
$out += ''

foreach ($s in $srcs) {
  $p = Join-Path $ROOT $s.path
  if (-not (Test-Path $p)) { $out += ("MISSING: " + $s.path); continue }
  $html = [IO.File]::ReadAllText($p)
  # strip tags so the prose is readable
  $txt = [regex]::Replace($html, '<script[^>]*>.*?</script>', ' ', 'Singleline,IgnoreCase')
  $txt = [regex]::Replace($txt, '<style[^>]*>.*?</style>', ' ', 'Singleline,IgnoreCase')
  $txt = [regex]::Replace($txt, '<[^>]+>', ' ')
  $txt = [regex]::Replace($txt, '&nbsp;', ' ')
  $txt = [regex]::Replace($txt, '&amp;', '&')
  $txt = [regex]::Replace($txt, '[ \t]+', ' ')
  $txt = [regex]::Replace($txt, "(\r?\n\s*)+", ' ')
  $out += ('## ' + $s.tag + ' - ' + $s.url)
  $out += ('retained bytes: ' + $s.path + ' (' + (Get-Item $p).Length + ' bytes)')
  $out += ''
  foreach ($n in $needles) {
    $hits = @()
    $idx = 0
    while ($hits.Count -lt 3) {
      $i = $txt.IndexOf($n, $idx, [StringComparison]::OrdinalIgnoreCase)
      if ($i -lt 0) { break }
      $a = [math]::Max(0, $i - 90)
      $b = [math]::Min($txt.Length, $i + 150)
      $hits += ($txt.Substring($a, $b - $a).Trim())
      $idx = $i + $n.Length
    }
    if ($hits.Count -gt 0) {
      $out += ('- `' + $n + '` - ' + $hits.Count + ' excerpt(s):')
      foreach ($h in $hits) { $out += ('    > ' + $h) }
    } else {
      $out += ('- `' + $n + '` - no prose hit (attribute documented in tables that collapsed)')
    }
  }
  $out += ''
}
[IO.File]::WriteAllText((Join-Path $TMP 'doc-excerpts.md'), (($out -join "`n") + "`n"), $ENC)
Write-Output ("wrote {0}  ({1} lines)" -f (Join-Path $TMP 'doc-excerpts.md'), $out.Count)
