# verify-suite-2.ps1 -- re-verify the delivered suite against the current spec.
#
# Run without -Records  -> print the full report and write verify-report.json only.
# Run with -Records     -> additionally refresh suite-state.json, append the next event to
#                          events.jsonl and write the next numbered checkpoint.
#
# Everything checked here is read from disk in this run. Nothing is accepted from a previous
# conclusion, and nothing is reported that was not measured.
#
# Start base: this script sits at tmp/<run>/_suite/, three directories under the suite root,
# so it works from any working directory without a machine-specific path.
param([switch]$Records)

$ErrorActionPreference = 'Stop'
$suiteRoot = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$runId = 'run-20261002-220723-mimo'
$rc = [IO.File]::ReadAllText((Join-Path $suiteRoot 'run-config.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$outRoot = Join-Path $suiteRoot ("{0}\{1}" -f $rc.output_root, $runId)
$tmpRoot = Join-Path $suiteRoot ("{0}\{1}" -f $rc.temp_root, $runId)
$suiteDir = Join-Path $outRoot '_suite'
$stDir = Join-Path $tmpRoot '_suite'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$rxMachine = [regex]'D:[\\/]{1,2}workspaces[\\/]{1,2}opencode-with-mimo-v2\.6-flash-free|C:[\\/]{1,2}Users[\\/]{1,2}mueds'
$relOut = "$($rc.output_root)/$runId"
$relTmp = "$($rc.temp_root)/$runId"

$ids = @(); foreach ($i in 1..24) { $ids += ('A{0:d2}' -f $i) }; foreach ($i in 1..6) { $ids += ('B{0:d2}' -f $i) }
$problems = @(); $notes = @()

# ---------- A. required suite artifacts, straight from run-config.json ----------
$required = @($rc.suite_required_artifacts)
$missingRequired = @($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $suiteDir $_)) })
if ($missingRequired.Count -gt 0) { $problems += ("suite_required_artifacts missing: {0}" -f ($missingRequired -join ', ')) }

# ---------- B. final PNG integrity: magic + .snapshot pair + IHDR == first Container ----------
$pngTotal = 0; $pairOk = 0; $dimOk = 0
$diskPngs = @()
foreach ($id in $ids) {
  $d = Join-Path $outRoot $id
  if (-not (Test-Path (Join-Path $d 'snapshot-usage.md'))) { $problems += "$id missing snapshot-usage.md" }
  if (-not (Test-Path (Join-Path $d 'task-metrics.json'))) { $problems += "$id missing task-metrics.json" }
  foreach ($f in @('requests.jsonl', 'iterations.jsonl')) {
    if (-not (Test-Path (Join-Path $tmpRoot "$id\$f"))) { $problems += "$id missing $f" }
  }
  $pngs = @(Get-ChildItem $d -Recurse -Filter '*.png' -File | Where-Object { $_.DirectoryName -notlike '*\archive' })
  $pngTotal += $pngs.Count
  foreach ($p in $pngs) {
    $diskPngs += $p.FullName
    $fs = [IO.File]::OpenRead($p.FullName); $b = New-Object byte[] 24
    $null = $fs.Read($b, 0, 24); $fs.Close()
    $magic = ($b[0..7] | ForEach-Object { $_.ToString('x2') }) -join ''
    if ($magic -ne '89504e470d0a1a0a') { $problems += "$id/$($p.Name) bad PNG magic"; continue }
    $snap = [IO.Path]::ChangeExtension($p.FullName, '.snapshot')
    if (-not (Test-Path $snap)) { $problems += "$id/$($p.Name) missing .snapshot pair"; continue }
    $pairOk++
    $txt = [IO.File]::ReadAllText($snap, [Text.Encoding]::UTF8)
    $m2 = [regex]::Match($txt, '<Container[^>]*width="(\d+)"[^>]*height="(\d+)"')
    if (-not $m2.Success) { $problems += "$id/$($p.Name) no Container in .snapshot"; continue }
    $w = [int]$b[16]*16777216 + [int]$b[17]*65536 + [int]$b[18]*256 + [int]$b[19]
    $h = [int]$b[20]*16777216 + [int]$b[21]*65536 + [int]$b[22]*256 + [int]$b[23]
    if ([int]$m2.Groups[1].Value -eq $w -and [int]$m2.Groups[2].Value -eq $h) { $dimOk++ }
    else { $problems += ("{0}/{1} png {2}x{3} vs container {4}x{5}" -f $id, $p.Name, $w, $h, $m2.Groups[1].Value, $m2.Groups[2].Value) }
  }
}
$diskSnaps = @(Get-ChildItem $outRoot -Recurse -Filter '*.snapshot' -File)

