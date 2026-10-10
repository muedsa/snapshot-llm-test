param(
  [string]$OutDsl = "tmp\run-20261002-220723-mimo\A05\v01.snapshot",
  [string]$OutJson = "outputs\run-20261002-220723-mimo\A05\normalized-data.json"
)
$ErrorActionPreference = 'Stop'
$Inv = [System.Globalization.CultureInfo]::InvariantCulture
$enc = New-Object System.Text.UTF8Encoding($false)

function F([double]$n) { $n.ToString('0.####', $Inv) }
function EW([string]$t, [double]$fs) {
  $w = 0.0
  foreach ($ch in $t.ToCharArray()) { if ([int]$ch -ge 0x1100) { $w += $fs } else { $w += $fs * 0.55 } }
  $w
}
function Segs($arr) {
  $res = @(); $cur = @()
  for ($i = 0; $i -lt $arr.Count; $i++) {
    if ($null -eq $arr[$i]) { if ($cur.Count -gt 0) { $res += , $cur; $cur = @() } }
    else { $cur += $i }
  }
  if ($cur.Count -gt 0) { $res += , $cur }
  return , $res
}

# ---------------- source data (readings.csv) ----------------
$times = @('08:00','08:10','08:35','09:00','09:15','09:40','10:10','10:50','11:00','11:40','12:10','12:30')
$offs  = @(0,10,35,60,75,100,130,170,180,220,250,270)
$temp  = @(19.2,19.6,20.1,21.0,$null,21.9,22.3,23.1,22.8,$null,22.0,21.7)
$hum   = @(41,40,39,38,37,$null,35,34,35,36,37,38)
$pres  = @(0.2,0.4,0.7,1.1,1.3,-0.2,-0.8,-0.3,0.1,0.6,0.3,0.0)

# ---------------- canvas geometry ----------------
$PX0 = 124.0; $PX1 = 1372.0; $PW = $PX1 - $PX0
$PH  = 124.0
$SPAN = 270.0
$scale = $PW / $SPAN
$PANEL_X = 40.0; $PANEL_W = 1360.0; $PANEL_H = 206.0
$PA = 196.0; $PB = 410.0; $PC = 624.0
$p1A = $PA + 164.0; $p1B = $PB + 164.0; $p1C = $PC + 164.0
$loT = 19.0; $hiT = 24.0
$loH = 33.0; $hiH = 42.0
$loP = -1.0; $hiP = 1.5

function X([double]$t) { $script:PX0 + $t * $script:scale }
function Y([double]$v, [double]$lo, [double]$hi, [double]$p1) { $p1 - (($v - $lo) / ($hi - $lo)) * $script:PH }

$C_TEMP = '#38BDF8'; $C_HUM = '#F59E0B'; $C_PRES = '#A78BFA'
$C_PANEL = '#111A2B'; $C_CARD = '#151F33'
$C_GRID = '#28374D'; $C_AXIS = '#334155'; $C_TICK = '#475569'
$C_T1 = '#F8FAFC'; $C_T2 = '#CBD5E1'; $C_T3 = '#94A3B8'; $C_T4 = '#64748B'
$C_NEG = '#F87171'; $C_NEGT = '#FCA5A5'
$FONT = 'Inter,Noto Sans CJK SC'

$sb = New-Object System.Text.StringBuilder
function L([string]$s) { [void]$script:sb.AppendLine($s) }
function Rect([double]$x, [double]$y, [double]$w, [double]$h, [string]$col, [string]$extra = '') {
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{3}"><Container width="{2}" height="{3}" color="{4}"{5}/></Positioned>' -f (F $x), (F $y), (F $w), (F $h), $col, $extra)
}
function Txt([double]$x, [double]$y, [string]$t, [double]$fs, [string]$col, [string]$extra = '') {
  L ('      <Positioned left="{0}" top="{1}"><Text fontSize="{2}" height="1.0" fontFamily="{3}" color="{4}"{5}>{6}</Text></Positioned>' -f (F $x), (F $y), (F $fs), $FONT, $col, $extra, $t)
}
function TxtC([double]$cx, [double]$y, [string]$t, [double]$fs, [string]$col) {
  $w = EW $t $fs
  Txt ($cx - $w / 2) $y $t $fs $col ''
}
function Seg([double]$x1, [double]$y1, [double]$x2, [double]$y2, [double]$th, [string]$col) {
  $dx = $x2 - $x1; $dy = $y2 - $y1
  $len = [Math]::Sqrt($dx * $dx + $dy * $dy)
  if ($len -lt 0.05) { return }
  $c = $dx / $len; $s = $dy / $len
  $top = $y1 - $th / 2
  $m = '({0},{1},0,0,{2},{3},0,0,0,0,1,0,0,0,0,1)' -f (F $c), (F $s), (F (-$s)), (F $c)
  L ('      <Positioned left="{0}" top="{1}">' -f (F $x1), (F $top))
  L ('        <Transform matrix="{0}" origin="(0,{1})">' -f $m, (F ($th / 2)))
  L ('          <Container width="{0}" height="{1}" color="{2}"/>' -f (F $len), (F $th), $col)
  L ('        </Transform>')
  L ('      </Positioned>')
}
function Dot([double]$cx, [double]$cy, [double]$d, [string]$col) {
  L ('      <Positioned left="{0}" top="{1}" width="{2}" height="{2}"><Container width="{2}" height="{2}" color="{3}" shape="CIRCLE"/></Positioned>' -f (F ($cx - $d / 2)), (F ($cy - $d / 2)), (F $d), $col)
}

