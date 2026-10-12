param([Parameter(Mandatory=$true)][string]$OutJsonl, [Parameter(Mandatory=$true)][string]$TmpDir)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Sha16([string]$p) { if (Test-Path -LiteralPath $p) { return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.Substring(0,16) } return $null }
function Bytes([string]$p) { if (Test-Path -LiteralPath $p) { return (Get-Item -LiteralPath $p).Length } return $null }

$rows = New-Object System.Collections.Generic.List[object]

# ---------------------------------------------------------------- it01 baseline --
$rows.Add([pscustomobject]@{
  id = 'A19-it01'; task = 'A19'; domain = 'grid-scene'; version = 'grid-v01'; parent_version = $null
  type = 'baseline'
  image = 'tmp/run-20261002-220723-mimo/A19/grid-v01.png'
  image_bytes = Bytes "$TmpDir\grid-v01.png"; image_sha256_prefix = Sha16 "$TmpDir\grid-v01.png"
  render_request_id = 'A19-grid-v01'; render_http_status = 200; render_duration_ms = 2440.9
  render_ended_utc = '2026-10-04T15:20:58.906Z'
  viewed_at = $null
  viewed_at_basis = 'reconstructed window: >= 2026-10-04T15:20:58.906Z (render end) and < 2026-10-04T15:32:18.552Z (next render start); exact clock not captured'
  view_method = 'delegated general subagent image reading'
  observable_problems = 'ID labels are drawn at fontSize 14, cap height only about 10-11 px on a 1600x1600 canvas: legible but marginal for a diagnostic sheet. Everything else already correct.'
  change = 'none (baseline generate -> render -> view)'
  comparison_result = 'Self-check problems=0: 8x8=64 cells, exactly one subject per cell, colours 16/16/16/16, shapes 16/16/16/16, sizes 21/21/22, every row 4 distinct colours and 4 distinct shapes, ring hole = background and about 0.52x outer diameter, all labels outside their subjects with >= 27 px clearance, no clipping or overlap, divider lines continuous.'
  status = 'complete'
})

# ------------------------------------------------------------------ it02 visual --
$rows.Add([pscustomobject]@{
  id = 'A19-it02'; task = 'A19'; domain = 'grid-scene'; version = 'grid-v02'; parent_version = 'grid-v01'
  type = 'visual'
  image = 'tmp/run-20261002-220723-mimo/A19/grid-v02.png'
  image_bytes = Bytes "$TmpDir\grid-v02.png"; image_sha256_prefix = Sha16 "$TmpDir\grid-v02.png"
  render_request_id = 'A19-grid-v02'; render_http_status = 200; render_duration_ms = 5468.4
  render_ended_utc = '2026-10-04T15:32:24.029Z'
  viewed_at = $null
  viewed_at_basis = 'reconstructed window: >= 2026-10-04T15:41:56.241Z (the occlusion render it was inspected alongside) and < 2026-10-04T16:22:42.363Z (next render start); exact clock not captured'
  view_method = 'delegated general subagent image reading'
  observable_problems = 'none found on re-view; label legibility improved, geometry unchanged.'
  change = 'ID label fontSize 14 -> 16 and label box 56x20 -> 64x24 in gen-grid.ps1; label-overlap and clearance thresholds updated to match.'
  comparison_result = 'Measured ink box for every one of the 64 labels is 22x12 px, cap height about 12 px (16 px font), clearly readable at 100 percent; smallest label-to-shape clearance 39.8 px; counts still 16/16/16/16 by colour and shape, sizes 21/21/22, every row 4 distinct colours and 4 distinct shapes. No regression.'
  status = 'complete'
})

