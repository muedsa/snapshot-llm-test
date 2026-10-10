# A16 - validate findings.json parses and print its structure
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$p = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A16\findings.json'
try {
  $j = Get-Content $p -Raw -Encoding UTF8 | ConvertFrom-Json
  Write-Output ("parsed OK; findings=" + $j.findings.Count + " uncertain=" + $j.uncertain.Count)
  foreach ($f in $j.findings) {
    Write-Output ("  {0} [{1}/{2}] {3}" -f $f.id, $f.severity, $f.kind, $f.title)
    $missing = @()
    foreach ($k in @('image_location','phenomenon','source_check','impact','correction','final_view_result','evidence')) {
      if (-not ($f.PSObject.Properties.Name -contains $k)) { $missing += $k }
      else {
        $v = $f.$k
        if ($v -is [string] -and [string]::IsNullOrWhiteSpace($v)) { $missing += $k }
        if ($null -eq $v) { $missing += $k }
      }
    }
    if ($missing.Count -gt 0) { Write-Output ("      MISSING: " + ($missing -join ',')) }
  }
  foreach ($u in $j.uncertain) {
    Write-Output ("  {0} [uncertain/{1}] {2}" -f $u.id, $u.kind, $u.title)
    if ($u.confirmed_error -eq $true) { Write-Output ("      ERROR: uncertain item marked confirmed_error=true") }
  }
  Write-Output ("summary: " + ($j.summary | ConvertTo-Json -Compress))
  Write-Output ("annual : " + ($j.source_recomputation.annual | ConvertTo-Json -Compress))
  Write-Output ("claims : ")
  foreach ($c in $j.source_recomputation.flawed_claims_disproved) { Write-Output ("   - " + $c) }
} catch {
  Write-Output ("PARSE FAIL: " + $_.Exception.Message)
}