# ================= header =================
L '<Snapshot type="png" background="#0B1220">'
L '  <Container width="1440" height="1000">'
L '    <Stack>'
Txt 40 24 '实验舱 · 08:00–12:30' 36 $C_T1
Txt 40 66 '三联趋势报告 · 不规则采样与缺测（空单元格＝缺测，不是 0）｜数据源 readings.csv · 单位：°C、%、kPa' 20 $C_T3

# ================= legend =================
$ly = 96.0; $lcy = 106.0
$lx = 40.0; $gap = 26.0
$legend = @(
  @{ k = 'bar'; c = $C_TEMP; t = '温度' },
  @{ k = 'bar'; c = $C_HUM; t = '相对湿度' },
  @{ k = 'bar'; c = $C_PRES; t = '压差' },
  @{ k = 'dot'; c = $C_T1; t = '有效采样点' },
  @{ k = 'dash'; c = $C_T3; t = '缺测（该时点无读数）' },
  @{ k = 'broken'; c = $C_T2; t = '断线（缺测处不连接、不插值）' }
)
foreach ($it in $legend) {
  $sw = 0.0
  if ($it.k -eq 'bar') { Rect $lx ($lcy - 2) 26 4 $it.c ''; $sw = 34 }
  elseif ($it.k -eq 'dot') { Dot ($lx + 5) $lcy 10 $it.c; $sw = 18 }
  elseif ($it.k -eq 'dash') { Txt $lx $ly '—' 20 $it.c ''; $sw = 28 }
  else {
    Rect $lx ($lcy - 1.5) 18 3 $it.c ''
    Rect ($lx + 28) ($lcy - 1.5) 18 3 $it.c ''
    $sw = 54
  }
  Txt ($lx + $sw) $ly $it.t 20 $C_T2 ''
  $lx += $sw + (EW $it.t 20) + $gap
}

# ================= top summary cards =================
$cards = @(
  @{ n = '温度 °C'; ok = 10; mi = '19.2'; mat = '08:00'; ma = '23.1'; mat2 = '10:50' },
  @{ n = '相对湿度 %'; ok = 11; mi = '34'; mat = '10:50'; ma = '41'; mat2 = '08:00' },
  @{ n = '压差 kPa'; ok = 12; mi = '-0.8'; mat = '10:10'; ma = '1.3'; mat2 = '09:15' }
)
$cardY = 124.0; $cardH = 64.0; $cardW = 440.0
for ($i = 0; $i -lt 3; $i++) {
  $cx = 40.0 + $i * 460.0
  $c = $cards[$i]
  Rect $cx $cardY $cardW $cardH $C_CARD ' borderRadius="12"'
  Txt ($cx + 16) ($cardY + 8) $c.n 24 $C_T1 ''
  $rt = '有效 {0} / 12 · 缺测 {1}' -f $c.ok, (12 - $c.ok)
  Txt ($cx + $cardW - 16 - (EW $rt 20)) ($cardY + 12) $rt 20 $C_T3 ''
  $l2 = '最小 {0}（{1}）　最大 {2}（{3}）' -f $c.mi, $c.mat, $c.ma, $c.mat2
  Txt ($cx + 16) ($cardY + 36) $l2 20 $C_T2 ''
}

# ================= panel chrome + axes =================
$gridTimes = @(0, 60, 120, 180, 240, 270)
$gridLabels = @('08:00', '09:00', '10:00', '11:00', '12:00', '12:30')

