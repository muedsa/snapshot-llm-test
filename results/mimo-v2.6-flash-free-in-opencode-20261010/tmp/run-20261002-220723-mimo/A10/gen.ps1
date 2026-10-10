param([int]$Ver = 1)
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$T    = "$root\tmp\$RUN\A10"
New-Item -ItemType Directory -Force -Path $T | Out-Null

function F([double]$v) { $v.ToString('0.###', [Globalization.CultureInfo]::InvariantCulture) }

# ---------- canvas / grid -------------------------------------------------
$W = 1440; $H = 1100
$BG   = '#EEF1F6'
$INK  = '#12161F'
$SUB  = '#5A6478'
$ZB   = '#D7DCE5'
$FF   = 'Inter,Noto Sans CJK SC'
$ZW = 320; $ZH = 240          # experiment zone
$PITCH = 400
$COLX = @(160, 560, 960)      # zone left per column  (gap = 80 >= 32)
$ROWY = @(140, 560)           # cell header top per row
$AREADY = @(270, 690)         # zone top per row      (row gap = 50 >= 32)

$sb = New-Object System.Text.StringBuilder
function W([string]$s) { [void]$script:sb.Append($s) }

function Esc([string]$t) { return ($t -replace '&','&amp;' -replace '<','&lt;' -replace '>','&gt;') }

function TLine([int]$x, [int]$y, [int]$w, [int]$h, [int]$fs, [string]$col, [string]$txt, [string]$align = 'START', [string]$style = 'NORMAL') {
  $ta = ''
  if ($align -ne 'START') { $ta = ' textAlign="' + $align + '"' }
  $fmt = '<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Text fontFamily="{4}" fontSize="{5}" fontStyle="{6}" color="{7}"{8} height="1.0">{9}</Text></Positioned>'
  return ($fmt -f $x, $y, $w, $h, $FF, $fs, $style, $col, $ta, (Esc $txt))
}
function Box([int]$x, [int]$y, [int]$w, [int]$h, [string]$col, [int]$r = -1) {
  if ($r -ge 0) {
    return ('<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}" borderRadius="{5}"/></Positioned>' -f $x, $y, $w, $h, $col, $r)
  }
  return ('<Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}"/></Positioned>' -f $x, $y, $w, $h, $col)
}

# ---------- zone frame: white base + content + hairline border ------------
function Zone([int]$ax, [int]$ay, [string]$inner) {
  $base = '<Positioned left="0" top="0" width="320" height="240"><Container width="320" height="240" color="#FFFFFF"/></Positioned>'
  $edge = '<Positioned left="0" top="0" width="320" height="240"><Container width="320" height="240" border="1 SOLID ' + $ZB + '"/></Positioned>'
  return ('<Positioned left="{0}" top="{1}" width="320" height="240"><Stack>{2}{3}{4}</Stack></Positioned>' -f $ax, $ay, $base, $inner, $edge)
}

# ---------- sharp stripe pattern, opaque, fills the whole zone ------------
function StripeEls {
  $e = New-Object System.Collections.Generic.List[string]
  $e.Add('<Positioned left="0" top="0" width="320" height="240"><Container width="320" height="240" color="#FFFFFF"/></Positioned>')
  for ($i = 0; $i -lt 20; $i++) {
    $e.Add(('<Positioned left="{0}" top="0" width="8" height="240"><Container width="8" height="240" color="#94A3B8"/></Positioned>' -f ($i * 16)))
  }
  return ($e -join '')
}

# ---------- broken crosshair around the sampling point -------------------
function Marker([int]$cx, [int]$cy) {
  $n = 8; $f = 16; $t = 2
  $e = New-Object System.Collections.Generic.List[string]
  $e.Add((Box ($cx - $f) ($cy - 1) ($f - $n) $t '#111111'))   # left arm  : x 164..171
  $e.Add((Box ($cx + $n) ($cy - 1) ($f - $n) $t '#111111'))   # right arm : x 188..195
  $e.Add((Box ($cx - 1) ($cy - $f) $t ($f - $n) '#111111'))   # top arm   : y 84..91
  $e.Add((Box ($cx - 1) ($cy + $n) $t ($f - $n) '#111111'))   # bottom arm: y 108..115
  return ($e -join '')
}

# ---------- card subtree shared by 3/4 -----------------------------------
function CardStripes {
  return ('<Positioned left="-40" top="-40" width="320" height="240"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack>' + (StripeEls) + '</Stack></ImageFiltered></Positioned>')
}

# ---------- 5/6 subtree: dark rects + gaps + shadow ----------------------
function FilterBody {
  $e = New-Object System.Collections.Generic.List[string]
  $e.Add((Box 0 0 180 44 '#16202E'))            # full-width bar  -> flat edge, circle cuts it
  $e.Add((Box 0 60 76 60 '#16202E'))            # left block   (gap y 44..60)
  $e.Add((Box 104 60 76 60 '#16202E'))          # right block  (gap x 76..104, y 44..60)
  $e.Add(('<Positioned left="12" top="136" width="156" height="36"><Container width="156" height="36" color="#243447" borderRadius="6" boxShadow="0 6 12 0 #00000066"/></Positioned>'))  # gap y 120..136
  return ($e -join '')
}

# ==========================================================================
$stripe = StripeEls
$card3  = CardStripes
$card4  = '<Positioned left="-40" top="-40" width="320" height="240"><Stack>' + $stripe + '</Stack></Positioned>' +
          (TLine 24 58 192 34 24 '#0B1220' 'SHARP / BLUR' 'CENTER') +
          (Box 24 110 192 20 '#E11D48' 10)

# ---------------- zones --------------------------------------------------
$z1 = (Box 40 40 160 120 '#FF000080') + (Box 120 80 160 120 '#0000FF80') + (Marker 180 100)

