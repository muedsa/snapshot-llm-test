# A09 probe: does <Transform> accept multiple <Positioned> children (variant A),
# or must each shape carry its own Positioned>Transform>Container (variant B)?
param([string]$Ver = '01')
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$T    = "$root\tmp\$RUN\A09"
$utf8 = New-Object System.Text.UTF8Encoding($false)

# ---------------------------------------------------------------- stamp ----
$stamp = Get-Content "$root\tasks\A09-transform-atlas\inputs\stamp.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$SX = [double]$stamp.size[0]; $SY = [double]$stamp.size[1]
$PX = [double]$stamp.pivot[0]; $PY = [double]$stamp.pivot[1]

function Num([double]$v) {
  if ([math]::Abs($v) -lt 0.0000005) { return '0' }
  return $v.ToString('0.######', [System.Globalization.CultureInfo]::InvariantCulture)
}
# matrix components must all carry a decimal point or the service answers
# "Attr [matrix] value format error" (the all-integer identity matrix proved it)
function NumF([double]$v) {
  if ([math]::Abs($v) -lt 0.0000005) { return '0.0' }
  $s = $v.ToString('0.######', [System.Globalization.CultureInfo]::InvariantCulture)
  if ($s -notmatch '\.') { $s = $s + '.0' }
  return $s
}
# column-major 4x4, image coords (y down): clockwise rotation by deg
function RotM([double]$deg) {
  $r = $deg * [math]::PI / 180.0
  $c = [math]::Cos($r); $s = [math]::Sin($r)
  return ('({0},{1},0,0,{2},{3},0,0,0,0,1,0,0,0,0,1)' -f (Num $c), (Num $s), (Num (-$s)), (Num $c))
}
function Ident { return '(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)' }

# L = 2x2 linear part applied to a column vector p -> (a*p.x + b*p.y, c*p.x + d*p.y)
function ApplyL($L, [double]$x, [double]$y) {
  $a = $L[0]; $b = $L[2]; $c = $L[1]; $d = $L[3]
  $r = @()
  $r += ($a * $x + $b * $y)
  $r += ($c * $x + $d * $y)
  return $r
}