function Panel([double]$pY, [string]$title, [string]$rightTxt) {
  Rect $PANEL_X $pY $PANEL_W $PANEL_H $C_PANEL ' borderRadius="12"'
  Txt 60 ($pY + 6) $title 24 $C_T1 ''
  Txt ($PX1 + 8 - (EW $rightTxt 18)) ($pY + 9) $rightTxt 18 $C_T4 ''
}
function Axis([double]$pY, [double]$lo, [double]$hi, [array]$ticks, [bool]$isPressure) {
  $p0 = $pY + 40.0; $p1 = $pY + 164.0
  foreach ($v in $ticks) {
    $gy = $p1 - (($v - $lo) / ($hi - $lo)) * $PH
    $isZero = $isPressure -and [Math]::Abs($v) -lt 1e-9
    if ($isZero) { Rect $PX0 $gy $PW 2 $C_T3 '' } else { Rect $PX0 $gy $PW 1 $C_GRID '' }
    if ($isPressure) { $lab = $v.ToString('0.0', $Inv) } else { $lab = $v.ToString('0', $Inv) }
    $col = if ($isZero) { $C_T1 } else { $C_T4 }
    $w = EW $lab 18
    Txt (116 - $w) ($gy - 9) $lab 18 $col ''
  }
  foreach ($t in $gridTimes) { $gx = X $t; Rect $gx $p0 1 $PH $C_GRID '' }
  Rect $PX0 $p1 $PW 1 $C_AXIS ''
  foreach ($o in $offs) { $tx = X $o; Rect $tx ($p1 + 1) 1 5 $C_TICK '' }
  for ($i = 0; $i -lt 6; $i++) { $gxl = X $gridTimes[$i]; TxtC $gxl ($p1 + 10) $gridLabels[$i] 18 $C_T3 }
}

# ---- panel A: temperature ----
Panel $PA '① 温度（纵轴：°C）' '有效采样 10 / 12 · 缺测 2'
Axis $PA $loT $hiT @(19,20,21,22,23,24) $false
for ($i = 0; $i -lt 12; $i++) { if ($null -eq $temp[$i]) { $bx = X $offs[$i]; Rect ($bx - 6) ($PA + 40) 12 $PH '#64748B26' '' } }
$segsA = Segs $temp
foreach ($sg in $segsA) {
  for ($k = 0; $k -lt $sg.Count - 1; $k++) {
    $a = $sg[$k]; $b = $sg[$k + 1]
    $y1 = Y $temp[$a] $loT $hiT $p1A
    $y2 = Y $temp[$b] $loT $hiT $p1A
    $x1 = X $offs[$a]; $x2 = X $offs[$b]
    Seg $x1 $y1 $x2 $y2 3 $C_TEMP
  }
}
for ($i = 0; $i -lt 12; $i++) {
  $mx = X $offs[$i]
  if ($null -ne $temp[$i]) { $my = Y $temp[$i] $loT $hiT $p1A; Dot $mx $my 10 $C_PANEL; Dot $mx $my 7 $C_TEMP }
  else { TxtC $mx ($PA + 48) '—' 20 $C_T3 }
}

# ---- panel B: humidity ----
Panel $PB '② 相对湿度（纵轴：%）' '有效采样 11 / 12 · 缺测 1'
Axis $PB $loH $hiH @(34,36,38,40,42) $false
for ($i = 0; $i -lt 12; $i++) { if ($null -eq $hum[$i]) { $bx = X $offs[$i]; Rect ($bx - 6) ($PB + 40) 12 $PH '#64748B26' '' } }
$segsB = Segs $hum
foreach ($sg in $segsB) {
  for ($k = 0; $k -lt $sg.Count - 1; $k++) {
    $a = $sg[$k]; $b = $sg[$k + 1]
    $y1 = Y $hum[$a] $loH $hiH $p1B
    $y2 = Y $hum[$b] $loH $hiH $p1B
    $x1 = X $offs[$a]; $x2 = X $offs[$b]
    Seg $x1 $y1 $x2 $y2 3 $C_HUM
  }
}
for ($i = 0; $i -lt 12; $i++) {
  $mx = X $offs[$i]
  if ($null -ne $hum[$i]) { $my = Y $hum[$i] $loH $hiH $p1B; Dot $mx $my 10 $C_PANEL; Dot $mx $my 7 $C_HUM }
  else { TxtC $mx ($PB + 48) '—' 20 $C_T3 }
}

