$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$utf8 = New-Object System.Text.UTF8Encoding($false)
$suffix = ''
if ($args.Count -gt 0) { $suffix = $args[0] }
$out = New-Object System.Collections.Generic.List[string]
$out.Add(('# example line audit ({0})  limit: 94 chars / 1040px at mono fs22' -f $suffix))
$bad = 0
for ($n = 1; $n -le 4; $n++) {
  $id = ('example-0{0}' -f $n)
  $p = Join-Path $ROOT ('tmp\run-20261002-220723-mimo\A17\' + $id + $suffix + '.snapshot')
  if (!(Test-Path $p)) { $p = Join-Path $ROOT ('outputs\run-20261002-220723-mimo\A17\' + $id + '.snapshot') }
  $txt = [IO.File]::ReadAllText($p, $utf8)
  $lines = $txt -split "`r?`n"
  if ($lines.Count -gt 0 -and $lines[$lines.Count - 1] -eq '') { $lines = $lines[0..($lines.Count - 2)] }
  $out.Add('')
  $out.Add(('## {0}  lines = {1}  ({2})' -f $id, $lines.Count, (Split-Path $p -Leaf)))
  if ($lines.Count -ne 18) { $bad++; $out.Add('  <== MUST BE 18 LINES') }
  $i = 0
  foreach ($ln in $lines) {
    $i++
    $w = 0
    foreach ($ch in $ln.ToCharArray()) {
      $c = [int]$ch
      if (($c -ge 0x1100 -and $c -le 0x115F) -or ($c -ge 0x2E80 -and $c -le 0xA4CF) -or ($c -ge 0xAC00 -and $c -le 0xD7A3) -or ($c -ge 0xF900 -and $c -le 0xFAFF) -or ($c -ge 0xFE30 -and $c -le 0xFE6F) -or ($c -ge 0xFF00 -and $c -le 0xFF60) -or ($c -ge 0xFFE0 -and $c -le 0xFFE6) -or ($c -ge 0x3000 -and $c -le 0x303F) -or ($c -ge 0xFF01 -and $c -le 0xFF60)) { $w += 22 } elseif ($c -ge 0x2000 -and $c -le 0x206F -and $c -ne 0x2018 -and $c -ne 0x2019 -and $c -ne 0x201C -and $c -ne 0x201D) { $w += 11 } else { $w += 11 }
    }
    $flag = ''
    if ($w -gt 1040) { $flag = '  <== TOO WIDE'; $bad++ }
    $out.Add(('{0,3} ({1,4}px) {2}{3}' -f $i, $w, $ln, $flag))
  }
}
$out.Add('')
$out.Add(('PROBLEMS = {0}' -f $bad))
[IO.File]::WriteAllLines((Join-Path $ROOT ('tmp\run-20261002-220723-mimo\A17\example-line-audit' + $suffix + '.md')), $out.ToArray(), $utf8)
Write-Output ('wrote audit rows=' + $out.Count + ' problems=' + $bad)
