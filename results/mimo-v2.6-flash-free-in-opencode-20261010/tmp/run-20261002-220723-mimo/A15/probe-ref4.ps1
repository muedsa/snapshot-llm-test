# Fourth pass: exact ink colours used by the reference. Read-only observation.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing

$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
function Hex($c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }
function Lum($c) { (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }

# darkest / most-saturated pixel inside a box = the ink colour (edges are blended)
function InkColour($x0, $y0, $x1, $y1, [string]$mode) {
  $best = $null; $bestScore = -1.0
  for ($y = $y0; $y -lt $y1; $y++) {
    for ($x = $x0; $x -lt $x1; $x++) {
      $c = $bmp.GetPixel($x, $y)
      $l = Lum $c
      $score = 0.0
      if ($mode -eq 'dark')  { $score = 255 - $l }
      elseif ($mode -eq 'light') { $score = $l }
      elseif ($mode -eq 'sat') { $mx = [math]::Max($c.R,[math]::Max($c.G,$c.B)); $mn = [math]::Min($c.R,[math]::Min($c.G,$c.B)); $score = ($mx - $mn) }
      if ($score -gt $bestScore) { $bestScore = $score; $best = $c }
    }
  }
  return (Hex $best)
}

$rows = @(
  @{ n='sidebar brand NORTHSTAR'; x0=73;y0=38;x1=189;y1=52;   m='light' },
  @{ n='nav label Overview';      x0=63;y0=126;x1=149;y1=142; m='light' },
  @{ n='nav label Projects';      x0=63;y0=191;x1=134;y1=209; m='light' },
  @{ n='nav dot 1 (selected)';    x0=32;y0=127;x1=45;y1=141;  m='sat'   },
  @{ n='nav dot 2';               x0=32;y0=191;x1=45;y1=205;  m='light' },
  @{ n='nav dot 3';               x0=32;y0=255;x1=45;y1=269;  m='light' },
  @{ n='nav dot 4';               x0=32;y0=319;x1=45;y1=333;  m='light' },
  @{ n='logo mark fill';          x0=30;y0=33;x1=58;y1=61;    m='sat'   },
  @{ n='card PRO WORKSPACE';      x0=39;y0=770;x1=151;y1=780; m='sat'   },
  @{ n='card 12 team members';    x0=41;y0=804;x1=169;y1=817; m='light' },
  @{ n='card Manage access';      x0=39;y0=836;x1=160;y1=849; m='light' },
  @{ n='title ink';               x0=261;y0=39;x1=594;y1=69;  m='dark'  },
  @{ n='subtitle ink';            x0=261;y0=86;x1=507;y1=103; m='dark'  },
  @{ n='button label';            x0=1237;y0=56;x1=1347;y1=71; m='light'},
  @{ n='KPI label REVENUE';       x0=285;y0=161;x1=349;y1=171; m='dark' },
  @{ n='KPI value 128,400';       x0=285;y0=200;x1=432;y1=228; m='dark' },
  @{ n='KPI change +12.4%';       x0=285;y0=246;x1=341;y1=258; m='sat'  },
  @{ n='KPI change +8.1%';        x0=669;y0=246;x1=714;y1=258; m='sat'  },
  @{ n='KPI change -0.8pp';       x0=1053;y0=246;x1=1112;y1=261;m='sat' },
  @{ n='chart title Net revenue'; x0=286;y0=336;x1=414;y1=352; m='dark' },
  @{ n='chart period Apr-Sep';    x0=897;y0=338;x1=973;y1=353; m='dark' },
  @{ n='chart unit label';        x0=288;y0=376;x1=356;y1=385; m='dark' },
  @{ n='chart y tick label';      x0=300;y0=400;x1=320;y1=412; m='dark' },
  @{ n='chart month label';       x0=373;y0=561;x1=395;y1=574; m='dark' },
  @{ n='activity title';          x0=1055;y0=335;x1=1199;y1=356;m='dark' },
  @{ n='activity dot 1';          x0=1054;y0=397;x1=1064;y1=407;m='sat'  },
  @{ n='activity dot 2';          x0=1054;y0=457;x1=1064;y1=467;m='sat'  },
  @{ n='activity dot 3';          x0=1054;y0=517;x1=1064;y1=527;m='sat'  },
  @{ n='activity item text';      x0=1078;y0=395;x1=1219;y1=412;m='dark' },
  @{ n='activity time text';      x0=1078;y0=423;x1=1219;y1=433;m='dark' },
  @{ n='table title';             x0=286;y0=645;x1=453;y1=666; m='dark' },
  @{ n='table header PROJECT';    x0=299;y0=699;x1=353;y1=708; m='dark' },
  @{ n='row1 project text';       x0=299;y0=735;x1=460;y1=750; m='dark' },
  @{ n='row1 owner text';         x0=783;y0=735;x1=856;y1=747; m='dark' },
  @{ n='row1 due text';           x0=1231;y0=735;x1=1285;y1=747;m='dark' },
  @{ n='pill1 text';              x0=1035;y0=732;x1=1170;y1=754;m='dark' },
  @{ n='pill2 text';              x0=1035;y0=767;x1=1170;y1=789;m='dark' },
  @{ n='pill3 text';              x0=1035;y0=802;x1=1170;y1=824;m='dark' },
  @{ n='footer text';             x0=261;y0=867;x1=516;y1=880; m='dark' }
)
foreach ($r in $rows) {
  $c = InkColour $r.x0 $r.y0 $r.x1 $r.y1 $r.m
  Write-Output ("  {0,-26} #{1}" -f $r.n, $c)
}

# pill backgrounds (sample a pixel left of the label, inside the pill)
Write-Output '--- pill backgrounds ---'
Write-Output ("  pill1 bg #{0}" -f (Hex $bmp.GetPixel(1033, 742)))
Write-Output ("  pill2 bg #{0}" -f (Hex $bmp.GetPixel(1033, 777)))
Write-Output ("  pill3 bg #{0}" -f (Hex $bmp.GetPixel(1033, 812)))

# rounded corner radius estimate on KPI card1: find first x where border appears per row
Write-Output '--- KPI card1 top-left corner (first non-bg x per row 138..156) ---'
$s = ''
for ($y = 138; $y -lt 157; $y++) {
  for ($x = 256; $x -lt 300; $x++) {
    $c = $bmp.GetPixel($x, $y)
    if (-not ($c.R -eq 0xF3 -and $c.G -eq 0xF6 -and $c.B -eq 0xFB)) { $s += "{0}:{1} " -f $y, $x; break }
  }
}
Write-Output "  $s"

# button corner
Write-Output '--- button top-left corner (first blue x per row 43..58) ---'
$s = ''
for ($y = 43; $y -lt 59; $y++) {
  for ($x = 1180; $x -lt 1230; $x++) {
    $c = $bmp.GetPixel($x, $y)
    if ($c.B -gt 150 -and $c.B -gt ($c.R + 60)) { $s += "{0}:{1} " -f $y, $x; break }
  }
}
Write-Output "  $s"

$bmp.Dispose()