# ---- panel C: pressure ----
Panel $PC '③ 压差（纵轴：kPa）' '有效采样 12 / 12 · 缺测 0'
Axis $PC $loP $hiP @(-1.0,-0.5,0,0.5,1.0,1.5) $true
$bx0 = X 100; $bx1 = X 170
Rect $bx0 ($PC + 40) ($bx1 - $bx0) $PH '#F871711A' ''
$segsC = Segs $pres
foreach ($sg in $segsC) {
  for ($k = 0; $k -lt $sg.Count - 1; $k++) {
    $a = $sg[$k]; $b = $sg[$k + 1]
    $y1 = Y $pres[$a] $loP $hiP $p1C
    $y2 = Y $pres[$b] $loP $hiP $p1C
    $x1 = X $offs[$a]; $x2 = X $offs[$b]
    Seg $x1 $y1 $x2 $y2 3 $C_PRES
  }
}
for ($i = 0; $i -lt 12; $i++) {
  $mx = X $offs[$i]; $my = Y $pres[$i] $loP $hiP $p1C
  if ($pres[$i] -lt 0) { Dot $mx $my 15 $C_NEG; Dot $mx $my 11 $C_PANEL; Dot $mx $my 7 $C_PRES }
  else { Dot $mx $my 10 $C_PANEL; Dot $mx $my 7 $C_PRES }
}
Txt ($bx0 + 4) ($PC + 44) '负值采样 3 点：09:40 / 10:10 / 10:50' 20 $C_NEGT ''
Txt ($bx0 + 4) ($PC + 68) '仅这 3 点为负，不声称区间内每刻为负' 20 $C_T2 ''

# ================= bottom table =================
Txt 40 840 '全部 12 个采样时点明细（缺测记作 —；单位：°C / % / kPa）' 22 $C_T1 ''
$colW = 104.0; $colX0 = 152.0
$hdrY = 868.0; $rowH = 24.0
Rect 40 $hdrY 1360 $rowH '#1A2540' ' borderRadius="4"'
Txt 52 ($hdrY + 3) '时点' 18 $C_T3 ''
for ($i = 0; $i -lt 12; $i++) {
  $cx = $colX0 + $i * $colW
  $w = EW $times[$i] 18
  Txt ($cx + ($colW - $w) / 2) ($hdrY + 3) $times[$i] 18 $C_T3 ''
}
$rows = @(
  @{ n = '温度 °C'; arr = $temp; dec = 1 },
  @{ n = '相对湿度 %'; arr = $hum; dec = 0 },
  @{ n = '压差 kPa'; arr = $pres; dec = 1 }
)
for ($r = 0; $r -lt 3; $r++) {
  $ry = 892.0 + $r * 24.0
  if ($r % 2 -eq 0) { $bg = '#131C2E' } else { $bg = '#0F1728' }
  Rect 40 $ry 1360 $rowH $bg ''
  $row = $rows[$r]
  Txt 52 ($ry + 3) $row.n 18 $C_T2 ''
  for ($i = 0; $i -lt 12; $i++) {
    $cx = $colX0 + $i * $colW
    $v = $row.arr[$i]
    if ($null -eq $v) {
      Rect $cx $ry $colW $rowH '#2A3750' ''
      $w = EW '—' 18
      Txt ($cx + ($colW - $w) / 2) ($ry + 3) '—' 18 $C_T3 ''
    } else {
      if ($row.dec -eq 1) { $txt = ([double]$v).ToString('0.0', $Inv) } else { $txt = ([double]$v).ToString('0', $Inv) }
      $col = $C_T2
      if ($r -eq 2 -and $v -lt 0) { $col = $C_NEG }
      $w = EW $txt 18
      Txt ($cx + ($colW - $w) / 2) ($ry + 3) $txt 18 $col ''
    }
  }
}

L '    </Stack>'
L '  </Container>'
L '</Snapshot>'

$dslPath = Join-Path (Get-Location) $OutDsl
[System.IO.Directory]::CreateDirectory((Split-Path $dslPath -Parent)) | Out-Null
[System.IO.File]::WriteAllText($dslPath, $sb.ToString(), $enc)
"wrote $dslPath ($($sb.Length) chars)"