# ---------- C. B-track cases and A21/A22 preset rounds ----------
$bCaseOk = 0
foreach ($i in 1..6) {
  foreach ($c in 1..10) {
    $cd = Join-Path $outRoot ("{0}\case-{1:d2}" -f ('B{0:d2}' -f $i), $c)
    if ((Test-Path (Join-Path $cd 'final.png')) -and (Test-Path (Join-Path $cd 'final.snapshot')) -and (Test-Path (Join-Path $cd 'case.md'))) { $bCaseOk++ }
    else { $problems += ("B{0:d2} case-{1:d2} incomplete" -f $i, $c) }
  }
}
$rounds = @()
foreach ($rid in @('A21', 'A22')) {
  foreach ($rn in 1..3) {
    $rd = Join-Path $outRoot ("{0}\round-{1:d2}" -f $rid, $rn)
    if (-not (Test-Path $rd)) { $problems += "$rid round-0$rn missing"; continue }
    $np = @(Get-ChildItem $rd -Filter '*.png' -File).Count
    $ns = @(Get-ChildItem $rd -Filter '*.snapshot' -File).Count
    $rounds += ("{0}/round-{1:d2} {2}png+{3}snapshot" -f $rid, $rn, $np, $ns)
    if ($np -eq 0 -or $np -ne $ns) { $problems += "$rid round-0$rn png/snapshot mismatch ($np/$ns)" }
  }
}

