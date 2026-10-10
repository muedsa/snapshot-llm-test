$ErrorActionPreference = "Stop"
$T = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A17')
$L = Join-Path $T "log-iter.ps1"
$now = "2026-10-04T16:42:00+08:00"

$reqs = Get-Content (Join-Path $T "requests.jsonl") | ForEach-Object { $_ | ConvertFrom-Json }
function Dur($id) {
  $r = $reqs | Where-Object { $_.id -eq $id } | Select-Object -Last 1
  if ($r) { return $r.duration_ms } else { return $null }
}
function One($ver,$par,$type,$purpose,$dsl,$image,$req,$view,$method,$obs,$chg,$cat,$status) {
  $st = 200
  if ($status) { $st = $status }
  $d = Dur $req
  & $L -Version $ver -Parent $par -Type $type -Purpose $purpose -Dsl $dsl -Image $image `
       -RequestId $req -HttpStatus $st -DurationMs $d -ViewedAt $view -ViewMethod $method `
       -Observed $obs -Change $chg -Category $cat | Out-Null
}

# ---- rule-check probes behind two handbook claims ----
One "probe-12" "probe-11" "alternative" "check the handbook claim that Raw outside Text is rejected" `
  "tmp/run-20261002-220723-mimo/A17/probe-12.snapshot" $null `
  "A17-probe12" $null $null `
  "HTTP 400 PARSE_ERROR: Element [Raw] ... cant not buildWidget, it can only be used in the Text at position 81" `
  "none (measurement)" "dsl" 400

One "probe-13" "probe-12" "alternative" "check the handbook claim that Expanded in the wrong place fails to parse" `
  "tmp/run-20261002-220723-mimo/A17/probe-13.snapshot" $null `
  "A17-probe13" $null $null `
  "HTTP 400 PARSE_ERROR: Tag [Expanded] must be a direct child of Flex, Row or Column at position 98" `
  "none (measurement)" "dsl" 400

# ---- printed snippets actually parse ----
foreach ($n in @("01","02","03","04")) {
  $mark = @{ "01"="11 12"; "02"="12 13"; "03"="14 15"; "04"="5 6" }[$n]
  One ("printed-" + $n) $n "visual" "prove the 17 lines the handbook prints really parse as standalone DSL" `
    ("tmp/run-20261002-220723-mimo/A17/printed-" + $n + ".snapshot") `
    ("tmp/run-20261002-220723-mimo/A17/printed-" + $n + ".png") `
    ("A17-printed" + $n) $now "pixel-sampling" `
    ("HTTP 200, 400x240 png with real content (distinct colours 5-530); the XML-comment marker is skipped by the parser as the guide documents; this round omits example lines " + $mark) `
    "none (verification)" "verification"
}

# ---- handbook pages v03: copy accuracy pass ----
$obs = @{
 "01"="page reads correctly; heading now states 16 printed lines + marker and 18 lines in the file; illustration 0 differing pixels against example-01.png"
 "02"="wrong claim replaced: canvas size comes from the root layout and is capped by the server, not from Snapshot width/height (ai-guide line 28); Positioned wording now matches the source (at most two of left/right/width); heading corrected; illustration 0 differing pixels"
 "03"="heading corrected; the Raw-outside-Text 400 claim is now backed by probe-12; illustration 0 differing pixels against example-03.png"
 "04"="heading corrected; ClipRect wording softened to the source wording (usually needs ClipRect or ClipRRect); illustration 0 differing pixels against example-04.png"
}
$chg = @{
 "01"="codeHeading -> 可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）"
 "02"="codeHeading -> 可复制运行...; bullet1 -> 根尺寸由根布局决定，受服务端限制; point3 -> 最多只能给两个"
 "03"="codeHeading -> 可复制运行..."
 "04"="codeHeading -> 可复制运行...; bullet3 -> 毛玻璃通常需要 ClipRect / ClipRRect 限区"
}
$dur = @{ "01"="A17-pg01d"; "02"="A17-pg02d"; "03"="A17-pg03d"; "04"="A17-pg04d" }
foreach ($n in @("01","02","03","04")) {
  $id = $dur[$n]
  $d = Dur $id
  & $L -Version ("handbook-" + $n + "-v03") -Parent ("handbook-" + $n + "-v02") `
       -Type "requirement-change" `
       -Purpose "documentation accuracy pass against the retained source pages before delivery" `
       -Dsl ("tmp/run-20261002-220723-mimo/A17/handbook-" + $n + "-v03.snapshot") `
       -Image ("tmp/run-20261002-220723-mimo/A17/handbook-" + $n + "-v03.png") `
       -RequestId $id -HttpStatus 200 -DurationMs $d `
       -ViewedAt $now -ViewMethod "read-tool-image" `
       -Observed $obs[$n] -Change $chg[$n] -Category "content" | Out-Null
}

Write-Output ("iterations rows = " + (Get-Content (Join-Path $T "iterations.jsonl")).Count)
