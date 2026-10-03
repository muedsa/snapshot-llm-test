# A09 render helper: renders one DSL version against the real service.
# usage: pwsh -File render_a09.ps1 <version> [phase] [name]
param(
  [Parameter(Mandatory)][string]$Version,
  [string]$Phase = 'baseline',
  [string]$Name = 'transform-atlas'
)
$ErrorActionPreference = 'Stop'
$root = 'D:\workspaces\deepseek-v4.1-flash-max-in-dsh'
. (Join-Path $root 'tmp\20261003-114508-flashmax\_suite\shared\render.ps1')
$tmp = Join-Path $root 'tmp\20261003-114508-flashmax\A09'
$res = Invoke-Snapshot -DslPath (Join-Path $tmp "$Name.$Version.snapshot") `
  -OutPath (Join-Path $tmp "$Name.$Version.png") `
  -LogPath (Join-Path $tmp 'requests.jsonl') -ReqPrefix 'A09-REQ' -Task 'A09' -Phase $Phase
$res | ConvertTo-Json -Compress
