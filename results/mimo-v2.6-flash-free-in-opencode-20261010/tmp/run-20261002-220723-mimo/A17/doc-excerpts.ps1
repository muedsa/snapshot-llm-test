# A17 - extract the exact reference sections this handbook prints.
# Sources are retained bytes fetched during this same run_id: the parser tag
# reference from A15 and the eight pages fetched for A17. No new HTTP request.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$utf8 = New-Object System.Text.UTF8Encoding($false)

$A15 = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15\doc-parser-tags.html'
$A17 = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A17'

function Strip-Html([string]$h) {
  $h = [regex]::Replace($h, '(?is)<script.*?</script>', ' ')
  $h = [regex]::Replace($h, '(?is)<style.*?</style>', ' ')
  $h = [regex]::Replace($h, '(?i)</(p|li|tr|h[1-6]|div|pre|code|table|section)>', "`n")
  $h = [regex]::Replace($h, '(?i)<br\s*/?>', "`n")
  $h = [regex]::Replace($h, '(?s)<[^>]+>', '')
  $h = [System.Net.WebUtility]::HtmlDecode($h)
  $h = [regex]::Replace($h, "[ \t]+", ' ')
  $h = [regex]::Replace($h, "(\r?\n\s*){2,}", "`n")
  return $h.Trim()
}

function Get-Sections([string]$raw) {
  # returns ordered list of @{lvl;text;start;contentStart}
  $heads = @()
  foreach ($m in [regex]::Matches($raw, '(?is)<h([1-6])[^>]*>(.*?)</h\1>')) {
    $txt = Strip-Html $m.Groups[2].Value
    $txt = $txt -replace "\s+", ' '
    $heads += [pscustomobject]@{ lvl = [int]$m.Groups[1].Value; text = $txt; start = $m.Index; contentStart = ($m.Index + $m.Length) }
  }
  return ,$heads
}

function Get-Section([object[]]$heads, [string]$raw, [string]$needle) {
  for ($i = 0; $i -lt $heads.Count; $i++) {
    if ($heads[$i].text -like "*$needle*") {
      $end = $raw.Length
      for ($j = $i + 1; $j -lt $heads.Count; $j++) {
        if ($heads[$j].lvl -le $heads[$i].lvl) { $end = $heads[$j].start; break }
      }
      $slice = $raw.Substring($heads[$i].contentStart, ($end - $heads[$i].contentStart))
      $txt = Strip-Html $slice
      $txt = $txt -replace "`r", ''
      $lines = @()
      foreach ($ln in $txt.Split("`n")) { $t = $ln.Trim(); if ($t) { $lines += $t } }
      return [pscustomobject]@{ heading = $heads[$i].text; lines = $lines }
    }
  }
  return $null
}

$out = New-Object System.Collections.Generic.List[string]
$out.Add('# A17 - reference sections actually consulted')
$out.Add('')
$out.Add('All sources are retained bytes from this same `run_id`. The parser tag reference is')
$out.Add("reused from A15 (same URL, same service, same run) and the eight guide pages below")
$out.Add('were fetched for this task by `tmp/run-20261002-220723-mimo/A17/fetch-docs.ps1` and are')
$out.Add('logged in `requests.jsonl` as `A17-doc-01..08`. Nothing here is a new HTTP request.')
$out.Add('')
$out.Add('| section | source | retained bytes |')
$out.Add('| --- | --- | --- |')
$out.Add('| tag / attribute tables | https://snapshot.muedsa.com/reference/parser-tags/ | tmp/run-20261002-220723-mimo/A15/doc-parser-tags.html |')
foreach ($f in @('doc-rendering.html', 'doc-parser-errors.html', 'doc-layout.html', 'doc-parser.html', 'doc-media-text.html', 'doc-painting.html', 'doc-testing.html', 'doc-ai-guide.md')) {
  $p = Join-Path $A17 $f
  if (Test-Path $p) { $out.Add("| $f | see requests.jsonl | $f ($((Get-Item $p).Length) bytes) |") }
}
$out.Add('')

$plans = @(
  [pscustomobject]@{ file = $A15;                  label = 'reference/parser-tags'; needles = @('标签总表', 'Row 与 Column', 'Expanded 与 Flexible', 'Stack', 'Positioned', '对齐', '颜色', 'Raw') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-layout.html');       label = 'guides/layout';       needles = @('父节点给约束，子节点报尺寸', 'Container 的组合顺序', 'Flex 布局', 'Stack 与 Positioned', '布局自省') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-parser.html');       label = 'guides/parser';       needles = @('处理流程', '常用标签', '文本中的特殊字符', '错误处理') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-parser-errors.html');label = 'reference/parser-errors'; needles = @('文本与空白', '解析阶段错误', '构建阶段错误', '渲染阶段错误', '注释') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-painting.html');     label = 'guides/painting';     needles = @('透明度与颜色滤镜', '边框与圆角', '渐变', 'Transform') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-testing.html');      label = 'guides/testing';      needles = @('Golden 三态', '文本测试', 'Artifact', '常见误区') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-media-text.html');   label = 'guides/media-text';   needles = @('普通文本', 'TextStyle', '富文本', '行内 Widget 与 Emoji', 'TextPainter') },
  [pscustomobject]@{ file = (Join-Path $A17 'doc-rendering.html');    label = 'guides/rendering';    needles = @('渲染入口总览', '共同参数', '尺寸是如何决定的', '接入 HTTP 服务') }
)

foreach ($p in $plans) {
  if (!(Test-Path $p.file)) { $out.Add("## $($p.label) - FILE MISSING"); $out.Add(''); continue }
  $raw = [IO.File]::ReadAllText($p.file, $utf8)
  $heads = Get-Sections $raw
  $out.Add("## $($p.label)  ($((Split-Path $p.file -Leaf)))")
  $out.Add('')
  $out.Add('- headings found: ' + $heads.Count)
  $found = @()
  foreach ($n in $p.needles) {
    $s = Get-Section $heads $raw $n
    if ($null -eq $s) {
      $out.Add("- ``$n`` - no heading matched (not claimed)")
      continue
    }
    $found += $n
    $out.Add('')
    $out.Add("### $($s.heading)")
    $keep = 0
    foreach ($ln in $s.lines) {
      $out.Add("> $ln")
      $keep++
      if ($keep -ge 200) { $out.Add('> … (section truncated for this excerpt; full bytes retained on disk)'); break }
    }
  }
  $out.Add('')
  $out.Add('- matched: ' + $(if ($found.Count) { ($found -join ', ') } else { 'none' }))
  $out.Add('')
}

[IO.File]::WriteAllLines((Join-Path $A17 'doc-excerpts.md'), $out.ToArray(), $utf8)
Write-Output ("wrote doc-excerpts.md  lines=" + $out.Count)
