# A09 - 12-cell transform atlas generator.
# Reads inputs/stamp.json + inputs/transforms.json, composes every transform
# about the local pivot (60,60), and emits ONE <Transform matrix=...> per cell
# wrapping the whole stamp.  The service rejects multiple children on
# <Transform> ("Tag Transform only can have one child"), so the four shapes go
# through Container > Stack > Positioned - both edges already proven in A08.
param([string]$Ver = '01')
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$TDIR = "$root\tmp\$RUN\A09"
$IN   = "$root\tasks\A09-transform-atlas\inputs"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$CULT = [System.Globalization.CultureInfo]::InvariantCulture

$stamp = Get-Content "$IN\stamp.json"      -Raw -Encoding UTF8 | ConvertFrom-Json
$tfs   = Get-Content "$IN\transforms.json" -Raw -Encoding UTF8 | ConvertFrom-Json

$SX = [double]$stamp.size[0]; $SY = [double]$stamp.size[1]
$PX = [double]$stamp.pivot[0]; $PY = [double]$stamp.pivot[1]

# --------------------------------------------------------------- numbers ----
function Num([double]$v) {
  if ([math]::Abs($v) -lt 0.0000005) { return '0' }
  return $v.ToString('0.######', $CULT)
}
function NumZ([double]$v) {
  if ([math]::Abs($v - [math]::Round($v)) -lt 0.0000005) { return ([int][math]::Round($v)).ToString($CULT) }
  return (Num $v)
}
# column-major 4x4 tuple - must be parenthesised, exactly like the proven A08
# arrows: matrix="(a,c,0,0, b,d,0,0, 0,0,1,0, 0,0,0,1)"
function MatStr([double]$a, [double]$b, [double]$c, [double]$d) {
  return ('({0},{1},0,0,{2},{3},0,0,0,0,1,0,0,0,0,1)' -f (Num $a), (Num $c), (Num $b), (Num $d))
}
function MatIdent { return '(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)' }

# row-major 2x2 linear part:  p' = (a*x + b*y, c*x + d*y)
function Lrot([double]$deg) {
  $r = $deg * [math]::PI / 180.0
  return ,@([math]::Cos($r), (-[math]::Sin($r)), [math]::Sin($r), [math]::Cos($r))
}
function Lident { return ,@(1.0, 0.0, 0.0, 1.0) }
# compose: result applies $m1 first, then $m2   (result = m2 * m1)
function Lmul($m1, $m2) {
  $a1 = [double]$m1[0]; $b1 = [double]$m1[1]; $c1 = [double]$m1[2]; $d1 = [double]$m1[3]
  $a2 = [double]$m2[0]; $b2 = [double]$m2[1]; $c2 = [double]$m2[2]; $d2 = [double]$m2[3]
  $r = @(
    ($a2 * $a1 + $b2 * $c1), ($a2 * $b1 + $b2 * $d1),
    ($c2 * $a1 + $d2 * $c1), ($c2 * $b1 + $d2 * $d1)
  )
  return ,$r
}
function Lapply($m, [double]$x, [double]$y) {
  $a = [double]$m[0]; $b = [double]$m[1]; $c = [double]$m[2]; $d = [double]$m[3]
  return ,@(($a * $x + $b * $y), ($c * $x + $d * $y))
}

# ------------------------------------------------------------ operations ----
function OpLinear($name, $arg) {
  switch ($name) {
    'rotate_clockwise_deg' { return (Lrot ([double]$arg)) }
    'mirror_horizontal'    { return ,@(-1.0, 0.0, 0.0, 1.0) }
    'mirror_vertical'      { return ,@(1.0, 0.0, 0.0, -1.0) }
    'scale_uniform'        { return ,@([double]$arg, 0.0, 0.0, [double]$arg) }
    'scale_xy'             { return ,@([double]$arg[0], 0.0, 0.0, [double]$arg[1]) }
    default { throw "unknown operation $name" }
  }
}
function OpShort($name, $arg, [bool]$first) {
  switch ($name) {
    'rotate_clockwise_deg' {
      $v = NumZ ([double]$arg)
      if ($first) { return "顺时针 $v°" } else { return "旋转$v°" }
    }
    'mirror_horizontal' { return '左右镜像' }
    'mirror_vertical'   { return '上下镜像' }
    'scale_uniform'     { return "等比缩放 $(NumZ ([double]$arg))" }
    'scale_xy'          { return "缩放 $(NumZ ([double]$arg[0]))×$(NumZ ([double]$arg[1]))" }
    default { return [string]$name }
  }
}

