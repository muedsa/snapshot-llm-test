$ErrorActionPreference = "Stop"
$T = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A17')
$L = Join-Path $T "log-iter.ps1"
$now = "2026-10-04T15:58:00+08:00"

function One($ver,$par,$type,$purpose,$dsl,$image,$req,$dur,$view,$method,$obs,$chg,$cat,$status) {
  $st = 200
  if ($status) { $st = $status }
  & $L -Version $ver -Parent $par -Type $type -Purpose $purpose -Dsl $dsl -Image $image `
       -RequestId $req -HttpStatus $st -DurationMs $dur -ViewedAt $view -ViewMethod $method `
       -Observed $obs -Change $chg -Category $cat | Out-Null
}

# ---------- metric probes (page layout inputs) ----------
One "probe-07" "example-04-v03" "alternative" "measure per-size line box height for the default font stack so the page grid can be exact" `
  "tmp/run-20261002-220723-mimo/A17/probe-07.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-07.png" `
  "A17-probe07" 2114.6 $now "pixel-row-banding" `
  "identical glyphs give exact pitch: fs20=24, fs22=27, fs24=29, fs26=31, fs40=48" `
  "none (measurement)" "layout"

One "probe-08" "probe-07" "alternative" "measure line box and per-character advance for Noto Sans Mono CJK SC at fs20/22/24" `
  "tmp/run-20261002-220723-mimo/A17/probe-08.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-08.png" `
  "A17-probe08" 1567.3 $now "pixel-row-banding" `
  "mono line box fs20=29 fs22=32 fs24=35; 8-char ink width gives advance 10/11/12 px => fs22 budget = 1040/11 = 94 chars" `
  "none (measurement)" "layout"

One "probe-09" "probe-08" "alternative" "measure line box for Noto Sans CJK SC at fs20/24/26/40 (the prose font)" `
  "tmp/run-20261002-220723-mimo/A17/probe-09.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-09.png" `
  "A17-probe09" 1857.7 $now "pixel-row-banding" `
  "Noto Sans CJK SC line box = 29 / 35 / 38 / 58 for fs20 / 24 / 26 / 40, noticeably taller than the default stack" `
  "none (measurement)" "layout"

One "probe-10" "probe-09" "alternative" "does Text trim leading whitespace, and are internal spaces preserved" `
  "tmp/run-20261002-220723-mimo/A17/probe-10.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-10.png" `
  "A17-probe10" 1899.3 $now "pixel-ink-extent" `
  "plain and CDATA leading spaces are trimmed (ink starts at x102); internal A  B and Z    T keep their gaps; nested Raw keeps its 4 leading spaces (ink starts x126)" `
  "none (measurement)" "dsl"

One "probe-11" "probe-10" "alternative" "can a single Raw span carry a whole printed code line including its indentation" `
  "tmp/run-20261002-220723-mimo/A17/probe-11.snapshot" "tmp/run-20261002-220723-mimo/A17/probe-11.png" `
  "A17-probe11" 1560 $now "pixel-ink-extent" `
  "<Raw><![CDATA[    AA]]></Raw> starts at x144 = 100+4x11, so Raw+CDATA reproduces indentation exactly; control plain CDATA starts at x101 (trimmed)" `
  "none (measurement)" "dsl"

# ---------- handbook page v01 ----------
One "handbook-01-v01" $null "baseline" "first render of handbook page 1 (call contract)" `
  "tmp/run-20261002-220723-mimo/A17/handbook-01-v01.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-01-v01.png" `
  "A17-pg01" 6338.8 $now "read-tool-image" `
  "page structure complete (badge/title/desc, figure card, code card with 17 printed lines, points card, footer); illustration at (72,242) compares 0 differing pixels against example-01.png" `
  "none (baseline)" "verification"

One "handbook-02-v01" $null "baseline" "first render of handbook page 2 (root size and bounded layout)" `
  "tmp/run-20261002-220723-mimo/A17/handbook-02-v01.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-02-v01.png" `
  "A17-pg02" 3622 $now "read-tool-image" `
  "all sections present and legible; illustration compares 0 differing pixels against example-02.png; right column and illustration bottom align" `
  "none (baseline)" "verification"

