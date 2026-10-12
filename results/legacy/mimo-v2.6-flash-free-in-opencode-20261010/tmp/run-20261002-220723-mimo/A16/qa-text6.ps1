Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function Get-Kind([System.Drawing.Color]$p) {
  if ($p.B -gt 170 -and $p.R -lt 110 -and $p.G -lt 140) { return 'B' }
  if ($p.R -gt 215 -and $p.G -ge 120 -and $p.G -le 190 -and $p.B -lt 120) { return 'O' }
  $lum = 0.299*$p.R + 0.587*$p.G + 0.114*$p.B
  if ($lum -lt 200) { return 'D' }
  return '.'
}

"--- category label zones (below baseline y=516), y=520..560"
foreach ($zone in @(@{n='Q1';x0=180;x1=360}, @{n='Q2';x0=444;x2=624}, @{n='Q3';x0=708;x1=888}, @{n='Q4';x0=972;x1=1152})) {
  $x0 = $zone.x0; $x1 = if ($zone.x2) { $zone.x2 } else { $zone.x1 }
  $minX=[int]::MaxValue;$maxX=-1;$minY=[int]::MaxValue;$maxY=-1;$hasBlue=$false;$blueRows=@{}
  for ($y=520;$y -le 575;$y++) { for ($x=$x0;$x -le $x1;$x++) {
      $p=$bmp.GetPixel($x,$y); $k=Get-Kind $p
      if ($k -ne '.') { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y}
        if ($k -eq 'B') { $hasBlue=$true; if(-not $blueRows.ContainsKey($y)){$blueRows[$y]=0}; $blueRows[$y]++ } } } }
  if ($maxX -lt 0) { "  $($zone.n): none"; continue }
  "  $($zone.n): text bbox x=$minX..$maxX (center=$([int](($minX+$maxX)/2))) y=$minY..$maxY  blue=$hasBlue"
  if ($hasBlue) { "      blue row counts: " + (($blueRows.Keys | Sort-Object | ForEach-Object { "$_=$($blueRows[$_])" }) -join ' ') }
}
"  bar-group centers: Q1=$([int]((190+353)/2)) Q2=$([int]((454+617)/2)) Q3=$([int]((718+881)/2)) Q4=$([int]((982+1145)/2))"
$bmp.Dispose()
