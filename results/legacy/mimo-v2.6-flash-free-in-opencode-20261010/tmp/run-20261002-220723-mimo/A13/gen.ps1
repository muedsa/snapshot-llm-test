# A13 brand system generator - ONE geometric rule set -> symbol / banner / poster.
# The symbol geometry lives here once (Get-Bars) and is re-emitted at every scale,
# so banner and poster contain the mark built from the same DSL rules rather than
# an embedded rendered PNG.
param(
  [string]$Mode = 'all'     # 'all' | 'final' | 'thumb'
)
$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$OUT = "outputs\$RUN\A13"
$T   = "tmp\$RUN\A13"
New-Item -ItemType Directory -Force -Path $OUT | Out-Null
New-Item -ItemType Directory -Force -Path $T   | Out-Null

$FAM  = 'Noto Sans CJK SC,Noto Sans CJK JP'
$MONO = 'Noto Sans Mono CJK SC'

# ---------------------------------------------------------------- palette -----
$BG    = '#0B1220'
$TEXT  = '#F8FAFC'
$MUTED = '#9FB0CB'
$HAIR  = '#23324C'
$AMBER = '#F6B94A'
$CYAN  = '#38BDF8'
$BLACK = '#000000'
# 10% alpha variants of the same two hues (background echo of the mark)
$CYAN10  = '#38BDF81A'
$AMBER10 = '#F6B94A1A'

# --------------------------------------------------- symbol geometry (512) ----
# chosen direction: A "three layered light beams"
#   beam   : rounded bar 256 x 88, corner radius 44 (= half thickness -> pill)
#   axis   : 45 deg, rotated about the beam centre
#   spacing: 122 along the "\" diagonal -> 34 px clear channel between beams
#   centres: (c + s*122*0.7071, c + s*122*0.7071), s = -1, 0, +1
$MATRIX = '(0.70710678,-0.70710678,0,0,0.70710678,0.70710678,0,0,0,0,1,0,0,0,0,1)'

function NF([double]$v) { return $v.ToString('0.##', [cultureinfo]::InvariantCulture) }

# Emits the three beams scaled into a box of $box px whose top-left is ($ox,$oy).
function Get-Bars {
  param([double]$box, [double]$ox, [double]$oy, [string]$cA, [string]$cB, [string]$cC)
  $k   = $box / 512.0
  $L   = 256.0 * $k
  $TH  =  88.0 * $k
  $R   =  44.0 * $k
  $off = 122.0 * $k * 0.70710678
  $cx0 = $ox + $box / 2.0
  $cy0 = $oy + $box / 2.0
  $cols = @($cA, $cB, $cC)
  $sgn  = @(-1, 0, 1)
  $parts = New-Object System.Collections.Generic.List[string]
  # NOTE: the rotation origin must be the beam CENTRE (L/2, TH/2). Using the box
  # size instead translated every beam by (+6.4, +103.4) px and clipped the mark
  # against the canvas edge - caught by verify.ps1 M01/S01, fixed here.
  $hL = NF ($L / 2.0); $hT = NF ($TH / 2.0)
  $fmt = '<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Transform matrix="{4}" origin="({5},{6})"><Container width="{2}" height="{3}" borderRadius="{7}" color="{8}"/></Transform></Positioned>'
  for ($i = 0; $i -lt 3; $i++) {
    $cx   = $cx0 + $sgn[$i] * $off
    $cy   = $cy0 + $sgn[$i] * $off
    $left = $cx - $L / 2.0
    $top  = $cy - $TH / 2.0
    $parts.Add(($fmt -f (NF $left), (NF $top), (NF $L), (NF $TH), $MATRIX, $hL, $hT, (NF $R), $cols[$i]))
  }
  return ($parts -join '')
}

function Write-Utf8([string]$path, [string]$text) {
  [IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))
}

function Save-Dsl([string]$name, [string]$body) {
  $p = Join-Path $T "$name.snapshot"
  Write-Utf8 $p $body
  $b = [IO.File]::ReadAllBytes($p)
  $bom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
  Write-Output ("  wrote {0,-34} {1,6} B  BOM={2}" -f "$name.snapshot", $b.Length, $bom)
  return $p
}

# helper: a Text line inside its own Positioned box
function Text-Line {
  param([string]$s, [string]$fam, [double]$size, [string]$color,
        [double]$l, [double]$t, [double]$w, [string]$align = 'LEFT')
  $h = [math]::Round($size * 1.2, 2)
  $a = ''
  if ($align -ne 'LEFT') { $a = ' textAlign="' + $align + '"' }
  $fmt = '<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Text fontFamily="{4}" fontSize="{5}" color="{6}"{7} height="1.2"><Raw><![CDATA[{8}]]></Raw></Text></Positioned>'
  return ($fmt -f (NF $l), (NF $t), (NF $w), (NF $h), $fam, (NF $size), $color, $a, $s)
}

