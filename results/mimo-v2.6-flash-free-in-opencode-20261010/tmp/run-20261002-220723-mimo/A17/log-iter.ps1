param(
  [Parameter(Mandatory=$true)][string]$Version,
  [string]$Parent = $null,
  [Parameter(Mandatory=$true)][string]$Type,
  [Parameter(Mandatory=$true)][string]$Purpose,
  [string]$Dsl = $null,
  [string]$Image = $null,
  [string]$RequestId = $null,
  [int]$HttpStatus = 0,
  [double]$DurationMs = -1,
  [string]$ErrorSummary = $null,
  [string]$ViewedAt = $null,
  [string]$ViewMethod = $null,
  [string]$Observed = $null,
  [string]$Change = $null,
  [string]$Category = $null
)
$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$LOG = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A17\iterations.jsonl')
$seq = 0
if (Test-Path $LOG) { $seq = @(Get-Content $LOG | Where-Object { $_ -and $_.Trim() }).Count }
$seq++
if (-not $Parent) { $parentVal = $null } else { $parentVal = $Parent }
function Arr($s) { if (-not $s) { return $null }; return @($s -split '\s*\|\|\s*') }
$render = [ordered]@{}
if ($RequestId) { $render.request_id = $RequestId }
if ($HttpStatus -gt 0) { $render.http_status = $HttpStatus }
if ($DurationMs -ge 0) { $render.duration_ms = $DurationMs }
if ($ErrorSummary) { $render.error_summary = $ErrorSummary }
$entry = [ordered]@{
  seq = $seq; task = "A17"; version = $Version; parent = $parentVal; type = $Type
  purpose = $Purpose
  dsl = $Dsl
  image = $Image
  render = $render
  viewed_at = $ViewedAt
  view_method = $ViewMethod
  observed_problems = (Arr $Observed)
  change = $Change
}
if ($Category) { $entry.category = $Category }
[IO.File]::AppendAllText($LOG, (($entry | ConvertTo-Json -Compress -Depth 6) + "`n"), $utf8)
Write-Output "logged iteration seq=$seq version=$Version type=$Type"
