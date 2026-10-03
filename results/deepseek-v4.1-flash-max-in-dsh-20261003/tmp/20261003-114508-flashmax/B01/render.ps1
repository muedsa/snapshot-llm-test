param(
  [Parameter(Mandatory)][string]$Manifest,
  [Parameter(Mandatory)][string]$Task
)
# Renders every DSL listed in the manifest (TSV: dslPath<TAB>outPath<TAB>caseId<TAB>phase)
# through the shared helper and prints one result line per request.
. "D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared\render.ps1"
$log = "D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\$Task\requests.jsonl"
foreach ($line in [System.IO.File]::ReadAllLines($Manifest)) {
  if (-not $line.Trim()) { continue }
  $f = $line -split "`t"
  if ($f.Count -lt 2) { continue }
  $case = if ($f.Count -ge 3 -and $f[2].Trim()) { $f[2].Trim() } else { '' }
  $phase = if ($f.Count -ge 4 -and $f[3].Trim()) { $f[3].Trim() } else { 'render' }
  $r = Invoke-Snapshot -DslPath $f[0].Trim() -OutPath $f[1].Trim() -LogPath $log `
        -ReqPrefix "$Task-REQ" -Task $Task -Case $case -Phase $phase
  "{0}`t{1}`t{2}`t{3}`t{4}" -f $r.RequestId, $r.Status, $r.Success, $r.Bytes, $f[1].Trim()
  if (-not $r.Success) { "    ERR: $($r.Error)" }
}