# ================================================================== outputs ====
if ($Mode -eq 'all' -or $Mode -eq 'final') {

  # --- 1. transparent colour symbol -------------------------------------
  $body = '<Snapshot type="png" background="#00000000">' +
          '<Container width="512" height="512"><Stack>' +
          (Get-Bars 512 0 0 $CYAN $AMBER $CYAN) +
          '</Stack></Container></Snapshot>'
  Save-Dsl 'symbol-color' $body | Out-Null

  # --- 2. transparent pure-black symbol (identical geometry) ------------
  $body = '<Snapshot type="png" background="#00000000">' +
          '<Container width="512" height="512"><Stack>' +
          (Get-Bars 512 0 0 $BLACK $BLACK $BLACK) +
          '</Stack></Container></Snapshot>'
  Save-Dsl 'symbol-black' $body | Out-Null

  # --- 3. brand banner 1200x400 (mark regenerated from Get-Bars) --------
  $title = '叠光 Layerlight'
  $tag   = '把复杂信息，组织成清晰画面'
  $banner = '<Snapshot type="png" background="' + $BG + '">' +
    '<Container width="1200" height="400" color="' + $BG + '"><Stack>' +
    # quiet echo of the mark behind the copy (same geometry, 10% alpha)
    (Get-Bars 300 872 48 $CYAN10 $AMBER10 $CYAN10) +
    # amber kicker rule
    '<Positioned left="96" top="96" width="72" height="6">' +
    '<Container width="72" height="6" borderRadius="3" color="' + $AMBER + '"/></Positioned>' +
    # the mark itself
    (Get-Bars 176 96 112 $CYAN $AMBER $CYAN) +
    # divider
    '<Positioned left="336" top="96" width="1" height="208">' +
    '<Container width="1" height="208" color="' + $HAIR + '"/></Positioned>' +
    # wordmark + tagline
    (Text-Line $title $FAM 56 $TEXT 392 132 740) +
    (Text-Line $tag   $FAM 28 $MUTED 392 226 740) +
    '</Stack></Container></Snapshot>'
  Save-Dsl 'brand-banner' $banner | Out-Null

  # --- 4. launch poster 1080x1350 (independent composition) ------------
  #  vertical stack: rule / large mark / wordmark / tagline / badge / date / url
  $poster = '<Snapshot type="png" background="' + $BG + '">' +
    '<Container width="1080" height="1350" color="' + $BG + '"><Stack>' +
    '<Positioned left="0" top="0" width="1080" height="8">' +
    '<Container width="1080" height="8" color="' + $AMBER + '"/></Positioned>' +
    (Get-Bars 360 360 144 $CYAN $AMBER $CYAN) +
    (Text-Line $title $FAM 84  $TEXT  90 584 900 'CENTER') +
    (Text-Line $tag   $FAM 36  $MUTED 90 710 900 'CENTER') +
    # OPEN BETA badge: pill + centred label (two siblings, no text inside Container)
    '<Positioned left="396" top="832" width="288" height="64">' +
    '<Container width="288" height="64" borderRadius="32" color="' + $AMBER + '"/></Positioned>' +
    (Text-Line 'OPEN BETA' $MONO 30 $BG 396 846 288 'CENTER') +
    (Text-Line '2026.11.07 · ONLINE' $MONO 34 $TEXT 90 962 900 'CENTER') +
    '<Positioned left="440" top="1064" width="200" height="1">' +
    '<Container width="200" height="1" color="' + $HAIR + '"/></Positioned>' +
    (Text-Line 'layerlight.example.org' $MONO 28 $MUTED 90 1116 900 'CENTER') +
    '</Stack></Container></Snapshot>'
  Save-Dsl 'launch-poster' $poster | Out-Null
}

if ($Mode -eq 'all' -or $Mode -eq 'thumb') {
  # native 32x32 service render of the same geometry (check preview, temp only)
  $body = '<Snapshot type="png" background="#00000000">' +
          '<Container width="32" height="32"><Stack>' +
          (Get-Bars 32 0 0 $CYAN $AMBER $CYAN) +
          '</Stack></Container></Snapshot>'
  Save-Dsl 'symbol-color-native32' $body | Out-Null
}

Write-Output "gen.ps1 -Mode $Mode done"
