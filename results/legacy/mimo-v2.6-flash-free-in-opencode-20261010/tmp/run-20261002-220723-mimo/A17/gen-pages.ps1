$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$utf8 = New-Object System.Text.UTF8Encoding($false)
$OUT = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A17'
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A17'

# measured metrics
$MONO_CJK = 22; $MONO_LAT = 11      # Noto Sans Mono CJK SC @ fs22
$LINE_CODE = 32                      # mono fs22 line box
$LINE_24 = 35; $LINE_26 = 38; $LINE_40 = 58   # Noto Sans CJK SC line boxes
$PROSE_CJK = 24; $PROSE_LAT = 14     # Noto Sans CJK SC @ fs24 advance

function IsWide([char]$c) {
  $x = [int]$c
  if ($x -ge 0x1100 -and $x -le 0x115F) { return $true }
  if ($x -ge 0x2E80 -and $x -le 0xA4CF) { return $true }
  if ($x -ge 0xF900 -and $x -le 0xFAFF) { return $true }
  if ($x -ge 0xFE30 -and $x -le 0xFE6F) { return $true }
  if ($x -ge 0xFF00 -and $x -le 0xFF60) { return $true }
  if ($x -ge 0xFFE0 -and $x -le 0xFFE6) { return $true }
  if ($x -ge 0x3000 -and $x -le 0x303F) { return $true }
  if ($x -ge 0x2010 -and $x -le 0x201F) { return $true }
  if ($x -eq 0x00B7) { return $true }
  return $false
}
function CodeWidth([string]$s) {
  $w = 0
  foreach ($ch in $s.ToCharArray()) { if (IsWide $ch) { $w += $MONO_CJK } else { $w += $MONO_LAT } }
  return $w
}
function ProseWidth([string]$s) {
  $w = 0
  foreach ($ch in $s.ToCharArray()) { if (IsWide $ch) { $w += $PROSE_CJK } else { $w += $PROSE_LAT } }
  return $w
}
function Esc([string]$s) {
  if ($s -match '[<>&]') { return '<![CDATA[' + $s + ']]>' }
  return $s
}
# Emit exact characters (including leading indentation) as the content of one <Raw> span.
# A line that itself contains "]]>" cannot live inside a single CDATA section, so the
# terminator is split across two sections: section 1 ends with "]]" and section 2 begins
# with ">", which together reconstruct "]]>" in the resulting text.
function EmitVerbatim([string]$s) {
  $idx = $s.IndexOf(']]>')
  if ($idx -lt 0) { return '<Raw><![CDATA[' + $s + ']]></Raw>' }
  $A = $s.Substring(0, $idx)
  $B = $s.Substring($idx + 3)
  if ($B -like '*]]>*') { throw ('line has more than one ]]> : ' + $s) }
  return '<Raw><![CDATA[' + $A + ']]' + ']]>' + '<![CDATA[' + '>' + $B + ']]></Raw>'
}

