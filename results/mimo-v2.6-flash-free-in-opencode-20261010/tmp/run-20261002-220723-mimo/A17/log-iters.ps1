$ErrorActionPreference = "Stop"
$T = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A17')
$L = Join-Path $T "log-iter.ps1"
$now = "2026-10-04T15:12:00+08:00"

function One($ver,$par,$type,$purpose,$dsl,$image,$req,$dur,$view,$method,$obs,$chg,$cat) {
  & $L -Version $ver -Parent $par -Type $type -Purpose $purpose -Dsl $dsl -Image $image `
       -RequestId $req -HttpStatus 200 -DurationMs $dur -ViewedAt $view -ViewMethod $method `
       -Observed $obs -Change $chg -Category $cat | Out-Null
}

# --- v01 baselines (first real renders of the four examples) ---
One "example-01-v01" $null "baseline" "render first draft of example-01 (call contract card)" `
  "outputs/run-20261002-220723-mimo/A17/example-01.snapshot" "tmp/run-20261002-220723-mimo/A17/example-01-v01.png" `
  "A17-ex01" 2281.1 $now "read-tool-image" `
  "renders fully; but Column default crossAxisAlignment=CENTER centres the 5 body lines while the blue header title is left aligned||ink x37..363 proves centring" `
  "none (baseline)" "layout"

One "example-02-v01" $null "baseline" "render first draft of example-02 (bounded Row + Stack positioning)" `
  "outputs/run-20261002-220723-mimo/A17/example-02.snapshot" "tmp/run-20261002-220723-mimo/A17/example-02-v01.png" `
  "A17-ex02" 1589.1 $now "read-tool-image" `
  "Row split 264+88 correct; Positioned left/top and right/bottom correct||label 'right + bottom' uses default black on the #1E293B panel, unreadable" `
  "none (baseline)" "contrast"

One "example-03-v01" $null "baseline" "render first draft of example-03 (tail alpha + Raw + CDATA)" `
  "outputs/run-20261002-220723-mimo/A17/example-03.snapshot" "tmp/run-20261002-220723-mimo/A17/example-03-v01.png" `
  "A17-ex03" 2048.1 $now "read-tool-image" `
  "three swatch alphas FF/80/26 clearly differ; CDATA and Raw spans correct||the two fs16 legend lines in #64748B are too dim on #0F172A" `
  "none (baseline)" "contrast"

One "example-04-v01" $null "baseline" "render first draft of example-04 (backdrop + subtree filters)" `
  "outputs/run-20261002-220723-mimo/A17/example-04.snapshot" "tmp/run-20261002-220723-mimo/A17/example-04-v01.png" `
  "A17-ex04" 1759.3 $now "read-tool-image" `
  "BLUR label renders default black on dark navy, nearly invisible||left frost region shows only a 26% white wash, band edges stay hard (delta=310), BackdropFilter blur absent" `
  "none (baseline)" "filters"

# --- v02 visual iterations ---
One "example-01-v02" "example-01-v01" "visual" "fix horizontal alignment mismatch between header and body" `
  "tmp/run-20261002-220723-mimo/A17/example-01-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/example-01-v02.png" `
  "A17-ex01b" 2139.9 $now "read-tool-image" `
  "body now left aligned with the header; widest line ends x363 inside the 24px padding" `
  "added crossAxisAlignment=START to the inner Column (line 8)" "layout"

One "example-02-v02" "example-02-v01" "visual" "make the Positioned label readable without lengthening the printed line" `
  "tmp/run-20261002-220723-mimo/A17/example-02-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/example-02-v02.png" `
  "A17-ex02b" 2059.2 $now "read-tool-image" `
  "label now black on light panel, fully legible; line 12 stays 86 chars (<=94 budget)" `
  "panel color #1E293B -> #E2E8F0 instead of adding a color attribute (a color attr would push line 12 to 101 chars > 94)" "contrast"

One "example-03-v02" "example-03-v01" "visual" "raise contrast of the two secondary legend lines" `
  "tmp/run-20261002-220723-mimo/A17/example-03-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/example-03-v02.png" `
  "A17-ex03b" 1865.4 $now "read-tool-image" `
  "both fs16 legend lines readable; overall line rhythm unchanged" `
  "color #64748B -> #94A3B8 on lines 14 and 15" "contrast"

One "example-04-v02" "example-04-v01" "visual" "give the BLUR label a light colour and give the frost an explicit box" `
  "tmp/run-20261002-220723-mimo/A17/example-04-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/example-04-v02.png" `
  "A17-ex04b" 2380.5 $now "read-tool-image" `
  "BLUR label now white and legible||backdrop blur STILL missing: x75 y48 delta=310 hard edge, left region equals band+26% white exactly" `
  "added color=#FFF to the Text and wrapped the frost in Positioned left/top/width/height" "filters"

# --- diagnostic probes ---
One "probe-03" "example-04-v02" "alternative" "isolate the missing BackdropFilter blur with 4 structural variants in one render" `
  "tmp/run-20261002-220723-mimo/A17/probe-03.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-03.png" `
  "A17-probe03" 1969.2 $now "pixel-column-sampling" `
  "Column bands / Positioned bands / added opaque background child / frost at left=200 all blur identically (soft ramp 13-17 per row)||so band style, paint order and frost offset are not the cause" `
  "none (diagnostic)" "filters"

One "probe-04" "probe-03" "alternative" "test ex04 structure with the ImageFiltered subtree removed" `
  "tmp/run-20261002-220723-mimo/A17/probe-04.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-04.png" `
  "A17-probe04" 1593.3 $now "pixel-column-sampling" `
  "blurs (soft ramp 13-17 per row at y44-52)||removing ImageFiltered from the Stack restores the backdrop blur" `
  "none (diagnostic)" "filters"

One "probe-05" "probe-04" "alternative" "test ex04 structure with Snapshot background=#FFFFFF but ImageFiltered kept" `
  "tmp/run-20261002-220723-mimo/A17/probe-05.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-05.png" `
  "A17-probe05" 2027.8 $now "pixel-column-sampling" `
  "no blur (hard edge delta=310)||the background attribute is not the cause" `
  "none (diagnostic)" "filters"

One "probe-06" "probe-05" "alternative" "test ex04 structure with Stack and Column tags on separate lines" `
  "tmp/run-20261002-220723-mimo/A17/probe-06.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-06.png" `
  "A17-probe06" 1712.1 $now "pixel-column-sampling" `
  "no blur (hard edge delta=310)||the merged Stack/Column opening tag is not the cause" `
  "none (diagnostic)" "filters"

One "example-04-v03" "example-04-v02" "visual" "move the ImageFiltered subtree out of the Stack that carries the BackdropFilter" `
  "tmp/run-20261002-220723-mimo/A17/example-04-v03.snapshot" "tmp/run-20261002-220723-mimo/A17/example-04-v03.png" `
  "A17-ex04c" 1606.9 $now "read-tool-image" `
  "backdrop blur restored (soft ramp 9-17 per row at y44-52 and y186-191); frost panel ends exactly at the band block y192; BLUR white and blurred; visually confirmed by direct image view" `
  "outer Column now holds <Stack> (bands + frost) and <ImageFiltered> as siblings; frost height 192 = 4x48 band block; merged </BackdropFilter></ClipRect></Positioned> and </Column></Container> to stay at 18 lines" "filters"

Write-Output "done"
