$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$p = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16\iterations.jsonl'
$lines = [IO.File]::ReadAllLines($p)
$n = 0; $bad = 0; $imgs = 0; $iv = 0
$types = @{}; $cats = @{}
foreach ($ln in $lines) {
  if ([string]::IsNullOrWhiteSpace($ln)) { continue }
  $n++
  try {
    $o = $ln | ConvertFrom-Json
  } catch { $bad++; Write-Output ("line {0} BAD: {1}" -f $n, $_.Exception.Message); continue }
  if (-not $o.id) { $bad++; Write-Output ("line {0} missing id" -f $n) }
  if ($o.seq -ne $n) { Write-Output ("line {0} seq={1} mismatch" -f $n, $o.seq); $bad++ }
  $imgs += [int]$o.images_viewed
  if ($o.images_viewed_by_independent_viewer) { $iv += [int]$o.images_viewed_by_independent_viewer }
  if ($types.ContainsKey($o.type)) { $types[$o.type] = $types[$o.type] + 1 } else { $types[$o.type] = 1 }
  if ($cats.ContainsKey($o.category)) { $cats[$o.category] = $cats[$o.category] + 1 } else { $cats[$o.category] = 1 }
  foreach ($k in @('id','seq','task','type','category','stage','target','action','finding','outcome','evidence','note')) {
    if (-not ($o.PSObject.Properties.Name -contains $k)) { $bad++; Write-Output ("line {0} missing {1}" -f $n, $k) }
  }
}
Write-Output ("rows={0} bad={1} images_viewed_total={2} independent_viewer={3}" -f $n, $bad, $imgs, $iv)
Write-Output ("types: " + (($types.GetEnumerator() | ForEach-Object { $_.Key + '=' + $_.Value }) -join ', '))
Write-Output ("categories: " + (($cats.GetEnumerator() | ForEach-Object { $_.Key + '=' + $_.Value }) -join ', '))

$req = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16\requests.jsonl'
$rn = 0; $render = 0; $doc = 0; $fail = 0; $ms = 0.0
foreach ($ln in [IO.File]::ReadAllLines($req)) {
  if ([string]::IsNullOrWhiteSpace($ln)) { continue }
  $o = $ln | ConvertFrom-Json
  $rn++
  if ($o.type -eq 'render') { $render++; if ($o.duration_ms) { $ms += [double]$o.duration_ms } }
  if ($o.type -eq 'document') { $doc++ }
  if ($o.http_status -ne 200) { $fail++ }
}
Write-Output ("requests.jsonl rows={0} renders={1} documents={2} non200={3} render_duration_sum_ms={4}" -f $rn, $render, $doc, $fail, $ms)