$pages = @(
  [pscustomobject]@{
    id='01'; ex='example-01'; omit=11; why='两条响应提示文本'
    badge='P1 · 调用契约'; title='一次快照调用的完整形状'
    desc='先记住请求与响应长什么样，再学标签与属性'
    rightHeading='这一步要弄清什么'
    bullets=@(
      '请求体是 UTF-8 纯文本，不是 JSON',
      'Content-Type: text/plain; charset=utf-8',
      '成功返回 PNG 字节，失败返回 JSON 错误体',
      'X-Request-Id 两边都要留，方便对账',
      '429 / 503 先读 Retry-After 再重试')
    caption='图 1 · example-01.snapshot 的真实渲染（400×240，未做后期处理）'
    codeHeading='可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）'
    pointsHeading='这一步的踩坑'
    points=@(
      '错误体是 JSON，别当纯文本读',
      'code / message / requestId 三个字段都要取',
      '400 是解析失败，422 是参数或状态不合法',
      '省略标注是注释，删掉后示例照样能解析')
    footerL='A17 文档手册 · 第 1 / 4 页 · 调用契约'
  },
  [pscustomobject]@{
    id='02'; ex='example-02'; omit=12; why='右下定位的第二块'
    badge='P2 · 尺寸与定位'; title='根尺寸与有界布局'
    desc='从根尺寸出发，约束只能逐层收窄不能凭空放大'
    rightHeading='这一步要弄清什么'
    bullets=@(
      '根尺寸由根布局决定，受服务端限制',
      '约束从外向内收紧，子节点不能凭空放大',
      'Expanded 只能是 Row / Column 的直接子级',
      '有界主轴才能用 Expanded 拆分剩余空间',
      'Stack 不提供尺寸，靠 Positioned 摆位置')
    caption='图 2 · example-02.snapshot 的真实渲染（400×240，未做后期处理）'
    codeHeading='可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）'
    pointsHeading='这一步的踩坑'
    points=@(
      'Expanded 放错层级会直接解析失败',
      '无界主轴上 Expanded 没有可分配空间',
      '同一轴上 left / right / width 最多只能给两个',
      '根尺寸是布局结果，不是 HTML 的视口')
    footerL='A17 文档手册 · 第 2 / 4 页 · 尺寸与定位'
  },
  [pscustomobject]@{
    id='03'; ex='example-03'; omit=14; why='两条图例行'
    badge='P3 · 文本与颜色'; title='原样保留的文本与尾随透明度'
    desc='谁修剪空白、谁保留空白，以及颜色末尾两位'
    rightHeading='这一步要弄清什么'
    bullets=@(
      'Text 会修剪自己首尾的空白',
      'Raw 只能写在 Text 里，用来保住空格',
      'CDATA 原样保留 < > &，不走实体解码',
      '颜色写 #RRGGBBAA，末两位是透明度',
      'Kotlin 侧 0xAARRGGBB，顺序正好相反')
    caption='图 3 · example-03.snapshot 的真实渲染（400×240，未做后期处理）'
    codeHeading='可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）'
    pointsHeading='这一步的踩坑'
    points=@(
      '&amp; 不会被解码，会原样显示',
      'Raw 写在 Text 之外会直接 400',
      '十六进制别混用 AARRGGBB 与 RRGGBBAA',
      '尾随 alpha 越小越透明，FF 是不透明')
    footerL='A17 文档手册 · 第 3 / 4 页 · 文本与颜色'
  },
  [pscustomobject]@{
    id='04'; ex='example-04'; omit=5; why='两条色带'
    badge='P4 · 滤镜与自检'; title='背景滤镜、子树滤镜与自检'
    desc='先分清滤的是身后还是自己，再逐层做验证'
    rightHeading='这一步要弄清什么'
    bullets=@(
      'BackdropFilter 滤它身后已画好的内容',
      'ImageFiltered 滤子树自己的绘制结果',
      '毛玻璃通常需要 ClipRect / ClipRRect 限区',
      '背后没有内容时，背景滤镜等于没生效',
      '先量像素再看图，别只凭肉眼判断')
    caption='图 4 · example-04.snapshot 的真实渲染（400×240，未做后期处理）'
    codeHeading='可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）'
    pointsHeading='这一步的踩坑'
    points=@(
      'ImageFiltered 在同一 Stack 里会让背景滤镜失效',
      '布局、像素、黄金图、产物四层都要验',
      '产物只是结果，不是断言',
      '黄金图不稳时先查字体与抗锯齿')
    footerL='A17 文档手册 · 第 4 / 4 页 · 滤镜与自检'
  }
)

$report = New-Object System.Collections.Generic.List[string]
$report.Add('# handbook page generation report')