function RefBox([double]$cx, [double]$cy) {
  return "      <Positioned left=`"$(Num ($cx - $SX/2))`" top=`"$(Num ($cy - $SY/2))`" width=`"$SX`" height=`"$SY`"><Container width=`"$SX`" height=`"$SY`" color=`"#FFFFFF`" border=`"1 SOLID #C3CAD6`"/></Positioned>"
}
function Shapes {
  $b = New-Object System.Text.StringBuilder
  foreach ($r in $stamp.rectangles) {
    [void]$b.Append("        <Positioned left=`"$($r.xywh[0])`" top=`"$($r.xywh[1])`"><Container width=`"$($r.xywh[2])`" height=`"$($r.xywh[3])`" color=`"$($r.color)`"/></Positioned>`n")
  }
  $d = $stamp.dot
  $dx = [double]$d.center[0] - [double]$d.radius
  $dy = [double]$d.center[1] - [double]$d.radius
  $dd = [double]$d.radius * 2
  [void]$b.Append("        <Positioned left=`"$(Num $dx)`" top=`"$(Num $dy)`" width=`"$dd`" height=`"$dd`"><Container width=`"$dd`" height=`"$dd`" color=`"$($d.color)`" shape=`"CIRCLE`"/></Positioned>")
  return $b.ToString()
}

# ---------------- variant A: one Transform wrapping the whole stamp ----------
# <Transform> accepts exactly ONE child, so the stamp is wrapped in a plain
# (colourless) Container > Stack; every parent/child edge used here has already
# been proven in A08 (Container > Stack > Positioned, Transform > Container).
function EmitA($M, [double]$cx, [double]$cy) {
  $body = Shapes
  return @"
      <Positioned left="$(Num ($cx - $PX))" top="$(Num ($cy - $PY))" width="$SX" height="$SY">
        <Transform matrix="$M" origin="($PX,$PY)">
          <Container width="$SX" height="$SY">
            <Stack>
$body
            </Stack>
          </Container>
        </Transform>
      </Positioned>
"@
}
# --------------------------------- variant B: one Positioned per shape -------
function EmitB($M, $L, [double]$cx, [double]$cy) {
  $b = New-Object System.Text.StringBuilder
  $lv = @(ApplyL $L $PX $PY)
  $ox = $cx - $lv[0]; $oy = $cy - $lv[1]
  foreach ($r in $stamp.rectangles) {
    $sv = @(ApplyL $L ([double]$r.xywh[0]) ([double]$r.xywh[1]))
    [void]$b.Append(("      <Positioned left=`"{0}`" top=`"{1}`"><Transform matrix=`"{2}`" origin=`"(0,0)`">" -f (Num ($ox + $sv[0])), (Num ($oy + $sv[1])), $M) + "`n")
    [void]$b.Append(("        <Container width=`"{0}`" height=`"{1}`" color=`"{2}`"/>" -f $r.xywh[2], $r.xywh[3], $r.color) + "`n")
    [void]$b.Append("      </Transform></Positioned>`n")
  }
  $d = $stamp.dot
  $dd = [double]$d.radius * 2
  $sx = [double]$d.center[0] - [double]$d.radius
  $sy = [double]$d.center[1] - [double]$d.radius
  $sv = @(ApplyL $L $sx $sy)
  [void]$b.Append(("      <Positioned left=`"{0}`" top=`"{1}`" width=`"{2}`" height=`"{2}`"><Transform matrix=`"{3}`" origin=`"(0,0)`">" -f (Num ($ox + $sv[0])), (Num ($oy + $sv[1])), $dd, $M) + "`n")
  [void]$b.Append(("        <Container width=`"{0}`" height=`"{0}`" color=`"{1}`" shape=`"CIRCLE`"/>" -f $dd, $d.color) + "`n")
  [void]$b.Append("      </Transform></Positioned>`n")
  return $b.ToString()
}
# -------------------------- variant C: Transform > Stack > Positioned --------
function EmitC($M, [double]$cx, [double]$cy) {
  $body = Shapes
  return @"
      <Positioned left="$(Num ($cx - $PX))" top="$(Num ($cy - $PY))">
        <Transform matrix="$M" origin="($PX,$PY)">
          <Stack>
$body
          </Stack>
        </Transform>
      </Positioned>
"@
}

# ------------------------------------------------------------- layout -------
$W = 1240; $H = 460
$CY = 268
$cards = @(
  @{ x = 110;  label = 'identity（无变换）';  kind = 'id' },
  @{ x = 390;  label = 'A：Transform > Positioned ×4';  kind = 'A' },
  @{ x = 670;  label = 'B：4 × Positioned > Transform';  kind = 'B' },
  @{ x = 950;  label = 'C：Transform > Stack > Positioned';  kind = 'C' }
)
$DEG = 45.0
$M = RotM $DEG
$c = [math]::Cos($DEG * [math]::PI / 180.0); $s = [math]::Sin($DEG * [math]::PI / 180.0)
$L = @($c, $s, (-$s), $c)   # col-major linear: a=c b=s c=-s d=s

$sb = New-Object System.Text.StringBuilder
[void]$sb.Append("<Snapshot type=`"png`" background=`"#EEF1F6`">`n")
[void]$sb.Append("  <Container width=`"$W`" height=`"$H`">`n")
[void]$sb.Append("    <Stack>`n")
[void]$sb.Append("      <Positioned left=`"24`" top=`"20`"><Text fontSize=`"26`" height=`"1.0`" fontFamily=`"Inter,Noto Sans CJK SC`" color=`"#12161F`" fontStyle=`"BOLD`">A09 探针 · Transform 结构（45° 顺时针）</Text></Positioned>`n")
[void]$sb.Append("      <Positioned left=`"24`" top=`"58`"><Text fontSize=`"20`" height=`"1.0`" fontFamily=`"Inter,Noto Sans CJK SC`" color=`"#5A6478`">白框 = 印章未变换的 120×120 局部范围；三张旋转变体必须完全重合于白框中心</Text></Positioned>`n")
foreach ($cd in $cards) {
  [void]$sb.Append("      <Positioned left=`"$(Num ($cd.x - 125))`" top=`"120`" width=`"250`" height=`"300`"><Container width=`"250`" height=`"300`" color=`"#FFFFFF`" border=`"1 SOLID #DCE1EA`" borderRadius=`"10`"/></Positioned>`n")
  [void]$sb.Append("      <Positioned left=`"$(Num ($cd.x - 120))`" top=`"136`"><Text fontSize=`"20`" height=`"1.0`" fontFamily=`"Inter,Noto Sans CJK SC`" color=`"#12161F`">$($cd.label)</Text></Positioned>`n")
  [void]$sb.Append((RefBox $cd.x $CY) + "`n")
  switch ($cd.kind) {
    'id' { [void]$sb.Append((EmitA (Ident) $cd.x $CY) + "`n") }
    'A' { [void]$sb.Append((EmitA $M $cd.x $CY) + "`n") }
    'B' { [void]$sb.Append((EmitB $M $L $cd.x $CY) + "`n") }
    'C' { [void]$sb.Append((EmitC $M $cd.x $CY) + "`n") }
  }
}
[void]$sb.Append("    </Stack>`n  </Container>`n</Snapshot>")
$txt = $sb.ToString()
$path = "$T\probe-atlas-v$Ver.snapshot"
[IO.File]::WriteAllText($path, $txt, $utf8)
$bytes = (Get-Item $path).Length
$noBom = (([IO.File]::ReadAllBytes($path))[0..2] -join ',') -eq '60,83,110'
try { $x = [xml]$txt; "XML OK elements=$($x.SelectNodes('//*').Count)" } catch { "XML FAIL: $($_.Exception.Message)" }
Write-Host "$path ($bytes bytes) noBOM=$noBom"