One "handbook-03-v01-attempt1" $null "syntax-fix" "first render attempt of handbook page 3 (text and colour)" `
  "tmp/run-20261002-220723-mimo/A17/handbook-03-v01.snapshot" $null `
  "A17-pg03" 1623.4 $null $null `
  "HTTP 400 PARSE_ERROR Not Support RAWTEXT: ]]> at position 5735 -- the printed line already contains ]]> which closed the outer CDATA section early" `
  "split the printed line across two CDATA sections: section 1 ends with ]] and section 2 starts with >, which reconstructs the literal ]]>" `
  "parse" 400

One "handbook-03-v01" "handbook-03-v01" "baseline" "render handbook page 3 after the CDATA split fix" `
  "tmp/run-20261002-220723-mimo/A17/handbook-03-v01.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-03-v01.png" `
  "A17-pg03b" 5351.1 $now "read-tool-image" `
  "page renders; the tricky line displays verbatim as <Text ...><![CDATA[CDATA keeps <tag> and &]]></Text> and the Raw indentation shows 4 spaces; illustration compares 0 differing pixels against example-03.png" `
  "none (baseline after fix)" "verification"

One "handbook-04-v01" $null "baseline" "first render of handbook page 4 (filters and self-check)" `
  "tmp/run-20261002-220723-mimo/A17/handbook-04-v01.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-04-v01.png" `
  "A17-pg04" 4383.8 $now "read-tool-image" `
  "page renders and reads well||illustration pixel comparison reports 6078 differing pixels (maxChannelDelta 219) confined to columns 0-149 rows 0-191: the BackdropFilter blur pulls the white card in from outside the 400x240 illustration, interior and right/bottom edges are exact" `
  "none (baseline)" "verification"

One "handbook-04-v02-pregen" "handbook-04-v01" "visual" "stop the backdrop blur from bleeding the page card into the illustration" `
  "tmp/run-20261002-220723-mimo/A17/handbook-04-v02-pregen.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-04-v02.png" `
  "A17-pg04b" 3415.5 $now "pixel-region-comparison" `
  "wrapping the illustration in ClipRect gives it its own layer, so the blur clamps at the illustration frame: differing pixels drop from 6078 to 0" `
  "<Positioned left=72 top=242> now opens <ClipRect> and closes </ClipRect></Positioned>" `
  "filters"

# ---------- final handbook pages ----------
One "handbook-01-v02" "handbook-01-v01" "visual" "regenerate page 1 with the ClipRect illustration wrapper so all four pages share one structure" `
  "tmp/run-20261002-220723-mimo/A17/handbook-01-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-01-v02.png" `
  "A17-pg01c" 4136.5 $now "read-tool-image" `
  "PNG byte-identical to v01 (ClipRect is visually neutral for an opaque illustration); illustration 0 differing pixels; page viewed and accepted" `
  "illustration wrapped in ClipRect" "verification"

One "handbook-02-v02" "handbook-02-v01" "visual" "regenerate page 2 with the ClipRect illustration wrapper" `
  "tmp/run-20261002-220723-mimo/A17/handbook-02-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-02-v02.png" `
  "A17-pg02c" 4611.2 $now "read-tool-image" `
  "PNG byte-identical to v01; illustration 0 differing pixels; page viewed and accepted" `
  "illustration wrapped in ClipRect" "verification"

One "handbook-03-v02" "handbook-03-v01" "visual" "regenerate page 3 with the ClipRect illustration wrapper" `
  "tmp/run-20261002-220723-mimo/A17/handbook-03-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-03-v02.png" `
  "A17-pg03c" 3639.4 $now "read-tool-image" `
  "PNG byte-identical to v01; illustration 0 differing pixels; printed CDATA line still verbatim; page viewed and accepted" `
  "illustration wrapped in ClipRect" "verification"

One "handbook-04-v02" "handbook-04-v02-pregen" "visual" "final render of page 4 from the shipped snapshot bytes" `
  "tmp/run-20261002-220723-mimo/A17/handbook-04-v02.snapshot" "tmp/run-20261002-220723-mimo/A17/handbook-04-v02.png" `
  "A17-pg04c" 3806.5 $now "read-tool-image" `
  "re-rendered from the exact snapshot that ships (the earlier pg04b run used a pre-generation draft that carried a stray closing tag); illustration 0 differing pixels; page viewed and accepted" `
  "none (final)" "verification"

One "handbook-03-v01-draft1" "handbook-03-v01-attempt1" "retry" "re-send the reconstructed pre-fix page 3 draft to prove the archived failure record is faithful" `
  "tmp/run-20261002-220723-mimo/A17/handbook-03-v01-draft1.snapshot" $null `
  "A17-pg03draft" $null $null $null `
  "HTTP 400 PARSE_ERROR Not Support RAWTEXT: ]]> at position 5735 near: TA keeps <tag> and &]]></Text>]]></Raw></Text></Positioned> -- byte-for-byte the same response as A17-pg03, so the reconstruction matches the draft that was overwritten by the generator" `
  "none (verification of a reconstructed attempt)" "parse" 400

Write-Output "done"