foreach ($p in $pages) {
  $exFile = Join-Path $OUT ($p.ex + '.snapshot')
  $all = [IO.File]::ReadAllText($exFile, $utf8) -split "`r?`n"
  if ($all.Count -gt 0 -and $all[$all.Count-1] -eq '') { $all = $all[0..($all.Count-2)] }
  if ($all.Count -ne 18) { throw "$($p.ex) is not 18 lines" }

  $k = $p.omit
  $marker = '<!--省略 ' + $p.ex + '.snapshot 第 ' + $k + '、' + ($k+1) + ' 行（' + $p.why + '）；完整文件共 18 行 -->'
  $printed = @()
  $printed += $all[0..($k-2)]
  $printed += $marker
  $printed += $all[($k+1)..17]
  if ($printed.Count -ne 17) { throw "$($p.ex) printed count = $($printed.Count)" }

  $report.Add('')
  $report.Add(('## ' + $p.ex + '  printed lines = ' + $printed.Count))
  $pi = 0
  foreach ($ln in $printed) {
    $pi++
    $w = CodeWidth $ln
    $flag = ''
    if ($w -gt 1040) { $flag = '  <== TOO WIDE'; throw "$($p.ex) printed line $pi too wide ($w)" }
    $report.Add(('  {0,2} ({1,4}px) {2}{3}' -f $pi, $w, $ln, $flag))
  }
  foreach ($b in $p.bullets) { $w = ProseWidth ('• ' + $b); if ($w -gt 632) { throw "$($p.ex) bullet too wide ($w): $b" } }
  foreach ($pt in $p.points) { $w = ProseWidth ('• ' + $pt); if ($w -gt 1056) { throw "$($p.ex) point too wide ($w): $pt" } }
  $report.Add(('  bullets max width ok, caption=' + (ProseWidth $p.caption) + 'px, desc=' + (ProseWidth $p.desc) + 'px'))

  # ---- build page DSL ----
  $L = New-Object System.Collections.Generic.List[string]
  $L.Add('<Snapshot type="png">')
  $L.Add('  <Container width="1200" height="1600" color="#F1F5F9">')
  $L.Add('    <Stack>')

  # header
  $L.Add('      <Positioned left="48" top="48"><Container color="#1D4ED8" borderRadius="8" padding="(6,14)"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#FFFFFF">' + (Esc $p.badge) + '</Text></Container></Positioned>')
  $L.Add('      <Positioned left="48" top="103"><Text fontSize="40" fontFamily="Noto Sans CJK SC" color="#0F172A">' + (Esc $p.title) + '</Text></Positioned>')
  $L.Add('      <Positioned left="48" top="169"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#334155">' + (Esc $p.desc) + '</Text></Positioned>')

  # card A
  $L.Add('      <Positioned left="48" top="218"><Container width="1104" height="346" color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/></Positioned>')
  # illustration = example lines 2..17 at (72,242)
  # ClipRect gives the illustration its own layer, so a BackdropFilter inside it clamps
  # at the 400x240 frame exactly like the standalone render does (no white-card bleed).
  $L.Add('      <Positioned left="72" top="242"><ClipRect>')
  foreach ($i in 1..16) { $L.Add('  ' + $all[$i]) }
  $L.Add('      </ClipRect></Positioned>')
  # right column
  $L.Add('      <Positioned left="496" top="242"><Text fontSize="26" fontFamily="Noto Sans CJK SC" color="#0F172A">' + (Esc $p.rightHeading) + '</Text></Positioned>')
  $bt = 300
  foreach ($b in $p.bullets) {
    $L.Add('      <Positioned left="496" top="' + $bt + '"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#334155">' + (Esc ('• ' + $b)) + '</Text></Positioned>')
    $bt += 40
  }
  # caption
  $L.Add('      <Positioned left="72" top="505"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#64748B">' + (Esc $p.caption) + '</Text></Positioned>')

  # card B
  $L.Add('      <Positioned left="48" top="578"><Container width="1104" height="656" color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/></Positioned>')
  $L.Add('      <Positioned left="72" top="602"><Text fontSize="26" fontFamily="Noto Sans CJK SC" color="#0F172A">' + (Esc $p.codeHeading) + '</Text></Positioned>')
  $L.Add('      <Positioned left="72" top="646"><Container width="1056" height="564" color="#0F172A" borderRadius="8"/></Positioned>')
  $ci = 0
  foreach ($ln in $printed) {
    $col = '#E2E8F0'
    if ($ln -like '<!--*') { $col = '#F59E0B' }
    $top = 656 + ($ci * $LINE_CODE)
    # Raw inside Text preserves the leading indentation of the printed line verbatim
    $L.Add('      <Positioned left="88" top="' + $top + '"><Text fontSize="22" fontFamily="Noto Sans Mono CJK SC" color="' + $col + '">' + (EmitVerbatim $ln) + '</Text></Positioned>')
    $ci++
  }

  # card C
  $L.Add('      <Positioned left="48" top="1248"><Container width="1104" height="254" color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/></Positioned>')
  $L.Add('      <Positioned left="72" top="1272"><Text fontSize="26" fontFamily="Noto Sans CJK SC" color="#0F172A">' + (Esc $p.pointsHeading) + '</Text></Positioned>')
  $ptt = 1326
  foreach ($pt in $p.points) {
    $L.Add('      <Positioned left="72" top="' + $ptt + '"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#334155">' + (Esc ('• ' + $pt)) + '</Text></Positioned>')
    $ptt += 39
  }

  # footer
  $L.Add('      <Positioned left="48" top="1516"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#64748B">' + (Esc $p.footerL) + '</Text></Positioned>')
  $L.Add('      <Positioned left="528" top="1516"><Container width="624" height="' + $LINE_24 + '" alignment="CENTER_RIGHT"><Text fontSize="24" fontFamily="Noto Sans CJK SC" color="#64748B">来源：open-snapshot AI Guide、Snapshot DSL 文档</Text></Container></Positioned>')

  $L.Add('    </Stack>')
  $L.Add('  </Container>')
  $L.Add('</Snapshot>')

  [IO.File]::WriteAllLines((Join-Path $TMP ('handbook-' + $p.id + '-v03.snapshot')), $L.ToArray(), $utf8)
  $report.Add(('  wrote handbook-' + $p.id + '-v03.snapshot  lines=' + $L.Count))
}

[IO.File]::WriteAllLines((Join-Path $TMP 'page-gen-report.md'), $report.ToArray(), $utf8)
Write-Output ('wrote page-gen-report.md rows=' + $report.Count)
