$ErrorActionPreference = 'Stop'
try {
  & (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A21\gen-a21.ps1') -Round 3 -OutDir 'outputs\run-20261002-220723-mimo\A21\round-03' -MapPath 'tmp\run-20261002-220723-mimo\A21\layout-map-r3.json'
} catch {
  "==== ERROR ===="
  $_.Exception.Message
  "---- position ----"
  $_.InvocationInfo.PositionMessage
  "---- stack ----"
  $_.ScriptStackTrace
}