# ------------------------------------------------------------ transforms ----
$TIDS = @(); $TL = @{}; $TNAME = @{}
foreach ($tf in $tfs) {
  $L = Lident
  $names = @()
  for ($k = 0; $k -lt $tf.operations.Count; $k++) {
    $op = $tf.operations[$k]
    $L  = Lmul $L (OpLinear $op[0] $op[1])
    $names += OpShort $op[0] $op[1] ($tf.operations.Count -eq 1)
  }
  $TIDS += $tf.id
  $TL[$tf.id] = $L
  $TNAME[$tf.id] = ($names -join [string][char]0x2192)   # →
}
if ($TIDS.Count -ne 12) { throw "expected 12 transforms, got $($TIDS.Count)" }

# ---------------------------------------------------------------- layout ----
$W = 1600; $H = 1200
$CW = 300; $CH = 250; $GAP = 32; $COLS = 4; $ROWS = 3
$BW = $COLS * $CW + ($COLS - 1) * $GAP          # 1296
$BH = $ROWS * $CH + ($ROWS - 1) * $GAP          # 814
$X0 = [int][math]::Floor(($W - $BW) / 2)        # 152
$Y0 = [int][math]::Floor(($H - $BH) / 2)        # 193

$BG     = '#EEF1F6'; $INK = '#12161F'; $SUB = '#5A6478'; $MUTE = '#7A8496'
$CELLBG = '#FFFFFF'; $CELLBR = '#DCE1EA'
$REFBG  = '#F7F9FC'; $REFBR = '#D3D9E3'
$GUIDE  = '#C9D0DC'; $TICK = '#A9B2C2'
$FF     = 'Inter,Noto Sans CJK SC'

function Txt([int]$l, [int]$t, [int]$fs, [string]$col, [string]$txt) {
  return ('<Positioned left="{0}" top="{1}"><Text fontSize="{2}" height="1.0" fontFamily="{3}" color="{4}">{5}</Text></Positioned>' -f $l, $t, $fs, $FF, $col, $txt)
}
function TxtB([int]$l, [int]$t, [int]$fs, [string]$col, [string]$txt) {
  return ('<Positioned left="{0}" top="{1}"><Text fontSize="{2}" height="1.0" fontFamily="{3}" color="{4}" fontStyle="BOLD">{5}</Text></Positioned>' -f $l, $t, $fs, $FF, $col, $txt)
}
function Box([int]$l, [int]$t, [int]$w, [int]$h, [string]$col, [string]$br) {
  $a = ''; if ($br -ne '') { $a = ' border="' + $br + '"' }
  $ra = ''; if ($w -ge 20 -and $h -ge 20) { $ra = ' borderRadius="8"' }
  return ('<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}"{5}{6}/></Positioned>' -f $l, $t, $w, $h, $col, $a, $ra)
}
function LineH([int]$l, [int]$t, [int]$w, [string]$col) {
  return ('<Positioned left="{0}" top="{1}" width="{2}" height="1"><Container width="{2}" height="1" color="{3}"/></Positioned>' -f $l, $t, $w, $col)
}
function LineV([int]$l, [int]$t, [int]$h, [string]$col) {
  return ('<Positioned left="{0}" top="{1}" width="1" height="{2}"><Container width="1" height="{2}" color="{3}"/></Positioned>' -f $l, $t, $h, $col)
}

# ------------------------------------------------------------------ emit ----
$sb = New-Object System.Text.StringBuilder
[void]$sb.Append('<Snapshot type="png" background="' + $BG + '">')
[void]$sb.Append('<Container width="' + $W + '" height="' + $H + '"><Stack>')