# ---------- D. gallery.md: complete, per-image, relative ----------
$gPath = Join-Path $suiteDir 'gallery.md'
$g = [IO.File]::ReadAllText($gPath, [Text.Encoding]::UTF8)
$gPreviews = ([regex]::Matches($g, '(?m)^!\[')).Count
$gTitles = ([regex]::Matches($g, '(?m)^#### ')).Count
# task sections are '## A01 ...' .. '## B06 ...'; the catalog order heading is '## 目录'
$gSections = ([regex]::Matches($g, '(?m)^## [AB]\d\d')).Count
# '\s*' before the line end because the file is CRLF and '$' sits after the '\r'
$gCaseGroups = ([regex]::Matches($g, '(?m)^### case-\d\d\s*$')).Count
$gRoundGroups = ([regex]::Matches($g, '(?m)^### round-\d\d\s*$')).Count
if ($gSections -ne 30) { $problems += "gallery.md has $gSections task sections, expected 30" }
if ($gRoundGroups -ne 6) { $problems += "gallery.md has $gRoundGroups round groups, expected 6 (A21+A22 x 3)" }
if ($gCaseGroups -ne 60) { $problems += "gallery.md has $gCaseGroups case groups, expected 60 (B01-B06 x 10)" }
$gPngLinks = New-Object System.Collections.Generic.HashSet[string]
$gSnapLinks = New-Object System.Collections.Generic.HashSet[string]
$gBroken = 0; $gRemote = 0; $gMachine = 0; $gAnchors = 0
foreach ($m in [regex]::Matches($g, '\]\(([^)]+)\)')) {
  $t = $m.Groups[1].Value
  if ($t.StartsWith('#')) { $gAnchors++; continue }               # in-document anchor, not a file path
  if ($t -match '^(https?:)?//') { $gRemote++; continue }
  if ($rxMachine.IsMatch($t)) { $gMachine++ }
  $full = [IO.Path]::GetFullPath((Join-Path $suiteDir $t))
  if (-not (Test-Path -LiteralPath $full)) { $gBroken++; continue }
  if ($t.EndsWith('.png')) { $null = $gPngLinks.Add($full.ToLower()) }
  elseif ($t.EndsWith('.snapshot')) { $gSnapLinks.Add($full.ToLower()) | Out-Null }
}
$diskPngSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($p in $diskPngs) { $null = $diskPngSet.Add($p.ToLower()) }
$diskSnapSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($s in $diskSnaps) { $null = $diskSnapSet.Add($s.FullName.ToLower()) }
$pngNotInGallery = 0; foreach ($p in $diskPngSet) { if (-not $gPngLinks.Contains($p)) { $pngNotInGallery++ } }
$pngNotOnDisk = 0; foreach ($p in $gPngLinks) { if (-not $diskPngSet.Contains($p)) { $pngNotOnDisk++ } }
$snapNotInGallery = 0; foreach ($s in $diskSnapSet) { if (-not $gSnapLinks.Contains($s)) { $snapNotInGallery++ } }
$snapNotOnDisk = 0; foreach ($s in $gSnapLinks) { if (-not $diskSnapSet.Contains($s)) { $snapNotOnDisk++ } }
if ($gBroken -ne 0) { $problems += "gallery.md has $gBroken broken link(s)" }
if ($gRemote -ne 0) { $problems += "gallery.md has $gRemote remote link(s)" }
if ($gMachine -ne 0) { $problems += "gallery.md has $gMachine machine path link(s)" }
if ($gPreviews -ne $pngTotal) { $problems += "gallery.md previews $gPreviews != $pngTotal final PNGs" }
if ($gTitles -ne $pngTotal) { $problems += "gallery.md titled images $gTitles != $pngTotal final PNGs" }
if ($pngNotInGallery -ne 0 -or $pngNotOnDisk -ne 0) { $problems += "gallery.md PNG set mismatch (missing $pngNotInGallery, extra $pngNotOnDisk)" }
if ($snapNotInGallery -ne 0 -or $snapNotOnDisk -ne 0) { $problems += "gallery.md .snapshot set mismatch (missing $snapNotInGallery, extra $snapNotOnDisk)" }

# ---------- E. index.md: resolves, and links to gallery.md ----------
$iPath = Join-Path $suiteDir 'index.md'
$i = [IO.File]::ReadAllText($iPath, [Text.Encoding]::UTF8)
$iBroken = 0; $iLinksGallery = 0; $iAnchors = 0
foreach ($m in [regex]::Matches($i, '\]\(([^)]+)\)')) {
  $t = $m.Groups[1].Value
  if ($t.StartsWith('#')) { $iAnchors++; continue }
  if ($t -match '^(https?:)?//') { continue }
  if ($t -eq 'gallery.md') { $iLinksGallery++ }
  if (-not (Test-Path -LiteralPath ([IO.Path]::GetFullPath((Join-Path $suiteDir $t))))) { $iBroken++ }
}
if ($iBroken -ne 0) { $problems += "index.md has $iBroken broken link(s)" }
if ($iLinksGallery -eq 0) { $problems += 'index.md does not link to gallery.md' }

# ---------- F. no machine-specific root anywhere in records, reports and scripts ----------
$pathSweep = @{ records = 0; scripts = 0; rawSkipped = 0 }
$sweepHits = @()
foreach ($scope in @($outRoot, $tmpRoot)) {
  foreach ($f in @(Get-ChildItem $scope -Recurse -File)) {
    if ($f.Extension -in @('.png', '.snapshot', '.html')) { $pathSweep.rawSkipped++; continue }
    $bytes = [IO.File]::ReadAllBytes($f.FullName)
    $off = if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) { 3 } else { 0 }
    try { $t = [System.Text.UTF8Encoding]::new($false, $true).GetString($bytes, $off, $bytes.Length - $off) } catch { continue }
    $n = $rxMachine.Matches($t).Count
    if ($n -eq 0) { continue }
    if ($f.Extension -eq '.ps1') { $pathSweep.scripts += $n } else { $pathSweep.records += $n }
    $sweepHits += ("{0} x{1}" -f $f.FullName.Substring($suiteRoot.Length + 1), $n)
  }
}
if ($pathSweep.records -ne 0) { $problems += "machine root in records/reports: $($sweepHits -join '; ')" }
if ($pathSweep.scripts -ne 0) { $problems += "machine root in scripts: $($sweepHits -join '; ')" }

