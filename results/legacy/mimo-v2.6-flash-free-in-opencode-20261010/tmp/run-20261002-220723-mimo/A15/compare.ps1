# A15 - measure reference and reconstruction with the SAME probe windows,
# compute per-element corrections, and update placement.json.
param([Parameter(Mandatory = $true)][string]$Png)

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
$REF = Join-Path $ROOT 'tasks\A15-reference-reconstruction\inputs\reference.png'
Add-Type -AssemblyName System.Drawing

function LumOf($c) { return (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }

function InkBox($bmp, $x0, $y0, $x1, $y1, $mode) {
  $maxX = $bmp.Width - 1; $maxY = $bmp.Height - 1
  if ($x0 -lt 0) { $x0 = 0 }; if ($y0 -lt 0) { $y0 = 0 }
  if ($x1 -gt $maxX) { $x1 = $maxX }; if ($y1 -gt $maxY) { $y1 = $maxY }
  $bx = 99999; $by = 99999; $bx1 = -1; $by1 = -1
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) {
      $lum = LumOf $bmp.GetPixel($x, $y)
      $hit = $false
      if ($mode -eq 'light') { if ($lum -gt 120) { $hit = $true } }
      else { if ($lum -lt 170) { $hit = $true } }
      if ($hit) {
        if ($x -lt $bx) { $bx = $x }
        if ($x -gt $bx1) { $bx1 = $x }
        if ($y -lt $by) { $by = $y }
        if ($y -gt $by1) { $by1 = $y }
      }
    }
  }
  if ($bx1 -lt 0) { return $null }
  return [pscustomobject]@{ x = $bx; y = $by; w = ($bx1 - $bx + 1); h = ($by1 - $by + 1); right = $bx1; bottom = $by1 }
}

$el = [IO.File]::ReadAllText((Join-Path $TMP 'elements.json')) | ConvertFrom-Json
$PL = [IO.File]::ReadAllText((Join-Path $TMP 'placement.json')) | ConvertFrom-Json

$ref = New-Object System.Drawing.Bitmap($REF)
$mine = New-Object System.Drawing.Bitmap($Png)

$rows = @(); $refOut = @(); $bad = 0
foreach ($e in $el.texts) {
  $p = $PL.PSObject.Properties[$e.id].Value
  $padR = [math]::Max(20.0, ($e.rw * 0.22))
  $wx0 = [int][math]::Floor($e.rx - 10); $wy0 = [int][math]::Floor($e.ry - 10)
  $wx1 = [int][math]::Ceiling($e.rx + $e.rw + $padR); $wy1 = [int][math]::Ceiling($e.ry + $e.rh + 10)

  $rb = InkBox $ref $wx0 $wy0 $wx1 $wy1 $e.mode
  $mb = InkBox $mine $wx0 $wy0 $wx1 $wy1 $e.mode

  if ($null -eq $rb) { Write-Output ("  !! {0}: no reference ink in window" -f $e.id); $bad++; continue }
  $refOut += [ordered]@{ id = $e.id; text = $e.text; x = $rb.x; y = $rb.y; w = $rb.w; h = $rb.h; mode = $e.mode }

  if ($null -eq $mb) {
    Write-Output ("  !! {0}: no ink in reconstruction (window {1},{2}..{3},{4})" -f $e.id, $wx0, $wy0, $wx1, $wy1)
    $bad++; continue
  }

  $fsOld = [double]$p.fs
  $lr = ($mb.x - [double]$p.left) / $fsOld
  $off = ($mb.y - [double]$p.top) / $fsOld
  $dwRaw = $rb.w - $mb.w
  $fsNew = $fsOld
  # only retune the font size when the ink width is out of tolerance; small
  # differences are glyph/anti-alias noise and chasing them would break the
  # visual consistency between elements that share a style in the reference.
  if ([math]::Abs($dwRaw) -gt 8 -and $mb.w -gt 0) {
    $fsNew = $fsOld * ($rb.w / [double]$mb.w)
    if ($fsNew -lt ($fsOld * 0.55)) { $fsNew = $fsOld * 0.55 }
    if ($fsNew -gt ($fsOld * 1.80)) { $fsNew = $fsOld * 1.80 }
  }
  $fsNew = [math]::Round($fsNew, 1)
  $newLeft = [math]::Round($rb.x - ($lr * $fsNew), 1)
  $newTop = [math]::Round($rb.y - ($off * $fsNew), 1)

  $dx = $rb.x - $mb.x; $dy = $rb.y - $mb.y; $dw = $rb.w - $mb.w; $dh = $rb.h - $mb.h
  $flag = ''
  if ([math]::Abs($dx) -gt 8 -or [math]::Abs($dy) -gt 8 -or [math]::Abs($dw) -gt 8) { $flag = ' <== OUT'; $bad++ }

  $rows += ('  {0,-9} ref {1,4},{2,-4} {3,4}x{4,-3} | got {5,4},{6,-4} {7,4}x{8,-3} | d {9,3},{10,3},{11,3},{12,3} | fs {13} -> {14}{15}' -f `
    $e.id, $rb.x, $rb.y, $rb.w, $rb.h, $mb.x, $mb.y, $mb.w, $mb.h, $dx, $dy, $dw, $dh, $fsOld, $fsNew, $flag)

  $p.left = $newLeft; $p.top = $newTop; $p.fs = $fsNew
  $p.lr = [math]::Round($lr, 4); $p.off = [math]::Round($off, 4)
}

Write-Output ('--- element alignment ({0} problem elements) ---' -f $bad)
foreach ($r in $rows) { Write-Output $r }

[IO.File]::WriteAllText((Join-Path $TMP 'placement.json'), ($PL | ConvertTo-Json -Depth 6), (New-Object Text.UTF8Encoding($false)))
[IO.File]::WriteAllText((Join-Path $TMP 'refink.json'), ($refOut | ConvertTo-Json -Depth 6), (New-Object Text.UTF8Encoding($false)))

$ref.Dispose(); $mine.Dispose()
Write-Output 'placement.json + refink.json updated'
