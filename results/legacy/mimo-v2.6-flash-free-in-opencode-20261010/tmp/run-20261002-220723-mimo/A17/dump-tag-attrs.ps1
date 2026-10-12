$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$utf8 = New-Object System.Text.UTF8Encoding($false)
$raw = [IO.File]::ReadAllText((Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15\doc-parser-tags.html'), $utf8)

function Strip-Html([string]$h) {
  $h = [regex]::Replace($h, '(?is)<script.*?</script>', ' ')
  $h = [regex]::Replace($h, '(?is)<style.*?</style>', ' ')
  $h = [regex]::Replace($h, '(?i)</(p|li|tr|h[1-6]|div|pre|code|table|section|td|th)>', "`n")
  $h = [regex]::Replace($h, '(?i)<br\s*/?>', "`n")
  $h = [regex]::Replace($h, '(?s)<[^>]+>', '')
  $h = [System.Net.WebUtility]::HtmlDecode($h)
  $h = [regex]::Replace($h, "[ \t]+", ' ')
  return $h
}

$heads = @()
foreach ($m in [regex]::Matches($raw, '(?is)<h([1-6])[^>]*>(.*?)</h\1>')) {
  $txt = (Strip-Html $m.Groups[2].Value) -replace "\s+", ' '
  $heads += [pscustomobject]@{ lvl = [int]$m.Groups[1].Value; text = $txt.Trim(); start = $m.Index; contentStart = ($m.Index + $m.Length) }
}

$want = @('Container', 'SizedBox', 'Text', 'ClipRect', 'Positioned', 'Stack')
$out = New-Object System.Collections.Generic.List[string]
$out.Add('# parser-tags - per-tag attribute rows actually extracted')
foreach ($nm in $want) {
  $hit = $null
  for ($i = 0; $i -lt $heads.Count; $i++) {
    if ($heads[$i].text -eq $nm) { $hit = $i; break }
  }
  $out.Add('')
  if ($null -eq $hit) { $out.Add("## $nm - no exact heading found (not claimed)"); continue }
  $end = $raw.Length
  for ($j = $hit + 1; $j -lt $heads.Count; $j++) {
    if ($heads[$j].lvl -le $heads[$hit].lvl) { $end = $heads[$j].start; break }
  }
  $slice = Strip-Html $raw.Substring($heads[$hit].contentStart, ($end - $heads[$hit].contentStart))
  $lines = @()
  foreach ($ln in $slice.Split("`n")) { $t = $ln.Trim(); if ($t) { $lines += $t } }
  $out.Add("## $nm  (heading level $($heads[$hit].lvl))")
  $k = 0
  foreach ($ln in $lines) { $out.Add("> $ln"); $k++; if ($k -ge 70) { $out.Add('> …'); break } }
}
[IO.File]::WriteAllLines((Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A17\tag-attrs.md'), $out.ToArray(), $utf8)
Write-Output ("wrote tag-attrs.md lines=" + $out.Count)