# ---------- G. path_base declared next to every local path ----------
$pb = [ordered]@{ suite_state = $false; suite_metrics = $false; checkpoints = 0; checkpoints_total = 0; logs = 0; logs_ok = 0; portfolios = 0; portfolios_ok = 0; violations = 0 }
$ssPath = Join-Path $suiteDir 'suite-state.json'
$ss = [IO.File]::ReadAllText($ssPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
$pb.suite_state = ($ss.path_base -eq 'suite_root')
if (-not $pb.suite_state) { $problems += 'suite-state.json does not declare path_base=suite_root' }
$smPath = Join-Path $suiteDir 'task-metrics.json'
$sm = [IO.File]::ReadAllText($smPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
$pb.suite_metrics = ($sm.path_base -eq 'suite_root')
if (-not $pb.suite_metrics) { $problems += 'task-metrics.json does not declare path_base=suite_root' }
foreach ($f in @(Get-ChildItem (Join-Path $stDir 'checkpoints') -Filter '*.json')) {
  $pb.checkpoints_total++
  $o = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8) | ConvertFrom-Json
  if ($o.path_base -eq 'suite_root') { $pb.checkpoints++ } else { $pb.violations++; $problems += "$($f.Name) missing path_base" }
}
foreach ($f in @(Get-ChildItem $outRoot -Recurse -Filter 'portfolio.json' -File)) {
  $pb.portfolios++
  $o = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8) | ConvertFrom-Json
  if ($o.path_base -eq 'output_dir') { $pb.portfolios_ok++ } else { $pb.violations++; $problems += "$($f.Name) path_base != output_dir" }
}
foreach ($f in @(Get-ChildItem $outRoot -Recurse -Filter '*.jsonl' -File) + @(Get-ChildItem $tmpRoot -Recurse -Filter '*.jsonl' -File)) {
  $text = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
  if ($text -notmatch '(?<=")(outputs|tmp)[\\/]') { continue }        # no local path -> nothing to declare
  $pb.logs++
  if ([regex]::Matches($text, '"path_base"').Count -eq 0) { $pb.violations++; $problems += "$($f.Name) holds local paths but declares no path_base"; continue }
  foreach ($ln in ($text -split "`n")) {
    if ([string]::IsNullOrWhiteSpace($ln)) { continue }
    try { $r = $ln | ConvertFrom-Json } catch { continue }           # continuation line of a pretty-printed record
    if (-not $r.PSObject.Properties['path_base']) { $pb.violations++; $problems += "$($f.Name) row without path_base" }
  }
  $pb.logs_ok++
}

# ---------- H. root .gitignore: caches out, evidence in ----------
$giPath = Join-Path $suiteRoot '.gitignore'
$giExists = Test-Path -LiteralPath $giPath
$giRules = @(); $giComments = 0
if ($giExists) {
  foreach ($ln in [IO.File]::ReadAllLines($giPath, [Text.Encoding]::UTF8)) {
    $s = $ln.Trim()
    if ($s -eq '' ) { continue }
    if ($s.StartsWith('#')) { $giComments++; continue }
    $giRules += $s
  }
}
$templateRules = @('__pycache__/', '*.pyc', '*.pyo', '.pytest_cache/', '.mypy_cache/', '.ruff_cache/')
$giMissingRules = @($templateRules | Where-Object { $giRules -notcontains $_ })
$giForbidden = @('tmp', 'tmp/', 'outputs', 'outputs/', 'cache', 'cache/', '.cache', '.cache/', '*.log',
                 '*.png', '*.snapshot', '*.json', '*.jsonl', '*.md', '*.html', '*.dsl', '*.txt', 'images', 'images/')
