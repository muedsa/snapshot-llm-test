$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:SNAPSHOT_TASK_ROOT = 'D:\mine\test\glm-5.3-flash'
$env:SNAPSHOT_RUN_ID = '20261016T164020-m1'
$root = $env:SNAPSHOT_TASK_ROOT
$run = $env:SNAPSHOT_RUN_ID
$client = "$root\tmp\$run\_suite\snapshot_client.py"
foreach ($i in 1..10) {
  $cs = "case-{0:d2}" -f $i
  $dsl = "tmp\$run\B04\dsl\$cs.snapshot"
  $tag = "b04-$cs-v1"
  $outdir = "outputs\$run\B04\$cs"
  $json = python $client render B04 $dsl $tag $outdir 2>&1 | Select-Object -Last 1
  $obj = $null
  try { $obj = $json | ConvertFrom-Json } catch {}
  if ($obj -and $obj.ok) {
    Copy-Item $obj.resp_file "$root\$outdir\final.png" -Force
    Write-Host ("OK {0} status={1} bytes={2}" -f $cs, $obj.status, $obj.bytes)
  } else {
    Write-Host ("FAIL {0} raw={1}" -f $cs, ($json | Out-String).Substring(0, [Math]::Min(400, ($json | Out-String).Length)))
  }
}