$z2 = '<Positioned left="0" top="0" width="320" height="240"><Opacity opacity="0.5"><Stack clipBehavior="NONE">' +
      (Box 40 40 160 120 '#FF0000') + (Box 120 80 160 120 '#0000FF') +
      '</Stack></Opacity></Positioned>' + (Marker 180 100)

$z3 = ('<Positioned left="0" top="0" width="320" height="240"><Stack>' + $stripe + '</Stack></Positioned>') +
      '<Positioned left="40" top="40" width="240" height="160"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS"><Stack clipBehavior="NONE">' + $card3 + '</Stack></ClipRRect></Positioned>' +
      (TLine 64 98 192 34 24 '#0B1220' 'SHARP / BLUR' 'CENTER') +
      (Box 64 150 192 20 '#E11D48' 10)

$z4 = ('<Positioned left="0" top="0" width="320" height="240"><Stack>' + $stripe + '</Stack></Positioned>') +
      '<Positioned left="40" top="40" width="240" height="160"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack clipBehavior="NONE">' + $card4 + '</Stack></ImageFiltered></ClipRRect></Positioned>'

$z5 = '<Positioned left="70" top="30" width="180" height="180"><ColorFiltered color="#F6B94A" blendMode="MULTIPLY">' +
      '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack clipBehavior="NONE">' + (FilterBody) + '</Stack>' +
      '</ImageFiltered></ColorFiltered></Positioned>'

$z6 = '<Positioned left="70" top="30" width="180" height="180"><ClipOval clipBehavior="ANTI_ALIAS">' +
      '<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">' +
      '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack clipBehavior="NONE">' + (FilterBody) + '</Stack>' +
      '</ImageFiltered></ColorFiltered></ClipOval></Positioned>'

$zones = @($z1, $z2, $z3, $z4, $z5, $z6)

# ---------------- headings and descriptions ------------------------------
$C1 = [string][char]0x2460; $C2 = [string][char]0x2461; $C3 = [string][char]0x2462
$C4 = [string][char]0x2463; $C5 = [string][char]0x2464; $C6 = [string][char]0x2465

$heads = @(
  ('' + $C1 + ' 各自 50% alpha'),
  ('' + $C2 + ' Opacity(0.5) 整组'),
  ('' + $C3 + ' 只模糊背景条纹'),
  ('' + $C4 + ' 子树整体模糊'),
  ('' + $C5 + ' MULTIPLY 与高斯模糊'),
  ('' + $C6 + ' 同' + $C5 + ' 再加圆形裁剪')
)
$descs = @(
  @('红 #FF000080 蓝 #0000FF80', '蓝在上层，重叠各算一次', '采样(180,100) a=128/255'),
  @('同样两个不透明矩形',         '整组只做一次半透明',     '采样(180,100) 组a=0.5'),
  @('条纹跨过卡边 240x160',      '只对背景做 sigma=6 模糊', '卡内文字保持锐利'),
  @('同一批条纹同一张卡',         '文字与形状整棵子树模糊', '卡外条纹仍然锐利'),
  @('先 ColorFiltered(MULTIPLY)', '滤色 #F6B94A 再子树模糊', '内含透明间隙与阴影'),
  @(('' + '与' + $C5 + ' 完全相同的效果'), '再用 ClipOval 限定圆形', '裁剪边界清晰可见')
)

# ==========================================================================
W('<Snapshot type="png" background="' + $BG + '">')
W('<Container width="' + $W + '" height="' + $H + '"><Stack>')

# title band
W((TLine 0 30 1440 52 40 $INK ('看到差异，才能说用对了') 'CENTER' 'BOLD'))
W((TLine 0 88 1440 26 20 $SUB ('透明合成与滤镜语义实验板 · 6 格对照 · 滤镜 sigmaX = sigmaY = 6') 'CENTER'))

for ($i = 0; $i -lt 6; $i++) {
  $c = $i % 3
  $r = [int][math]::Floor($i / 3)
  $zx = $COLX[$c]; $rt = $ROWY[$r]; $zy = $AREADY[$r]
  W((TLine $zx $rt 320 30 24 $INK $heads[$i] 'LEFT' 'BOLD'))
  W((TLine $zx ($rt + 38) 320 26 20 $SUB $descs[$i][0]))
  W((TLine $zx ($rt + 66) 320 26 20 $SUB $descs[$i][1]))
  W((TLine $zx ($rt + 94) 320 26 20 $SUB $descs[$i][2]))
  W((Zone $zx $zy $zones[$i]))
}

# footer evidence notes
W((TLine 160 964 1120 26 20 $INK ('重叠内部采样点为实验区坐标 (180,100)；① 与 ② 的预期 / 实测 RGB 见 composite-audit.json。')))
W((TLine 160 994 1120 26 20 $SUB ('③–⑥ 逐格判定（文字是否清晰、背景是否模糊、效果是否外溢）及其依据的文档原文见 composite-audit.json。')))
W((TLine 160 1024 1120 26 20 $SUB ('128/255 ≈ 0.50196 是把 0.5 量化到 8 位 alpha 的结果，0.5 是精确值。')))
W((TLine 160 1054 1120 26 20 $SUB ('① 的蓝叠在已合成的红上；② 的蓝先在组内盖住红，再整组半透明一次。')))

W('</Stack></Container></Snapshot>')

$xml = $sb.ToString()
$out = Join-Path $T ("compositing-lab-v{0:d2}.snapshot" -f $Ver)
[System.IO.File]::WriteAllText($out, $xml, [System.Text.UTF8Encoding]::new($false))
"written $out  bytes=$($xml.Length)"