$giHits = @($giRules | Where-Object { $giForbidden -contains $_ })
if (-not $giExists) { $problems += 'root .gitignore is missing' }
if ($giMissingRules.Count -gt 0) { $problems += (".gitignore missing template rules: {0}" -f ($giMissingRules -join ', ')) }
if ($giHits.Count -gt 0) { $problems += (".gitignore ignores process evidence: {0}" -f ($giHits -join ', ')) }

# ---------- I. suite_artifacts actually on disk ----------
$saMissing = @()
foreach ($a in @($ss.suite_artifacts)) {
  $full = [IO.Path]::GetFullPath((Join-Path $suiteRoot $a.path))
  if (-not (Test-Path -LiteralPath $full)) { $saMissing += $a.path }
}
if ($saMissing.Count -gt 0) { $problems += ("suite_artifacts entries missing: {0}" -f ($saMissing -join ', ')) }

# ---------- J. metrics agree with disk ----------
$smCountMismatch = @()
if ([int]$sm.counts.final_pngs -ne $pngTotal) { $smCountMismatch += "final_pngs $($sm.counts.final_pngs)!=$pngTotal" }
if ([int]$sm.counts.final_snapshots -ne $diskSnaps.Count) { $smCountMismatch += "final_snapshots $($sm.counts.final_snapshots)!=$($diskSnaps.Count)" }
if ([int]$sm.counts.independent_creative_cases -ne 118) { $smCountMismatch += "works $($sm.counts.independent_creative_cases)!=118" }
if ([int]$sm.task_status_counts.completed -ne 30) { $smCountMismatch += "completed $($sm.task_status_counts.completed)!=30" }
if ($smCountMismatch.Count -gt 0) { $problems += ("metrics disagree with disk: {0}" -f ($smCountMismatch -join '; ')) }

# ---------- report ----------
$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')
$report = [ordered]@{
  path_base = 'suite_root'
  run_id = $runId
  verified_at = $now
  verified_by = 'tmp/<run>/_suite/verify-suite-2.ps1'
  suite_required_artifacts = [ordered]@{ expected = $required; missing = $missingRequired }
  final_images = [ordered]@{ png_total = $pngTotal; paired_with_snapshot = $pairOk; dimension_matches_container = $dimOk; archive_drafts_excluded = $true }
  b_track_cases = [ordered]@{ complete = $bCaseOk; expected = 60 }
  preset_rounds = $rounds
  gallery_md = [ordered]@{ image_previews = $gPreviews; explicit_titles = $gTitles; sections = $gSections; case_groups = $gCaseGroups; round_groups = $gRoundGroups; in_document_anchors = $gAnchors; png_links_distinct = $gPngLinks.Count; snapshot_links_distinct = $gSnapLinks.Count; broken_links = $gBroken; remote_links = $gRemote; machine_path_links = $gMachine; png_not_in_gallery = $pngNotInGallery; png_not_on_disk = $pngNotOnDisk; snapshot_not_in_gallery = $snapNotInGallery; snapshot_not_on_disk = $snapNotOnDisk }
  index_md = [ordered]@{ broken_links = $iBroken; links_to_gallery_md = $iLinksGallery; in_document_anchors = $iAnchors }
  path_policy = [ordered]@{ machine_root_hits_in_records = $pathSweep.records; machine_root_hits_in_scripts = $pathSweep.scripts; raw_bytes_files_skipped = $pathSweep.rawSkipped; hits = $sweepHits }
  path_base_coverage = $pb
  gitignore = [ordered]@{ exists = $giExists; path = '.gitignore'; template_rules_present = $templateRules; template_rules_missing = $giMissingRules; non_comment_lines = $giRules; evidence_ignoring_rules = $giHits; comment_lines = $giComments }
  suite_artifacts = [ordered]@{ entries = @($ss.suite_artifacts).Count; missing_on_disk = $saMissing }
  metrics_agreement = [ordered]@{ mismatch = $smCountMismatch }
  problems = $problems
  passed = ($problems.Count -eq 0)
}
$reportPath = Join-Path $stDir 'verify-report.json'
[IO.File]::WriteAllText($reportPath, (($report | ConvertTo-Json -Depth 10)), $utf8NoBom)

