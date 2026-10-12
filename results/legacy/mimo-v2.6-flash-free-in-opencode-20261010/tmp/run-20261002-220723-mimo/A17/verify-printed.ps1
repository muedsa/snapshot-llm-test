$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$ROOT = $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
$T = Join-Path $ROOT "tmp\run-20261002-220723-mimo\A17"
$OUT = Join-Path $ROOT "outputs\run-20261002-220723-mimo\A17"
$R = Join-Path $ROOT "tmp\run-20261002-220723-mimo\_suite\render.ps1"

$rows = @(
  @{ id='01'; omit=11; why='两条响应提示文本' },
  @{ id='02'; omit=12; why='右下定位的第二块' },
  @{ id='03'; omit=14; why='两条图例行' },
  @{ id='04'; omit=5;  why='两条色带' }
)

$report = New-Object System.Collections.Generic.List[string]
$report.Add("# printed snippet parse verification")
$report.Add("")
$report.Add("Each handbook page prints 16 verbatim lines of the matching example-0N.snapshot")
$report.Add("plus one DSL-comment marker line, 17 lines total. This rebuilds exactly that")
$report.Add("17-line text from the shipped example file and sends it to the service at 400x240")
$report.Add("to prove the printed text is real, parseable DSL rather than decoration.")
$report.Add("The marker line is an XML comment, so it must be skipped by the parser for the")
$report.Add("snippet to load.")
$report.Add("")

foreach ($p in $rows) {
  $srcFile = Join-Path $OUT ("example-" + $p.id + ".snapshot")
  $all = [IO.File]::ReadAllLines($srcFile, $utf8)
  if ($all.Count -ne 18) { throw "example-$($p.id) has $($all.Count) lines, expected 18" }
  $k = $p.omit
  $marker = '<!--省略 example-' + $p.id + '.snapshot 第 ' + $k + '、' + ($k+1) + ' 行（' + $p.why + '）；完整文件共 18 行 -->'
  $printed = @()
  $printed += $all[0..($k-2)]
  $printed += $marker
  $printed += $all[($k+1)..17]
  if ($printed.Count -ne 17) { throw "printed count $($printed.Count)" }

  $file = Join-Path $T ("printed-" + $p.id + ".snapshot")
  [IO.File]::WriteAllLines($file, $printed, $utf8)

  $pngPath = Join-Path $T ("printed-" + $p.id + ".png")
  $reqId = "A17-printed" + $p.id
  if (Test-Path $pngPath) {
    # already rendered earlier in this run - reuse the recorded request instead of duplicating it
    $row = Get-Content (Join-Path $T "requests.jsonl") | ForEach-Object { $_ | ConvertFrom-Json } |
           Where-Object { $_.id -eq $reqId } | Select-Object -Last 1
    $status = "reused request $reqId (HTTP $($row.http_status), $($row.duration_ms) ms)"
    $note = "rendered earlier in this run"
  } else {
    # render.ps1 exits non-zero on failure, so run it in a child process
    $note = & powershell -NoProfile -ExecutionPolicy Bypass -File $R `
               -DslPath $file -OutPath $pngPath -TaskId "A17" -ReqId $reqId 2>&1 | ForEach-Object { "$_" }
    $status = "rendered"
    if (-not (Test-Path $pngPath)) { $status = "FAILED" }
  }
  $report.Add("## printed-$($p.id)  (17 lines, omits example-$($p.id).snapshot $($k) $($k+1))")
  $report.Add("- source: outputs/run-20261002-220723-mimo/A17/example-$($p.id).snapshot (18 lines)")
  $report.Add("- request id: " + $reqId)
  $report.Add("- status: " + $status)
  $report.Add("- result: " + $note.Trim())
  $report.Add("")
}
[IO.File]::WriteAllLines((Join-Path $T "printed-parse-report.md"), $report.ToArray(), $utf8)
Write-Output "wrote printed-parse-report.md"