# ================= normalized-data.json =================
$missingT = @(); $missingH = @(); $missingP = @()
for ($i = 0; $i -lt 12; $i++) {
  if ($null -eq $temp[$i]) { $missingT += $times[$i] }
  if ($null -eq $hum[$i]) { $missingH += $times[$i] }
  if ($null -eq $pres[$i]) { $missingP += $times[$i] }
}
$samples = @()
for ($i = 0; $i -lt 12; $i++) {
  $tval = $null; $hval = $null; $pval = $null
  if ($null -ne $temp[$i]) { $tval = [double]$temp[$i] }
  if ($null -ne $hum[$i]) { $hval = [double]$hum[$i] }
  if ($null -ne $pres[$i]) { $pval = [double]$pres[$i] }
  $samples += [ordered]@{ time = $times[$i]; offset_min = $offs[$i]; temperature_c = $tval; humidity_pct = $hval; pressure_kpa = $pval }
}
function SegJson($arr, $names, $offsArr) {
  $out = @()
  foreach ($sg in (Segs $arr)) {
    $pts = @(); $of = @()
    foreach ($i in $sg) { $pts += $names[$i]; $of += $offsArr[$i] }
    $out += [ordered]@{ points = $pts; offsets_min = $of; count = $sg.Count }
  }
  $out
}
$negSamples = @()
for ($i = 0; $i -lt 12; $i++) {
  if ($pres[$i] -lt 0) { $negSamples += [ordered]@{ time = $times[$i]; offset_min = $offs[$i]; pressure_kpa = [double]$pres[$i] } }
}
$segT = @(SegJson $temp $times $offs)
$segH = @(SegJson $hum $times $offs)
$segP = @(SegJson $pres $times $offs)

$doc = [ordered]@{
  task_id = 'A05'; run_id = 'run-20261002-220723-mimo'
  source = 'tasks/A05-irregular-sensors/inputs/readings.csv'
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  sampling = 'irregular'
  window = [ordered]@{ start = '08:00'; end = '12:30'; start_offset_min = 0; end_offset_min = 270; total_minutes = 270; x_axis_mapping = 'x = 124 + offset_min/270 * 1248 (linear, true time proportion, shared by all 3 charts)' }
  units = [ordered]@{ temperature_c = '°C'; humidity_pct = '%'; pressure_kpa = 'kPa' }
  missing_encoding = [ordered]@{
    csv = 'empty cell'; normalized = 'null'; table = '—'
    chart = '— marker at sample x + faint vertical band + line broken at that sample'
    note = '缺测不是 0；未使用直线或虚线补值，也未做任何插值'
  }
  samples = $samples
  valid_counts = [ordered]@{
    temperature_c = [ordered]@{ valid = 10; missing = 2; total = 12 }
    humidity_pct  = [ordered]@{ valid = 11; missing = 1; total = 12 }
    pressure_kpa  = [ordered]@{ valid = 12; missing = 0; total = 12 }
  }
  missing = [ordered]@{ temperature_c = $missingT; humidity_pct = $missingH; pressure_kpa = $missingP }
  ranges = [ordered]@{
    temperature_c = [ordered]@{ min = 19.2; min_at = '08:00'; max = 23.1; max_at = '10:50'; observed = @(19.2, 23.1); axis_domain = @(19, 24) }
    humidity_pct  = [ordered]@{ min = 34.0; min_at = '10:50'; max = 41.0; max_at = '08:00'; observed = @(34, 41); axis_domain = @(33, 42) }
    pressure_kpa  = [ordered]@{ min = -0.8; min_at = '10:10'; max = 1.3; max_at = '09:15'; observed = @(-0.8, 1.3); axis_domain = @(-1.0, 1.5) }
  }
  connected_segments = [ordered]@{ temperature_c = $segT; humidity_pct = $segH; pressure_kpa = $segP }
  connected_segments_note = '线段只连接相邻且均为有效读数的采样点；缺测点两侧断开，不使用直线或虚线补值。'
  pressure_negative = [ordered]@{
    samples = $negSamples
    sampled_span = [ordered]@{ from = '09:40'; to = '10:50'; from_offset_min = 100; to_offset_min = 170; sample_count = 3 }
    claim = '09:40、10:10、10:50 这 3 个实际采样点的压差为负'
    not_claimed = '不声称 09:40–10:50 之间每一刻均为负；相邻采样 09:15 = +1.3 kPa、11:00 = +0.1 kPa 为正，穿越零线的准确时刻未被采样。'
  }
}
$json = ConvertTo-Json -InputObject $doc -Depth 10
$json = [regex]::Replace($json, '\\u([0-9a-fA-F]{4})', { param($m) [char][Convert]::ToInt32($m.Groups[1].Value, 16) })
$jsonPath = Join-Path (Get-Location) $OutJson
[System.IO.Directory]::CreateDirectory((Split-Path $jsonPath -Parent)) | Out-Null
[System.IO.File]::WriteAllText($jsonPath, $json + "`r`n", $enc)
"wrote $jsonPath"