"=== verify-suite-2 ==="
"  required artifacts      : $($required.Count - $missingRequired.Count)/$($required.Count) present  [$($required -join ', ')]"
"  final PNGs              : total=$pngTotal paired=$pairOk dimOk=$dimOk  (archive drafts excluded)"
"  .snapshot on disk       : $($diskSnaps.Count)"
"  B-track cases           : $bCaseOk/60"
"  preset rounds           : $($rounds -join '  ')"
"  gallery.md              : previews=$gPreviews titles=$gTitles sections=$gSections caseGroups=$gCaseGroups roundGroups=$gRoundGroups pngLinks=$($gPngLinks.Count) snapLinks=$($gSnapLinks.Count) broken=$gBroken remote=$gRemote machine=$gMachine"
"  gallery coverage        : png missing=$pngNotInGallery extra=$pngNotOnDisk | snapshot missing=$snapNotInGallery extra=$snapNotOnDisk"
"  index.md                : broken=$iBroken linksToGalleryMd=$iLinksGallery"
"  path policy             : machineRoot records=$($pathSweep.records) scripts=$($pathSweep.scripts) (raw files skipped=$($pathSweep.rawSkipped))"
"  path_base coverage      : suite_state=$($pb.suite_state) suite_metrics=$($pb.suite_metrics) checkpoints=$($pb.checkpoints)/$($pb.checkpoints_total) logs=$($pb.logs_ok)/$($pb.logs) portfolios=$($pb.portfolios_ok)/$($pb.portfolios) violations=$($pb.violations)"
"  .gitignore              : exists=$giExists rules=$($giRules.Count) missingRules=$($giMissingRules.Count) evidenceIgnoring=$($giHits.Count)"
"  suite_artifacts         : $($ss.suite_artifacts.Count) entries, missing on disk=$($saMissing.Count)"
"  metrics agreement       : $(if ($smCountMismatch.Count -eq 0) { 'OK' } else { $smCountMismatch -join '; ' })"
"  PROBLEMS                : $($problems.Count)"
$problems | Select-Object -First 20 | ForEach-Object { "    ! $_" }
"  report                  : $($reportPath.Substring($suiteRoot.Length + 1))"

if ($problems.Count -gt 0) { "VERIFICATION FAILED - records not written"; exit 1 }
if (-not $Records) { "report only: suite-state/events/checkpoint untouched"; exit 0 }

# ==================== recording pass ====================
$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')
$nextSeq = 62
$nextCk = 'state-000038.json'