# ---- title band (outside the cell block) ----
[void]$sb.Append((TxtB 40 40 40 $INK '十二个非对称图形变换标本'))
[void]$sb.Append((Txt 40 96 24 $SUB '1600×1200 · 4 列 × 3 行 · 每格 300×250 · 格间距 32 · 印章 120×120 · 局部变换中心 (60,60)'))
[void]$sb.Append((Txt 40 136 22 $MUTE '每格给出编号与操作短名；灰色刻度线每 20 局部单位一格，细框是印章未变换的 120×120 范围。'))

# ---- 12 cells ----
for ($i = 0; $i -lt $TIDS.Count; $i++) {
  $id  = $TIDS[$i]
  $col = $i % $COLS
  $row = [int][math]::Floor($i / $COLS)
  $cx0 = $X0 + $col * ($CW + $GAP)
  $cy0 = $Y0 + $row * ($CH + $GAP)
  $mx  = $cx0 + [int]($CW / 2)
  $my  = $cy0 + [int]($CH / 2)
  $L   = $TL[$id]

  [void]$sb.Append((Box $cx0 $cy0 $CW $CH $CELLBG ('1 SOLID ' + $CELLBR)))

  # --- tick guide: reference box, cross hair, 20-unit ticks (under the stamp)
  [void]$sb.Append((Box ($mx - 60) ($my - 60) 120 120 $REFBG ('1 SOLID ' + $REFBR)))
  [void]$sb.Append((LineH ($cx0 + 16) $my ($CW - 32) $GUIDE))
  [void]$sb.Append((LineV $mx ($cy0 + 40) ($CH - 60) $GUIDE))
  for ($k = -4; $k -le 4; $k++) {
    if ($k -eq 0) { continue }
    $off = $k * 20
    [void]$sb.Append((LineV ($mx + $off) ($my - 4) 8 $TICK))
    [void]$sb.Append((LineH $mx ($my + $off) 8 $TICK))
  }
  [void]$sb.Append((LineH ($mx - 7) $my 15 $TICK))
  [void]$sb.Append((LineV $mx ($my - 7) 15 $TICK))

  # --- header: 编号 + 操作短名, one line so the stamp never collides ---
  [void]$sb.Append((TxtB ($cx0 + 16) ($cy0 + 10) 22 $INK $id))
  [void]$sb.Append((Txt ($cx0 + 70) ($cy0 + 10) 22 $SUB $TNAME[$id]))

  # --- the stamp: ONE Transform carrying the composed matrix ---
  if (([math]::Abs($L[0] - 1) -lt 1e-12) -and ([math]::Abs($L[1]) -lt 1e-12) -and ([math]::Abs($L[2]) -lt 1e-12) -and ([math]::Abs($L[3] - 1) -lt 1e-12)) {
    $ms = MatIdent
  } else {
    $ms = MatStr ([double]$L[0]) ([double]$L[1]) ([double]$L[2]) ([double]$L[3])
  }

  $shapeXml = New-Object System.Text.StringBuilder
  foreach ($r in $stamp.rectangles) {
    [void]$shapeXml.Append(('<Positioned left="{0}" top="{1}"><Container width="{2}" height="{3}" color="{4}"/></Positioned>' -f $r.xywh[0], $r.xywh[1], $r.xywh[2], $r.xywh[3], $r.color))
  }
  $dd = [double]$stamp.dot.radius * 2
  $dx = [double]$stamp.dot.center[0] - [double]$stamp.dot.radius
  $dy = [double]$stamp.dot.center[1] - [double]$stamp.dot.radius
  [void]$shapeXml.Append(('<Positioned left="{0}" top="{1}" width="{2}" height="{2}"><Container width="{2}" height="{2}" color="{3}" shape="CIRCLE"/></Positioned>' -f (Num $dx), (Num $dy), $dd, $stamp.dot.color))

  $head = ('<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Transform matrix="{4}" origin="({5},{6})"><Container width="{2}" height="{3}"><Stack>' -f (Num ($mx - $PX)), (Num ($my - $PY)), (Num $SX), (Num $SY), $ms, (Num $PX), (Num $PY))
  [void]$sb.Append($head + $shapeXml.ToString() + '</Stack></Container></Transform></Positioned>')
}

