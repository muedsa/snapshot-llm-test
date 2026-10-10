$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Strip-Html([string]$h) {
  $h = [regex]::Replace($h, '(?is)<script.*?</script>', ' ')
  $h = [regex]::Replace($h, '(?is)<style.*?</style>', ' ')
  $h = [regex]::Replace($h, '(?i)</(p|li|tr|h[1-6]|div|pre|code|table|section)>', "`n")
  $h = [regex]::Replace($h, '(?i)<br\s*/?>', "`n")
  $h = [regex]::Replace($h, '(?s)<[^>]+>', '')
  $h = [System.Net.WebUtility]::HtmlDecode($h)
  $h = [regex]::Replace($h, "[ \t]+", ' ')
  return $h
}
foreach ($f in @('doc-painting.html','doc-parser.html','doc-layout.html','doc-media-text.html','doc-rendering.html')) {
  $p = "tmp\run-20261002-220723-mimo\A17\$f"
  $raw = [IO.File]::ReadAllText((Join-Path $ROOT $p), $utf8)
  Write-Output "=== $f ==="
  foreach ($m in [regex]::Matches($raw, '(?is)<h([1-6])[^>]*>(.*?)</h\1>')) {
    $t = (Strip-Html $m.Groups[2].Value) -replace "\s+", ' '
    Write-Output ("  h{0}  {1}" -f $m.Groups[1].Value, $t.Trim())
  }
}