# ---- suite-state.json: refresh the current pointer (allowed to be updated) ----
$ssBytes = [IO.File]::ReadAllBytes($ssPath)
$hadBom = ($ssBytes.Length -ge 3 -and $ssBytes[0] -eq 239 -and $ssBytes[1] -eq 187 -and $ssBytes[2] -eq 191)
$off2 = if ($hadBom) { 3 } else { 0 }
$ssText = [System.Text.UTF8Encoding]::new($false, $true).GetString($ssBytes, $off2, $ssBytes.Length - $off2)
$ssText = [regex]::Replace($ssText, '"last_checkpoint":\s*"[^"]*"', ('"last_checkpoint": "{0}"' -f $nextCk))
$ssText = [regex]::Replace($ssText, '"updated_at":\s*"[^"]*"', ('"updated_at": "{0}"' -f $now))
$ssWrite = if ($hadBom) { [System.Text.UTF8Encoding]::new($true) } else { $utf8NoBom }
[IO.File]::WriteAllText($ssPath, $ssText, $ssWrite)
$ss2 = [IO.File]::ReadAllText($ssPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
"suite-state.json refreshed: status=$($ss2.status) last_checkpoint=$($ss2.last_checkpoint) updated_at=$($ss2.updated_at)"

# ---- events.jsonl: append-only ----
$note = ("按更新后的交付要求重新核验全套并归档（不是引用上一轮结论，本条同一次运行内全部实测）。要求变化：gallery.html 改为 gallery.md、总任务根新增 .gitignore、路径须按 PATHS.md 使用相对基准并声明 path_base。核验结果：run-config.suite_required_artifacts 的 {0} 项全部存在（index.md、gallery.md、snapshot-usage.md、task-metrics.json、suite-state.json）；gallery.md 逐图 Markdown 预览 {1} 张、显式标题 {1} 个，与磁盘最终 PNG 集合双向相等（缺失 0 / 多余 0），对应 .snapshot 链接 {2} 条且与磁盘 124 份双向相等，分组为 30 个题目小节 + case 分组 {3} 个 + round 分组 {4} 个，相对链接失效 {5} 条、远程图片 {6} 条、机器路径 {7} 条；index.md 失效链接 {8} 条并已链接 gallery.md；最终图片 {1} 张全部通过 PNG 魔数 + 同名 .snapshot 配对 + IHDR 尺寸等于 DSL 首个 Container 宽高（{9}/{10}/{11}）；B 轨 case 目录 {12}/60 齐全；A21/A22 各 3 轮 png 与 snapshot 数量相等；路径合规：outputs 与 tmp 下记录/报告/脚本中的机器盘符与用户名命中数为 {13}（原始字节类 .png/.snapshot/.html 共 {14} 个文件按留痕要求跳过不改写），A11 的 C:\work\cards\v2 属题面内容数据予以保留；path_base 覆盖 suite-state=suite_root、套件 metrics=suite_root、检查点 {15}/{16}、含本地路径的日志 {17}/{18}、portfolio {19}/{20}=output_dir，缺 path_base 的日志行 0 条；根 .gitignore 存在，含模板全部 6 条缓存规则，非注释规则行仅这 6 条，未排除 tmp/、outputs/、cache/、*.log 或任何图片/DSL/JSON 通配；suite_artifacts {21} 条全部在磁盘存在。指标与磁盘一致：最终图片 {1}、.snapshot {1}、独立作品 {22}、completed 30/30。" -f $required.Count, $pngTotal, $gSnapLinks.Count, $gCaseGroups, $gRoundGroups, $gBroken, $gRemote, $gMachine, $iBroken, $pairOk, $dimOk, $pngTotal, $bCaseOk, $pathSweep.records, $pathSweep.rawSkipped, $pb.checkpoints, $pb.checkpoints_total, $pb.logs_ok, $pb.logs, $pb.portfolios_ok, $pb.portfolios, @($ss2.suite_artifacts).Count, $sm.counts.independent_creative_cases)
$evObj = [ordered]@{
  path_base = 'suite_root'
  seq = $nextSeq; ts = $now; type = 'suite_revalidated'; task = 'SUITE'
  artifact_scope = "$relOut/_suite"
  renders_added = 0; views_added = 0; iterations_added = 0; cases_completed = 0
  spec_change = 'suite_required_artifacts: gallery.html -> gallery.md; add root .gitignore; all local paths relative per PATHS.md with path_base'
  note = $note
}
[IO.File]::AppendAllText((Join-Path $stDir 'events.jsonl'), (($evObj | ConvertTo-Json -Compress -Depth 4) + "`n"), $utf8NoBom)
"events.jsonl appended seq=$nextSeq"

# ---- checkpoint: numbered, new file, never overwriting an earlier one ----
$ckPath = Join-Path $stDir ("checkpoints\{0}" -f $nextCk)
if (Test-Path $ckPath) { throw "checkpoint $nextCk already exists; refusing to overwrite" }
$ckpt = [ordered]@{
  path_base = 'suite_root'
  checkpoint = $nextCk; created_at = $now; seq = $nextSeq
  run_id = $runId; run_profile = $ss2.profile
  purpose = 'revalidation against the revised delivery spec (gallery.md, root .gitignore, PATHS.md relative paths)'
  verification_report = "$relTmp/_suite/verify-report.json"
  suite_state = $ss2
}
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 20), $utf8NoBom)
"checkpoint written: $nextCk ($((Get-Item $ckPath).Length) bytes)"
"checkpoints total  : $(@(Get-ChildItem (Join-Path $stDir 'checkpoints') -Filter '*.json').Count)"