# ---- legend band (outside the cell block) ----
[void]$sb.Append((TxtB 40 1026 24 $INK '图例与说明'))
$ly = 1068
$items = @(
  @{ x = 40;   kind = 'rect';  col = $stamp.rectangles[0].color; label = '红矩形 28×92' },
  @{ x = 260;  kind = 'rect';  col = $stamp.rectangles[1].color; label = '蓝矩形 68×28' },
  @{ x = 480;  kind = 'rect';  col = $stamp.rectangles[2].color; label = '黄矩形 40×28' },
  @{ x = 700;  kind = 'dot';   col = $stamp.dot.color;           label = '黑圆点 r8' },
  @{ x = 880;  kind = 'tick';  col = $TICK;                      label = '刻度线 每 20 单位' },
  @{ x = 1160; kind = 'cross'; col = $INK;                       label = '变换中心 局部(60,60)' }
)
foreach ($it in $items) {
  $lx = [int]$it.x
  switch ($it.kind) {
    'rect'  { [void]$sb.Append((Box $lx $ly 26 26 $it.col '')) }
    'dot'   { [void]$sb.Append(('<Positioned left="{0}" top="{1}" width="26" height="26"><Container width="26" height="26" color="{2}" shape="CIRCLE"/></Positioned>' -f $lx, $ly, $it.col)) }
    'tick'  { [void]$sb.Append((LineH $lx ($ly + 12) 26 $it.col)) }
    'cross' { [void]$sb.Append((LineH ($lx + 6) ($ly + 13) 14 $it.col)); [void]$sb.Append((LineV ($lx + 13) ($ly + 6) 14 $it.col)) }
  }
  [void]$sb.Append((Txt ($lx + 36) $ly 22 $SUB $it.label))
}
[void]$sb.Append((Txt 40 1104 22 $SUB '操作按 transforms.json 列表顺序逐步作用，每一步都围绕局部 (60,60)；最终局部中心放到每格中心。'))
[void]$sb.Append((Txt 40 1138 22 $SUB '像素坐标 x 向右、y 向下，因此顺时针按图像方向；mirror_horizontal 为左右镜像，mirror_vertical 为上下镜像。'))
[void]$sb.Append((Txt 40 1172 22 $MUTE '各格主体的最终组合变换由 Transform.matrix（列主序 4×4）表达，形状坐标未手改，圆点随同变换；T07 与 T08 顺序相反，结果不同。'))

[void]$sb.Append('</Stack></Container></Snapshot>')

$xml = $sb.ToString()
$path = "$TDIR\transform-atlas-v$Ver.snapshot"
[IO.File]::WriteAllText($path, $xml, $utf8)

$bytes = (Get-Item $path).Length
$first0 = ([IO.File]::ReadAllBytes($path))[0]
$noBom = ($first0 -eq 60)
$ok = $false; $el = 0
try { $x = [xml]$xml; $el = $x.SelectNodes('//*').Count; $ok = $true } catch { Write-Host "XML FAIL: $($_.Exception.Message)" }
Write-Host $path
Write-Host "bytes=$bytes noBOM=$noBom xmlOK=$ok elements=$el transforms=$($TIDS.Count)"
foreach ($id in $TIDS) {
  $q = $TL[$id]
  Write-Host ("  {0}  {1,-18} L=({2},{3},{4},{5})  {6}" -f $id, $TNAME[$id], (Num ([double]$q[0])), (Num ([double]$q[1])), (Num ([double]$q[2])), (Num ([double]$q[3])), (MatStr ([double]$q[0]) ([double]$q[1]) ([double]$q[2]) ([double]$q[3])))
}
if (-not $ok) { exit 1 }