# ------------------------------------------------------------------ it03 visual --
$rows.Add([pscustomobject]@{
  id = 'A19-it03'; task = 'A19'; domain = 'grid-scene'; version = 'grid-v03'; parent_version = 'grid-v02'
  type = 'visual'
  image = 'tmp/run-20261002-220723-mimo/A19/grid-v03.png'
  image_bytes = Bytes "$TmpDir\grid-v03.png"; image_sha256_prefix = Sha16 "$TmpDir\grid-v03.png"
  render_request_id = 'A19-grid-v03'; render_http_status = 200; render_duration_ms = 5414.7
  render_ended_utc = '2026-10-04T16:22:47.785Z'
  viewed_at = $null
  viewed_at_basis = 'reconstructed window: >= 2026-10-04T16:22:47.785Z (render end) and < the next session turn; exact clock not captured'
  view_method = 'local image read (direct file open)'
  observable_problems = 'In v02 colour and shape were locked into period-4 pairs inside every row (blue <-> rounded-square, green <-> square, purple <-> ring, orange <-> circle, with the pairing rotated per row). Visible on the render as regular diagonal banding and confirmed by the colour x shape matrix, so it was not a real cross-distribution of the three attribute families.'
  change = 'Replaced the shared period-4 column construction in gen-grid.ps1 with two INDEPENDENT 64-cell shuffles (a colour bag of 16 each and a shape bag of 16 each, seeded System.Random Fisher-Yates) plus a rejection test: every row must hold >= 3 distinct colours AND >= 3 distinct shapes, and the colour x shape matrix must cover all 16 combinations. Size bag remains an independent shuffle. Added assignment diagnostics (attempt counts and the full matrix) to scene-data.json.'
  comparison_result = 'Self-check problems=0. Colour x shape matrix blue[5/4/5/2] orange[3/6/2/5] green[5/2/4/5] purple[3/4/5/4] - all 16 combinations non-zero, smallest cell 2, largest 6. Counts still 16/16/16/16 by colour and by shape, sizes 21/21/22, minimum 3 distinct colours and 3 distinct shapes per row, labels still outside every subject, no clipping or overlap. Regionally mixed rather than striped.'
  status = 'complete'
})

# --------------------------------------------------------------- it04 syntax-fix --
$rows.Add([pscustomobject]@{
  id = 'A19-it04'; task = 'A19'; domain = 'occlusion'; version = 'occ-a-v01 + occ-b-v01'; parent_version = $null
  type = 'syntax-fix'
  image = $null
  image_bytes = $null; image_sha256_prefix = $null
  render_request_id = 'A19-occA-v01 + A19-occB-v01'; render_http_status = 400; render_duration_ms = 1890.1
  render_ended_utc = '2026-10-04T15:39:25.680Z'
  viewed_at = $null
  viewed_at_basis = 'no image was produced, so nothing was viewed'
  view_method = 'none'
  observable_problems = 'Both requests returned 400 PARSE_ERROR: Unexpected character ''1'' in input state [AFTER_ATTR_VALUE_QUOTED] at position 1208 near: olor="      <Positioned left="150" top="85" width="400" height="480">.'
  change = 'Two real defects found by reading the generated DSL rather than guessing. (1) Case-insensitive PowerShell variables: the colour constant $PANEL and the List variable $panel were the SAME variable, so the list accumulated so far was concatenated into a color=\"...\" attribute and produced unterminated XML. Renamed the list to $panelList. (2) Midpoint arithmetic: (($PX0+$PW)/2) and (($BAR_Y+$BAR_H)/2) evaluated to (a+b)/2 instead of a+b/2, putting the opaque panel at (350,325) instead of (500,410) and the blue bar at y 200..256 instead of y 400..456. Corrected to $PX0+$PW/2, $PY0+$PH/2 and $BAR_Y+$BAR_H/2. Also switched the DSL comparison report to a prefix/suffix diff, because the two hidden blocks differ in length and a plain line-by-line diff is meaningless.'
  comparison_result = 'Regenerated as occ-a-v02 / occ-b-v02: shared prefix identical (7 lines up to the hidden marker), shared suffix identical (68 lines covering panel + visible objects + text), hidden block differs (9 vs 15 lines) as intended. Both then rendered 200.'
  status = 'complete'
})

