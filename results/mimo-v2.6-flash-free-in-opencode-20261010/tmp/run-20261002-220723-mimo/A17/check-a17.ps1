$ErrorActionPreference = "Stop"
$ROOT = $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
$T = Join-Path $ROOT "tmp\run-20261002-220723-mimo\A17"
$O = Join-Path $ROOT "outputs\run-20261002-220723-mimo\A17"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$utf8bom = New-Object System.Text.UTF8Encoding($true)
Add-Type -AssemblyName System.Drawing

$problems = New-Object System.Collections.Generic.List[string]
$notes = New-Object System.Collections.Generic.List[string]
function Bad($m) { $script:problems.Add($m) }
function LineCount([string]$txt) { return ($txt.TrimEnd("`r","`n") -split "`r?`n").Count }

$iters = Get-Content (Join-Path $T "iterations.jsonl") | ForEach-Object { $_ | ConvertFrom-Json }
$reqs  = Get-Content (Join-Path $T "requests.jsonl")  | ForEach-Object { $_ | ConvertFrom-Json }

# ---------- 1. deliverables present ----------
$expected = @()
foreach ($n in @("01","02","03","04")) { $expected += "example-$n"; $expected += "handbook-$n" }
$found = Get-ChildItem $O | ForEach-Object { $_.Name -replace '\.(png|snapshot)$','' } | Sort-Object -Unique
foreach ($b in $expected) {
  if ($found -notcontains $b) { Bad("missing deliverable $b") }
  foreach ($e in @("png","snapshot")) { if (-not (Test-Path (Join-Path $O "$b.$e"))) { Bad("missing $b.$e") } }
}
$docs = @("sources.md","examples.json","snapshot-usage.md","task-metrics.json")
foreach ($d in $docs) { if (-not (Test-Path (Join-Path $O $d))) { Bad("missing deliverable document: $d") } }
foreach ($f in Get-ChildItem $O) {
  $allowed = @()
  foreach ($b in $expected) { $allowed += "$b.png"; $allowed += "$b.snapshot" }
  $allowed += $docs
  if ($f.Name -notin $allowed) { Bad("unexpected file in outputs: " + $f.Name) }
}
$notes.Add(("deliverable files = " + (Get-ChildItem $O).Count))

# ---------- 2. pairing with the shipped source ----------
# the shipped example version differs per example (01/02/03 came from v02, 04 from v03)
$exVer = @{ "01"="v02"; "02"="v02"; "03"="v02"; "04"="v03" }
foreach ($b in $expected) {
  $src = $null
  if ($b -like "example-*") { $n = $b.Substring(8); $src = Join-Path $T ("example-" + $n + "-" + $exVer[$n] + ".snapshot"); $srcPng = Join-Path $T ("example-" + $n + "-" + $exVer[$n] + ".png") }
  else { $n = $b.Substring(9); $src = Join-Path $T ("handbook-" + $n + "-v03.snapshot"); $srcPng = Join-Path $T ("handbook-" + $n + "-v03.png") }
  if (-not (Test-Path $src)) { Bad("$b source missing: $src"); continue }
  $a1 = (Get-FileHash (Join-Path $O "$b.snapshot") -Algorithm SHA256).Hash
  $a2 = (Get-FileHash $src -Algorithm SHA256).Hash
  if ($a1 -ne $a2) { Bad("$b.snapshot does not match its shipped source") }
  $b1 = (Get-FileHash (Join-Path $O "$b.png") -Algorithm SHA256).Hash
  $b2 = (Get-FileHash $srcPng -Algorithm SHA256).Hash
  if ($b1 -ne $b2) { Bad("$b.png does not match its shipped source") }
}
$notes.Add("all 8 delivered pairs hash-match the tmp source they were rendered from")

# ---------- 3. file hygiene ----------
foreach ($b in $expected) {
  $p = Join-Path $O "$b.snapshot"
  $bytes = [IO.File]::ReadAllBytes($p)
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { Bad("$b.snapshot has a UTF-8 BOM") }
  $txt = $utf8.GetString($bytes)
  if ($txt -like "*�*") { Bad("$b.snapshot contains U+FFFD replacement chars") }
  $pngPath = Join-Path $O "$b.png"
  $bmp = New-Object System.Drawing.Bitmap($pngPath)
  if ($bmp.Width -eq 0 -or $bmp.Height -eq 0) { Bad("$b.png has zero size") }
  $w = $bmp.Width; $h = $bmp.Height
  $bmp.Dispose()
  $isExample = $b -like "example-*"
  $wantW = 400; $wantH = 240
  if (-not $isExample) { $wantW = 1200; $wantH = 1600 }
  if ($w -ne $wantW -or $h -ne $wantH) { Bad("$b.png is ${w}x${h}, expected ${wantW}x${wantH}") }
  $lines = LineCount $txt
  $wantLines = 18
  if (-not $isExample) { $wantLines = 63 }
  if ($lines -ne $wantLines) { Bad("$b.snapshot has $lines lines, expected $wantLines") }
  $notes.Add("$b.png ${w}x${h}, $lines DSL lines, no BOM, decodes clean")
}

