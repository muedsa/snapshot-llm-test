# A08 marker-label bounding boxes measured from the delivered PNG pixels
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$O    = "$root\outputs\$RUN\A08"
$utf8 = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap("$O\wayfinding.png")

$CELL = 44; $GX = 48; $GY = 116; $COLS = 26; $ROWS = 18
$raw  = [System.IO.File]::ReadAllLines("$root\tmp\$RUN\A08\floor.txt")

function HexRGB([string]$hex) {
  $h = $hex.TrimStart('#')
  return ,@([Convert]::ToInt32($h.Substring(0,2),16), [Convert]::ToInt32($h.Substring(2,2),16), [Convert]::ToInt32($h.Substring(4,2),16))
}
function Near($a, $b, $tol) {
  return ([math]::Abs($a[0]-$b[0]) -le $tol -and [math]::Abs($a[1]-$b[1]) -le $tol -and [math]::Abs($a[2]-$b[2]) -le $tol)
}

$C_R1  = HexRGB '#F43F5E'
$C_R2  = HexRGB '#38BDF8'
$C_WALL= HexRGB '#3E4C66'

# label key -> colour, band y range, scan x range, x range the text is allowed to occupy
$C_GREEN = HexRGB '#34D399'
$C_AMBER = HexRGB '#FBBF24'
$C_INDI  = HexRGB '#818CF8'

$defs = @(
  @{ k='S'; c=$C_GREEN; y0=174; y1=204; x0=48;  x1=320;  col0=1; col1=5  },
  @{ k='E'; c=$C_AMBER; y0=822; y1=856; x0=940; x1=1191; col0=20; col1=24 },
  @{ k='A'; c=$C_INDI;  y0=348; y1=378; x0=48;  x1=540;  col0=1;  col1=7  },
  @{ k='B'; c=$C_INDI;  y0=216; y1=246; x0=460; x1=790;  col0=9;  col1=16 },
  @{ k='C'; c=$C_INDI;  y0=348; y1=378; x0=880; x1=1191; col0=18; col1=24 },
  @{ k='D'; c=$C_INDI;  y0=695; y1=725; x0=380; x1=619;  col0=9;  col1=16; skip=@(576,577,578,617,618,619) }
)

$TOL = 45   # tight enough that the cyan route / marker fills cannot read as label ink
$lbl = @()
foreach ($d in $defs) {
  $skipCols = @(); if ($d.ContainsKey('skip')) { $skipCols = @($d.skip) }
  $minx = 99999; $maxx = -1; $miny = 99999; $maxy = -1
  for ($y = $d.y0; $y -le $d.y1; $y++) {
    for ($x = $d.x0; $x -le $d.x1; $x++) {
      $p = $bmp.GetPixel($x, $y)
      $c = @($p.R, $p.G, $p.B)
      if (Near $c $d.c $TOL) {
        if ($skipCols -contains $x) { continue }
        if ($x -lt $minx) { $minx = $x }
        if ($x -gt $maxx) { $maxx = $x }
        if ($y -lt $miny) { $miny = $y }
        if ($y -gt $maxy) { $maxy = $y }
      }
    }
  }
  # pass B: route ink found only inside the label's own glyph box, so a route
  # legitimately terminating on the marker cell is not counted as a collision
  $routeHit = $false
  if ($maxx -ge $minx) {
    for ($y = $miny; $y -le $maxy -and -not $routeHit; $y++) {
      for ($x = $minx; $x -le $maxx; $x++) {
        $p = $bmp.GetPixel($x, $y)
        $c = @($p.R, $p.G, $p.B)
        if ((Near $c $C_R1 25) -or (Near $c $C_R2 25)) { $routeHit = $true; break }
      }
    }
  }
  # which columns does the label text actually sit over?
  $touched = @()
  for ($x = $minx; $x -le $maxx; $x++) {
    $col = [int][math]::Floor(($x - $GX) / $CELL)
    if ($touched -notcontains $col) { $touched += $col }
  }
  $wrow = [int][math]::Floor(($miny - $GY) / $CELL)
  if ($wrow -lt 0 -or $wrow -ge $ROWS) { $wrow = [int][math]::Floor(($maxy - $GY) / $CELL) }
  $wallCols = @($touched | Where-Object { $_ -lt 0 -or $_ -ge $COLS -or $raw[$wrow][$_] -eq '#' })
  $lbl += [ordered]@{
    label = $d.k
    pixel_bbox = "x=$minx..$maxx y=$miny..$maxy"
    text_width_px = ($maxx - $minx + 1)
    columns_touched = ($touched -join ',')
    allowed_columns = "$($d.col0)..$($d.col1)"
    inside_allowed = (@($touched | Where-Object { $_ -lt $d.col0 -or $_ -gt $d.col1 }).Count -eq 0)
    over_wall = ($wallCols.Count -gt 0)
    wall_columns = ($wallCols -join ',')
    route_pixels_in_band = $routeHit
  }
}
$bmp.Dispose()

$bad = @($lbl | Where-Object { -not $_.inside_allowed -or $_.over_wall -or $_.route_pixels_in_band })
foreach ($r in $lbl) {
  $flag = if ($r.inside_allowed -and -not $r.over_wall -and -not $r.route_pixels_in_band) { 'OK  ' } else { 'BAD ' }
  Write-Host ("{0}{1}  {2}  w={3}px  cols={4} (allow {5})  wall={6}{7}  route={8}" -f `
    $flag, $r.label, $r.pixel_bbox, $r.text_width_px, $r.columns_touched, $r.allowed_columns, `
    $r.over_wall, $r.wall_columns, $r.route_pixels_in_band)
}
$report = [ordered]@{
  task_id = 'A08'
  measured_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  note = 'bounding boxes of marker-label glyph pixels measured from the delivered PNG; label ink matched at TOL=45 so the cyan route, marker fills and panel colours cannot be mistaken for glyphs; route collision tested only inside each label glyph box'
  labels = $lbl
  summary = [ordered]@{ labels = $lbl.Count; violations = $bad.Count; verdict = $(if ($bad.Count -eq 0) { 'PASS' } else { 'FAIL' }) }
}
$json = $report | ConvertTo-Json -Depth 8
$json = [regex]::Replace($json, '\\u([0-9a-fA-F]{4})', { param($m) [char][int]::Parse($m.Groups[1].Value, 'HexNumber') })
[IO.File]::WriteAllText("$O\label-audit.json", $json, $utf8)
Write-Host "labels=$($lbl.Count) violations=$($bad.Count)"