# ------------------------------------------------------------------ it05 visual --
$rows.Add([pscustomobject]@{
  id = 'A19-it05'; task = 'A19'; domain = 'occlusion'; version = 'occ-a-v02 + occ-b-v02'; parent_version = 'occ-a-v01 + occ-b-v01'
  type = 'visual'
  image = 'tmp/run-20261002-220723-mimo/A19/occ-a-v02.png'
  image_bytes = Bytes "$TmpDir\occ-a-v02.png"; image_sha256_prefix = Sha16 "$TmpDir\occ-a-v02.png"
  render_request_id = 'A19-occA-v02 + A19-occB-v02'; render_http_status = 200; render_duration_ms = 2878.9
  render_ended_utc = '2026-10-04T15:41:56.241Z'
  viewed_at = $null
  viewed_at_basis = 'reconstructed window: >= 2026-10-04T15:41:56.241Z (second render end) and < 2026-10-04T16:22:42.363Z; exact clock not captured. Both delivered finals were later reopened directly (measured during the delivery turn).'
  view_method = 'delegated general subagent image reading, then local image read of both delivered PNGs'
  observable_problems = 'none found. Panel is fully opaque and carries only its own two lines of text; V01..V06 each labelled outside the shape; the blue bar abuts the panel left edge with its visible stub and the label 可见部分 sits under the stub; bottom caption is inside the canvas; no dashed outline, ghost, shadow or faint hint of anything hidden.'
  change = 'Fixed by it04; rendered both variants and proved equivalence rather than assuming it.'
  comparison_result = 'Pixel proof over the delivered bytes: 800x800 = 640,000 pixels compared via GDI+ LockBits, differing pixels = 0, differing bytes = 0, identical SHA-256 12FE65E604ABDFE3..., byte streams identical. DSL side: shared prefix and suffix byte-identical, hidden block differs (A hides a bar ending at x=560 plus a green circle and a purple square; B hides a bar ending at x=430 plus an orange ring, a blue circle and a green square). VERDICT EQUIVALENT, written to equivalence.json. Both finals reopened and visually confirmed identical.'
  status = 'complete'
})

# ------------------------------------------------- it06 syntax-fix (non-image) ---
$rows.Add([pscustomobject]@{
  id = 'A19-it06'; task = 'A19'; domain = 'question-generation'; version = 'questions-v01 -> questions-v03'; parent_version = $null
  type = 'syntax-fix'
  image = $null
  image_bytes = $null; image_sha256_prefix = $null
  render_request_id = $null; render_http_status = $null; render_duration_ms = $null
  render_ended_utc = $null
  viewed_at = $null
  viewed_at_basis = 'non-image tool iteration: no render and no picture, recorded for completeness but NOT counted as a visual iteration'
  view_method = 'none'
  observable_problems = 'Three defects, found by running the generators and the audit rather than by inspection. (1) mk-questions.ps1 would not parse: Missing closing } in statement block, reported at the Q12 method expression - the ForEach-Object script block had no closing brace. (2) Three tolerance arguments were bare concatenations (string + $x + string) in command-argument position, which PowerShell parses as separate arguments rather than as one expression. (3) The first audit run reported 8 questions without an explicit comparison standard, and itself mis-reported the numbering block because check-a19.ps1 assigned $Q = @($q.questions) and $A = @($a.answers) - PowerShell variables are case-insensitive, so $q/$Q and $a/$A were the same variable and assigning the arrays destroyed the parsed documents.'
  change = 'Closed the missing brace; parenthesized the Q05, Q12 and Q14 tolerance expressions and replaced the Q14 concatenation with a single literal; added the 编号>=18 numbering block; added an explicit 比较标准 clause to Q01, Q07, Q08, Q09, Q10, Q11, Q13 and Q14 (each written for that question, not a boilerplate repeat); renamed the audit document variables to $QDoc/$ADoc.'
  comparison_result = 'Regenerated to questions-v03.json / answers-v03.json with problems=0. Answers are identical across all three generations (Q01..Q14 unchanged), confirming the fixes changed form and not content. Re-running the audit took problems from 5 to 0.'
  status = 'complete'
})

$sb = New-Object System.Text.StringBuilder
foreach ($r in $rows) {
  [void]$sb.AppendLine((($r | ConvertTo-Json -Depth 6) -replace "`r`n", ' ' -replace "`n", ' '))
}
[IO.File]::WriteAllText($OutJsonl, $sb.ToString(), $utf8)

Write-Output ("rows = {0}" -f $rows.Count)
$types = $rows | Group-Object type | ForEach-Object { "$($_.Name)=$($_.Count)" }
Write-Output ("types: " + ($types -join ' '))
Write-Output ("image iterations (viewed) = " + @($rows | Where-Object { $_.image -ne $null }).Count)
Write-Output ("-> {0}" -f $OutJsonl)
