# Render one or more B05/B06 cases: generates the DSL first and only posts when the
# generator succeeded, so a code error never burns a render request.
# Usage: pwsh -File render_cases.ps1 -Task B05 -Ver v1 -Cases case-01,case-02
param(
  [string]$Task = "B05",
  [string]$Ver = "v1",
  [string[]]$Cases = @("case-01")
)
$ErrorActionPreference = "Continue"
$root = "D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
$run = "20261003-114508-flashmax"
$t = Join-Path $root "tmp\$run\$Task"
$py = "C:\Users\mueds\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
. "$root\tmp\$run\_suite\shared\render.ps1"

& $py "$t\tools\gen_$($Task.ToLower()).py" $Ver @Cases
if ($LASTEXITCODE -ne 0) { Write-Output "GEN FAILED - no render posted"; exit 1 }

foreach ($c in $Cases) {
  $dsl = Join-Path $t "dsl\$c.$Ver.snapshot"
  $png = Join-Path $t "render\$c.$Ver.png"
  if (-not (Test-Path -LiteralPath $dsl)) { Write-Output "MISSING $dsl"; continue }
  $r = Invoke-Snapshot -DslPath $dsl -OutPath $png -LogPath "$t\requests.jsonl" `
       -ReqPrefix "$Task-REQ" -Task $Task -Case $c -Phase "render-$Ver"
  Write-Output ("{0} {1} status={2} bytes={3} {4}ms req={5}" -f $c, $r.Success, $r.Status, $r.Bytes, $r.DurationMs, $r.RequestId)
  if (-not $r.Success) { Write-Output ("   ERROR: " + $r.Error) }
}
