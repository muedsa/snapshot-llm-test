param([Parameter(Mandatory=$true)][string]$Path)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::new((Resolve-Path -LiteralPath $Path).Path)
$W = $bmp.Width; $H = $bmp.Height

function Is-Ink([int]$x, [int]$y) {
  $c = $bmp.GetPixel($x, $y)
  $dr = [Math]::Abs($c.R - 248); $dg = [Math]::Abs($c.G - 250); $db = [Math]::Abs($c.B - 252)
  $m = [Math]::Max($dr, [Math]::Max($dg, $db))
  return ($m -gt 14)
}
function Band-Extent([int]$y0, [int]$y1, [int]$x0, [int]$x1) {
  $lo = -1; $hi = -1
  for ($x = $x0; $x -le $x1; $x++) {
    $hit = $false
    for ($y = $y0; $y -le $y1; $y++) { if (Is-Ink $x $y) { $hit = $true; break } }
    if ($hit) { if ($lo -lt 0) { $lo = $x }; $hi = $x }
  }
  return ,@($lo, $hi)
}
function Row-Top([int]$y0, [int]$y1, [int]$x0, [int]$x1) {
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) { if (Is-Ink $x $y) { return $y } }
  }
  return -1
}

"file = $Path   size = ${W}x${H}"
""
"title    y26-80   x0-260   left=" + (Band-Extent 26 80 0 260)[0]
"subtitle y84-114  x0-1300  left=" + (Band-Extent 84 114 0 1300)[0] + "  right=" + (Band-Extent 84 114 0 1300)[1]
"topnote  y84-114  x1300-1599  left=" + (Band-Extent 84 114 1300 1599)[0] + "  right=" + (Band-Extent 84 114 1300 1599)[1] + "   (margin from edge = " + (1599 - (Band-Extent 84 114 1300 1599)[1]) + ")"
"ycaption y156-186 x0-279   left=" + (Band-Extent 156 186 0 279)[0] + "   (title margin = " + (Band-Extent 26 80 0 260)[0] + ")"
"ycap-top y150-200 x0-100   top=" + (Row-Top 150 200 0 100)
"xtick0   y926-956 x200-400 left=" + (Band-Extent 926 956 200 400)[0] + "  right=" + (Band-Extent 926 956 200 400)[1]
"xcaption y966-996 x200-1340 left=" + (Band-Extent 966 996 200 1340)[0]
"callout  y1014-1044 x200-1340 left=" + (Band-Extent 1014 1044 200 1340)[0] + "  right=" + (Band-Extent 1014 1044 200 1340)[1]
"legend1  y966-996  x1330-1599 right=" + (Band-Extent 966 996 1330 1599)[1]
"legend2  y1014-1044 x1330-1599 right=" + (Band-Extent 1014 1044 1330 1599)[1]
""
$bmp.Dispose()