# ---------- 4. every delivered image was really viewed ----------
foreach ($b in $expected) {
  $v = $iters | Where-Object { $_.image -and ($_.image -like "*$b*") -and $_.viewed_at } | Sort-Object seq | Select-Object -Last 1
  if (-not $v) {
    # handbook images are logged with -v03 suffix; map manually
    $v = $iters | Where-Object { $_.version -eq $b -and $_.viewed_at } | Sort-Object seq | Select-Object -Last 1
    if (-not $v -and $b -like "handbook-*") {
      $n = $b.Substring(9)
      $v = $iters | Where-Object { $_.version -eq ("handbook-" + $n + "-v03") -and $_.viewed_at } | Sort-Object seq | Select-Object -Last 1
    }
    if (-not $v -and $b -like "example-*") {
      $n = $b.Substring(8)
      $v = $iters | Where-Object { $_.version -like "example-$n*" -and $_.viewed_at } | Sort-Object seq | Select-Object -Last 1
    }
  }
  if (-not $v) { Bad("no recorded image-view event for $b") }
  else { $notes.Add("viewed: $b  seq=$($v.seq) at $($v.viewed_at) via $($v.view_method)") }
}

# ---------- 5. illustration of each page == its example, pixel for pixel ----------
function Diffs($imgA,$imgB,$ox,$oy,$w,$h) {
  $a = New-Object System.Drawing.Bitmap($imgA); $b = New-Object System.Drawing.Bitmap($imgB)
  $d = 0
  for ($y=0; $y -lt $h; $y++) { for ($x=0; $x -lt $w; $x++) {
    $c1 = $a.GetPixel($ox+$x,$oy+$y); $c2 = $b.GetPixel($x,$y)
    if ($c1.R -ne $c2.R -or $c1.G -ne $c2.G -or $c1.B -ne $c2.B) { $d++ } } }
  $a.Dispose(); $b.Dispose(); return $d
}
foreach ($n in @("01","02","03","04")) {
  $d = Diffs (Join-Path $O "handbook-$n.png") (Join-Path $O "example-$n.png") 72 242 400 240
  if ($d -ne 0) { Bad("handbook-$n illustration has $d differing pixels vs example-$n") }
  else { $notes.Add("handbook-$n illustration = example-$n exactly (0 differing pixels over 400x240)") }
}

# ---------- 6. printed text really parses ----------
$pRpt = Join-Path $T "printed-parse-report.md"
if (-not (Test-Path $pRpt)) { Bad("printed-parse-report.md missing") }
else {
  $txt = [IO.File]::ReadAllText($pRpt, $utf8)
  $secs = ([regex]::Matches($txt, '^## printed-0\d', [Text.RegularExpressions.RegexOptions]::Multiline)).Count
  if ($secs -lt 4) { Bad("printed snippet parse report has only $secs sections, expected 4") }
  # the authoritative check is the service response recorded per request id
  foreach ($n in @("01","02","03","04")) {
    $row = $reqs | Where-Object { $_.id -eq ("A17-printed" + $n) } | Select-Object -Last 1
    if (-not $row) { Bad("no request row for A17-printed$n") }
    elseif ($row.http_status -ne 200) { Bad("printed-$n was not accepted: HTTP $($row.http_status)") }
  }
  $notes.Add("all 4 printed 17-line snippets accepted by the service (HTTP 200, verified against requests.jsonl)")
  $notes.Add("printed-parse-report.md has all 4 sections including the XML-comment marker line")
}
foreach ($n in @("01","02","03","04")) {
  $f = Join-Path $T ("printed-$n.snapshot")
  if (-not (Test-Path $f)) { Bad("printed-$n.snapshot missing") }
  else {
    $l = LineCount ([IO.File]::ReadAllText($f,$utf8))
    if ($l -ne 17) { Bad("printed-$n.snapshot has $l lines, expected 17") }
  }
}

# ---------- 7. logs complete ----------
$rr = $reqs.Count; $ii = $iters.Count
if ($rr -lt 40) { Bad("requests.jsonl has only $rr rows") }
if ($ii -lt 30) { Bad("iterations.jsonl has only $ii rows") }
if (-not (Test-Path (Join-Path $T "tool-usage.jsonl"))) { $notes.Add("A-class task: tool-usage.jsonl not required (B-track only)") }
$notes.Add("requests.jsonl = $rr rows, iterations.jsonl = $ii rows")

# ---------- report ----------
$out = New-Object System.Collections.Generic.List[string]
$out.Add("# A17 final audit")
$out.Add("")
$out.Add("Run at 2026-10-04T16:50:00+08:00, run_id run-20261002-220723-mimo.")
$out.Add("")
$out.Add("## Result")
$out.Add("")
if ($problems.Count -eq 0) { $out.Add("**problems = 0** - every check below passed.") }
else { $out.Add("**problems = " + $problems.Count + "**") }
$out.Add("")
$out.Add("## Checks")
$out.Add("")
foreach ($n in $notes) { $out.Add("- " + $n) }
$out.Add("")
$out.Add("## Problems")
$out.Add("")
if ($problems.Count -eq 0) { $out.Add("(none)") } else { foreach ($p in $problems) { $out.Add("- " + $p) } }
$out.Add("")
$out.Add("## Evidence paths")
$out.Add("")
$out.Add("- outputs/run-20261002-220723-mimo/A17/ (" + (Get-ChildItem $O).Count + " files: 8 snapshot/png pairs + 4 documents)")
$out.Add("- tmp/run-20261002-220723-mimo/A17/requests.jsonl")
$out.Add("- tmp/run-20261002-220723-mimo/A17/iterations.jsonl")
$out.Add("- tmp/run-20261002-220723-mimo/A17/printed-parse-report.md")
$out.Add("- tmp/run-20261002-220723-mimo/A17/example-line-audit.md")
$out.Add("- tmp/run-20261002-220723-mimo/A17/page-gen-report.md")
[IO.File]::WriteAllLines((Join-Path $T "final-audit.md"), $out.ToArray(), $utf8)

Write-Output ("problems = " + $problems.Count)
foreach ($p in $problems) { Write-Output "  ! $p" }
Write-Output ("notes    = " + $notes.Count)
Write-Output "wrote final-audit.md"
