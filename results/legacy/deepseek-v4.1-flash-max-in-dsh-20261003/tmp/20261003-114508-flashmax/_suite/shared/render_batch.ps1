param(
  [Parameter(Mandatory)][string]$JobsJson,
  [string]$Root = 'D:\workspaces\deepseek-v4.1-flash-max-in-dsh'
)
# Render a batch of DSL files described by a JSON array of jobs.
# Each job: { dsl, out, task, prefix, round, phase, case }
# Appends one line per HTTP request to the task requests.jsonl used by the suite.
$ErrorActionPreference = 'Stop'
. (Join-Path $Root 'tmp\20261003-114508-flashmax\_suite\shared\render.ps1')
$jobs = Get-Content -LiteralPath $JobsJson -Raw | ConvertFrom-Json
$results = @()
foreach ($j in $jobs) {
  $log = Join-Path $Root ("tmp\20261003-114508-flashmax\{0}\requests.jsonl" -f $j.task)
  $out = Join-Path $Root $j.out
  $dsl = Join-Path $Root $j.dsl
  $r = Invoke-Snapshot -DslPath $dsl -OutPath $out -LogPath $log -ReqPrefix $j.prefix `
        -Task $j.task -Round $j.round -Case $j.case -Phase $j.phase
  $results += [pscustomobject]@{ request_id = $r.RequestId; dsl = $j.dsl; out = $j.out; ok = $r.Success; status = $r.Status; ms = $r.DurationMs; bytes = $r.Bytes }
}
$results | ConvertTo-Json -Depth 4
