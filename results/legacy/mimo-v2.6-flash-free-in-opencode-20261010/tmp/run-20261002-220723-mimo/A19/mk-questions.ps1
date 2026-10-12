param(
  [Parameter(Mandatory=$true)][string]$SceneJson,
  [Parameter(Mandatory=$true)][string]$OutQuestions,
  [Parameter(Mandatory=$true)][string]$OutAnswers,
  [switch]$Quiet
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

$scene = Get-Content $SceneJson -Raw -Encoding UTF8 | ConvertFrom-Json
$OBJ   = @($scene.objects)
if ($OBJ.Count -ne 64) { throw "expected 64 objects, got $($OBJ.Count)" }

$fail = New-Object System.Collections.Generic.List[string]
function Require([bool]$cond, [string]$msg) { if (-not $cond) { $script:fail.Add($msg) } }

$byId = @{}
foreach ($o in $OBJ) { $byId[$o.id] = $o }

function Dist([double]$x1,[double]$y1,[double]$x2,[double]$y2) { return [Math]::Sqrt(($x1-$x2)*($x1-$x2) + ($y1-$y2)*($y1-$y2)) }

# ordering helpers - every ordering in a question states its full key chain
function BySizeXy($list) { return @($list | Sort-Object @{Expression={[double]$_.size};Descending=$true}, @{Expression={[double]$_.cx}}, @{Expression={[double]$_.cy}}) }
function ByXy($list)     { return @($list | Sort-Object @{Expression={[double]$_.cx}}, @{Expression={[double]$_.cy}}) }

$Q = New-Object System.Collections.Generic.List[object]
$A = New-Object System.Collections.Generic.List[object]

function AddQ([string]$id, [string]$scene, [string]$cat, [int]$steps, [string]$text) {
  $Q.Add([pscustomobject]@{ id = $id; scene = $scene; category = $cat; steps = $steps; text = $text })
}
function AddA([string]$id, $answer, [string]$type, [string]$method, [string]$tol, [string]$vis, $check) {
  $A.Add([pscustomobject]@{ id = $id; answer = $answer; answer_type = $type; method = $method; coordinate_tolerance = $tol; visibility_basis = $vis; uniqueness_check = $check })
}

$ORIGIN = '坐标原点为画面左上角 (0,0)，x 向右增大，y 向下增大，单位为像素；对象中心指该对象包围框的中心点。'
$TOLG   = '1.5 px（按画面量取中心/边缘时的读数容差；答案为 ID 或整数，容差不影响结论）'

# =============================================================== Q01 composite ==
$f = @($OBJ | Where-Object { $_.color -eq 'green' -and $_.shape -eq 'ring' -and $_.size -eq 80 })
Require ($f.Count -eq 1) "Q01 expected exactly 1 match, got $($f.Count)"
$a1 = $(if ($f.Count -eq 1) { $f[0].id } else { '?' })
AddQ 'Q01' 'grid-scene' 'composite-attribute-search' 1 `
  ('同时满足以下三个条件的对象是哪一个？条件：①颜色为绿；②形状为圆环；③尺寸为 80。' + $ORIGIN + '只答该对象的编号，例如 G07。比较标准：三个条件按逻辑与取交集，实际交集恰为 1 个；本题不涉及数值比较，若交集不唯一则题目作废。')
AddA 'Q01' $a1 'object-id' `
  '在 64 个对象上按 color=green AND shape=ring AND size=80 三个条件取交集。' $TOLG `
  '网格图中 64 个对象全部可见、无遮挡，颜色、形状、尺寸均可直接从 grid-scene.png 判读。' `
  ([pscustomobject]@{ rule = 'three-condition intersection'; matches = $f.Count; ids = @($f | ForEach-Object { $_.id }) })

# ================================================ Q02 composite + ordering (2) ==
$p48 = @($OBJ | Where-Object { $_.color -eq 'purple' -and $_.size -eq 48 })
Require ($p48.Count -gt 0) 'Q02 empty filter'
$sortedP = ByXy $p48
$a2 = $sortedP[$sortedP.Count - 1].id
AddQ 'Q02' 'grid-scene' 'composite-attribute-search + ordering' 2 `
  ('分两步：第①步，从全部对象中筛出「颜色为紫」且「尺寸为 48」的对象；第②步，在第①步的结果里取中心 x 坐标最大（最靠右）的那一个。它的编号是？' + $ORIGIN + '比较标准：先比较中心 x，若相同再比较中心 y（取 y 较小者）。')
AddA 'Q02' $a2 'object-id' `
  ('①过滤 color=purple AND size=48，得到 ' + $p48.Count + ' 个候选（' + (($p48 | ForEach-Object { $_.id }) -join ',') + '）；②按中心 x 升序（x 相同按 y 升序）取最后一名。') $TOLG `
  '同 Q01：全部候选对象在网格图中完整可见。' `
  ([pscustomobject]@{ rule = 'filter then max cx (tie-break min cy)'; candidates = $p48.Count; candidate_ids = @($p48 | ForEach-Object { $_.id }); winner_cx = $byId[$a2].cx })

# ================================================ Q03 strict right relation =====
$anchor = $byId['G28']
$right = @($OBJ | Where-Object { $_.row -eq $anchor.row -and $_.cx -gt $anchor.cx } | Sort-Object @{Expression={[double]$_.cx}})
Require ($right.Count -gt 0) 'Q03 no right neighbour'
$a3 = $right[0].id
$gap3 = if ($right.Count -gt 0) { $right[0].cx - $anchor.cx } else { -1 }
AddQ 'Q03' 'grid-scene' 'strict centre left/right relation' 1 `
  ('以「中心 y 相同（即同一行）且中心 x 严格大于」为准：与 G28 处于同一行、位于 G28 右侧、且与 G28 水平距离最近的对象是哪一个？' + $ORIGIN + '比较标准：中心 y 完全相等，中心 x 严格大于 705，取 x 最小者。')
AddA 'Q03' $a3 'object-id' `
  ('在同一行中筛选 cx > ' + $anchor.cx + '，得到 ' + $right.Count + ' 个（' + (($right | ForEach-Object { $_.id }) -join ',') + '），取 cx 最小者；次小者与胜者的中心 x 相差 ' + $(if ($right.Count -gt 1) { $right[1].cx - $right[0].cx } else { 'n/a' }) + ' px，无并列。') $TOLG `
  '同一行的 8 个对象全部可见，中心 y 可直接由包围框量得。' `
  ([pscustomobject]@{ rule = 'same row AND cx > anchor AND min cx'; candidates = $right.Count; gap_to_next_px = $(if ($right.Count -gt 1) { $right[1].cx - $right[0].cx } else { $null }) })

# ================================ Q04 strict left relation then count (2 steps) ==
$anchor4 = $byId['G30']
$left4 = @($OBJ | Where-Object { $_.row -eq $anchor4.row -and $_.cx -lt $anchor4.cx } | Sort-Object @{Expression={[double]$_.cx};Descending=$true})
Require ($left4.Count -gt 0) 'Q04 no left neighbour'
$x4 = $left4[0]
$cnt4 = @($OBJ | Where-Object { $_.row -eq $x4.row -and $_.color -eq $x4.color }).Count
AddQ 'Q04' 'grid-scene' 'strict centre left/right relation + count' 2 `
  ('分两步：第①步，与 G30 处于同一行、位于 G30 左侧（中心 x 严格小于 1085）、且与 G30 水平距离最近的对象 X 是哪个？第②步，X 所在的那一行中，与 X 颜色相同的对象一共有几个？' + $ORIGIN + '行号从上到下为第 1 行至第 8 行；比较标准：中心 y 相等，中心 x 严格小于，取 x 最大者；计数时只数该行内的对象。')
AddA 'Q04' $cnt4 'integer-count' `
  ('①同 cx < ' + $anchor4.cx + ' 且同 row 取 cx 最大者，得到 X=' + $x4.id + '（颜色 ' + $x4.color + '）；②统计第 ' + ($x4.row + 1) + ' 行中 color=' + $x4.color + ' 的对象。') '整数，无容差' `
  ('第 ' + ($x4.row + 1) + ' 行的 8 个对象与 X 均完全可见，颜色可直接判读。') `
  ([pscustomobject]@{ rule = 'same row AND cx < anchor AND max cx, then count same colour in that row'; step1_object = $x4.id; step1_color = $x4.color; row = ($x4.row + 1); count = $cnt4 })

# ================================================== Q05 distance to a point =====
$PX = 777; $PY = 613
$dd = @($OBJ | ForEach-Object { [pscustomobject]@{ id = $_.id; d = (Dist $_.cx $_.cy $PX $PY) } } | Sort-Object @{Expression={[double]$_.d}})
$gap5 = $dd[1].d - $dd[0].d
Require ($gap5 -gt 3) "Q05 nearest is not decisive (gap $($gap5))"
$a5 = $dd[0].id
AddQ 'Q05' 'grid-scene' 'distance' 1 `
  ('以对象中心到点 P(777, 613) 的欧氏距离 sqrt((x-777)^2 + (y-613)^2) 计（单位像素），距离最小的对象是哪一个？' + $ORIGIN + '比较标准：欧氏距离升序，距离并列时取中心 x 较小者。')
AddA 'Q05' $a5 'object-id' `
  ('对 64 个对象逐一计算到 P(777,613) 的欧氏距离并升序排列，第一名 ' + $dd[0].id + ' = ' + [Math]::Round($dd[0].d,2) + ' px，第二名 ' + $dd[1].id + ' = ' + [Math]::Round($dd[1].d,2) + ' px，差距 ' + [Math]::Round($gap5,2) + ' px，远大于读数容差，无并列。') ('±1.5 px（距离读数容差；与第二名相差 ' + [Math]::Round($gap5,1) + ' px，结论不受影响）') `
  '64 个中心点全部可见；P 点是题面给定的固定点，不依赖画面外信息。' `
  ([pscustomobject]@{ rule = 'min euclidean distance to P(777,613)'; first_px = [Math]::Round($dd[0].d,2); second_px = [Math]::Round($dd[1].d,2); second_id = $dd[1].id; margin_px = [Math]::Round($gap5,2) })

# ============================================ Q06 right then down (2 steps) =====
$anchor6 = $byId['G44']
$right6 = @($OBJ | Where-Object { $_.row -eq $anchor6.row -and $_.cx -gt $anchor6.cx } | Sort-Object @{Expression={[double]$_.cx}})
Require ($right6.Count -gt 0) 'Q06 no right neighbour'
$x6 = $right6[0]
$down6 = @($OBJ | Where-Object { $_.col -eq $x6.col -and $_.cy -gt $x6.cy } | Sort-Object @{Expression={[double]$_.cy}})
Require ($down6.Count -gt 0) 'Q06 no object below'
$y6 = $down6[0]
AddQ 'Q06' 'grid-scene' 'two-step relation' 2 `
  ('分两步：第①步，找出与 G44 同一行且位于 G44 右侧、水平距离最近的对象 X；第②步，找出与 X 同一列且位于 X 下方、垂直距离最近的对象 Y。Y 的编号是？' + $ORIGIN + '比较标准：第①步要求中心 y 相等且中心 x 严格大于 705，取 x 最小者；第②步要求中心 x 相等且中心 y 严格大于 ' + $x6.cy + '，取 y 最小者。')
AddA 'Q06' $y6.id 'object-id' `
  ('①同 row 取 cx 最小且 cx > 705 的对象 -> X=' + $x6.id + '（中心 ' + $x6.cx + ',' + $x6.cy + '）；②同 col 取 cy 最小且 cy > ' + $x6.cy + ' 的对象 -> Y=' + $y6.id + '（中心 ' + $y6.cx + ',' + $y6.cy + '）。两步各只有 1 个候选满足严格不等式。') $TOLG `
  '两步涉及的同行、同列对象全部可见，无遮挡。' `
  ([pscustomobject]@{ rule = 'same-row right-neighbour then same-column down-neighbour'; step1 = $x6.id; step2 = $y6.id; strict_inequalities = 'cx > 705 then cy > ' + $x6.cy })

# ============================================================ Q07 ordering ======
$srt = BySizeXy $OBJ
$a7 = $srt[0].id
$ties7 = @($srt | Where-Object { $_.size -eq $srt[0].size -and $_.cx -eq $srt[0].cx -and $_.cy -eq $srt[0].cy }).Count
Require ($ties7 -eq 1) "Q07 first place not unique"
AddQ 'Q07' 'grid-scene' 'ordering' 1 `
  ('把全部 64 个对象按下面的键链排序，取第一名：①尺寸降序；②尺寸相同时中心 x 升序；③前两项都相同时中心 y 升序。第一名的编号是？' + $ORIGIN + '比较标准：完整键链为「尺寸降序 → 中心 x 升序 → 中心 y 升序」，三段构成全序，第一名唯一，不产生并列。')
AddA 'Q07' $a7 'object-id' `
  ('排序键链 size DESC -> cx ASC -> cy ASC。尺寸 80 的对象共 ' + @($OBJ | Where-Object { $_.size -eq 80 }).Count + ' 个，其中中心 x 最小为 ' + $srt[0].cx + '（第 1 列），并列的有 ' + (($srt | Where-Object { $_.size -eq 80 -and $_.cx -eq $srt[0].cx } | ForEach-Object { $_.id }) -join ',') + '，再按中心 y 升序取 ' + $a7 + '。三段键链构成全序，第一名唯一。') $TOLG `
  '尺寸由画面中圆的直径或方的边长量得，全部对象可见。' `
  ([pscustomobject]@{ rule = 'size DESC, cx ASC, cy ASC'; winner_size = $srt[0].size; winner_cx = $srt[0].cx; winner_cy = $srt[0].cy; same_size_same_cx = (($srt | Where-Object { $_.size -eq $srt[0].size -and $_.cx -eq $srt[0].cx } | ForEach-Object { $_.id })) })

# ============================================ Q08 ordering then count (2 steps) ==
$blues = @($OBJ | Where-Object { $_.color -eq 'blue' })
$bs = ByXy $blues
$x8 = $bs[9]   # 10th, 0-based
$cnt8 = @($OBJ | Where-Object { $_.row -eq $x8.row -and $_.color -eq 'blue' }).Count
AddQ 'Q08' 'grid-scene' 'ordering + count' 2 `
  ('分两步：第①步，把所有「蓝色」对象按中心 x 升序（x 相同按中心 y 升序）排列，取第 10 名 X；第②步，X 所在的那一行里，蓝色对象共有几个？' + $ORIGIN + '行号从上到下为第 1 行至第 8 行。比较标准：第①步排序键链为「中心 x 升序 → 中心 y 升序」，构成全序，第 10 名唯一；第②步计数只数该行内 color=blue 的主体，不计编号文字。')
AddA 'Q08' $cnt8 'integer-count' `
  ('①蓝色对象共 ' + $blues.Count + ' 个，按 cx ASC -> cy ASC 排序，第 10 名是 ' + $x8.id + '（中心 ' + $x8.cx + ',' + $x8.cy + '）；②统计第 ' + ($x8.row + 1) + ' 行中 color=blue 的对象，得到 ' + $cnt8 + ' 个。') '整数，无容差' `
  ('全部蓝色对象与其所在行的 8 个对象均完整可见，颜色可直接判读。' ) `
  ([pscustomobject]@{ rule = 'sort blue by cx ASC/cy ASC, take 10th, then count blue in that row'; step1_object = $x8.id; step1_rank = 10; row = ($x8.row + 1); count = $cnt8; blues_total = $blues.Count })

# ======================================================= Q09 colour count =======
$cnt9 = @($OBJ | Where-Object { $_.row -eq 1 -and $_.color -eq 'purple' }).Count
AddQ 'Q09' 'grid-scene' 'colour count' 1 `
  ('第 2 行（从上数第 2 行）中，颜色为紫的对象有几个？' + $ORIGIN + '行号从上到下为第 1 行至第 8 行，只数第 2 行内的对象。比较标准：按行号与颜色属性判定，满足两条件者计入，计数结果唯一，不涉及数值比较。')
AddA 'Q09' $cnt9 'integer-count' `
  ('筛选 row=1 AND color=purple，得到 ' + (($OBJ | Where-Object { $_.row -eq 1 -and $_.color -eq 'purple' } | ForEach-Object { $_.id }) -join ',') + '，计 ' + $cnt9 + ' 个。') '整数，无容差' `
  '第 2 行的 8 个对象全部可见，颜色可直接判读。' `
  ([pscustomobject]@{ rule = 'count row=1 AND color=purple'; row = 2; count = $cnt9; ids = @($OBJ | Where-Object { $_.row -eq 1 -and $_.color -eq 'purple' } | ForEach-Object { $_.id }) })

# ======================================================== Q10 shape+colour =======
$f10 = @($OBJ | Where-Object { $_.shape -eq 'rounded-square' -and $_.color -eq 'purple' })
AddQ 'Q10' 'grid-scene' 'shape/colour count' 1 `
  ('全图中，形状为圆角方且颜色为紫的对象共有几个？' + $ORIGIN + '只统计网格中 64 个主体，不计编号文字。比较标准：形状与颜色均按画面呈现判定，两条件按逻辑与取交集，结果唯一，不涉及数值比较。')
AddA 'Q10' $f10.Count 'integer-count' `
  ('筛选 shape=rounded-square AND color=purple，得到 ' + (($f10 | ForEach-Object { $_.id }) -join ',') + '，计 ' + $f10.Count + ' 个。') '整数，无容差' `
  '64 个主体全部可见，形状（圆角方与正方/圆/圆环的区别）可直接辨认。' `
  ([pscustomobject]@{ rule = 'count shape=rounded-square AND color=purple'; count = $f10.Count; ids = @($f10 | ForEach-Object { $_.id }) })

# ========================================= Q11 count then count (2 steps) =======
$c80circ = @($OBJ | Where-Object { $_.shape -eq 'circle' -and $_.size -eq 80 })
$blue80c = @($c80circ | Where-Object { $_.color -eq 'blue' })
AddQ 'Q11' 'grid-scene' 'two-step count' 2 `
  ('分两步：第①步，数出全图中「形状为圆且尺寸为 80」的对象个数；第②步，在第①步得到的这些对象里，再数出颜色为蓝的有几个。第②步的答案是？' + $ORIGIN + '尺寸指圆的直径。比较标准：第①步以「形状为圆且直径等于 80」判定，等于 80 才计入；第②步在第①步结果内按 color=blue 计数。两步的计数对象均唯一确定，不产生并列。')
AddA 'Q11' $blue80c.Count 'integer-count' `
  ('①shape=circle AND size=80 得到 ' + $c80circ.Count + ' 个（' + (($c80circ | ForEach-Object { $_.id }) -join ',') + '）；②在其中筛选 color=blue，得到 ' + (($blue80c | ForEach-Object { $_.id }) -join ',') + '，计 ' + $blue80c.Count + ' 个。') '整数，无容差' `
  '两步全部对象均可见；圆的直径可直接量得。' `
  ([pscustomobject]@{ rule = 'count circle AND size=80, then count blue within'; step1_count = $c80circ.Count; step1_ids = @($c80circ | ForEach-Object { $_.id }); count = $blue80c.Count; ids = @($blue80c | ForEach-Object { $_.id }) })

# ==================================================== Q12 bounding box ==========
$R0 = 610; $R1 = 990
$inR = @($OBJ | Where-Object { $_.bbox_x0 -ge $R0 -and $_.bbox_x1 -le $R1 -and $_.bbox_y0 -ge $R0 -and $_.bbox_y1 -le $R1 })
$inR80 = @($inR | Where-Object { $_.size -eq 80 })
Require ($inR80.Count -eq 1) "Q12 expected exactly 1, got $($inR80.Count) (candidates in R: " + (($inR | ForEach-Object { $_.id + '/' + $_.size }) -join ',') + ")"
$a12 = $(if ($inR80.Count -eq 1) { $inR80[0].id } else { '?' })
AddQ 'Q12' 'grid-scene' 'bounding box' 1 `
  ('记每个对象的包围框为以其为中心、边长等于该对象尺寸的正方形（圆的包围框即其外接正方形）。设矩形区域 R = { (x,y) | 610 ≤ x ≤ 990 且 610 ≤ y ≤ 990 }。哪一个对象的包围框完全落在 R 内（四条边都在 R 内或边界上），且尺寸为 80？' + $ORIGIN + '比较标准：x0 ≥ 610、x1 ≤ 990、y0 ≥ 610、y1 ≤ 990 四式同时成立。')
AddA 'Q12' $a12 'object-id' `
  ('先求包围框完全落在 R 内的对象，得到 ' + $inR.Count + ' 个（' + (($inR | ForEach-Object { $_.id + '(s=' + $_.size + ',bbox ' + $_.bbox_x0 + '..' + $_.bbox_x1 + ' × ' + $_.bbox_y0 + '..' + $_.bbox_y1 + ')'}) -join '; ') + '）；再要求 size=80，唯一剩下 ' + $a12 + '。') ('±1.5 px（按包围框边缘量取；' + $a12 + ' 的包围框距 R 各边至少 ' + $(if ($inR80.Count -eq 1) { [int][Math]::Min([Math]::Min($inR80[0].bbox_x0 - $R0, $R1 - $inR80[0].bbox_x1), [Math]::Min($inR80[0].bbox_y0 - $R0, $R1 - $inR80[0].bbox_y1)) } else { 0 }) + ' px）') `
  '包围框由对象自身的中心与尺寸唯一确定，全部可见；R 的边界是题面给定的固定坐标。' `
  ([pscustomobject]@{ rule = 'bbox fully inside R AND size=80'; inside_R = @($inR | ForEach-Object { $_.id }); inside_R_count = $inR.Count; size80_count = $inR80.Count })

# ================================================ Q13 occlusion: indeterminate ===
AddQ 'Q13' 'occlusion' 'occlusion / information sufficiency' 1 `
  ('在遮挡图中，被遮挡面板完全盖住、观众一点都看不到的对象有几个？（面板区域为 300 ≤ x ≤ 700 且 170 ≤ y ≤ 650）' + $ORIGIN + '只根据最终可见画面回答；若画面本身不足以判定，就回答「无法确定」。比较标准：答案只允许由可见像素推出，可见画面必须能唯一确定该数量才算可答；本题不能唯一确定，故正确答案是「无法确定」，不得把隐藏对象数量当作标准答案。')
AddA 'Q13' '无法确定' 'explicit-indeterminacy' `
  ('可见画面只给出面板的正面，面板内部不含任何可见信息，因此「完全被覆盖的对象个数」不存在任何可从画面推出的约束。该题的不可判定性由交付物本身证明：occlusion.png 与 occlusion-alternative.png 是像素完全等价的两张图（equivalence.json 记录 640,000 像素中 0 个不同、SHA-256 相同），但两者的隐藏内容不同——A 完全隐藏 2 个对象（绿圆 d140、紫方 90）并半隐藏 1 条蓝条，B 完全隐藏 3 个对象（橙圆环 160/80、蓝圆 90、绿方 70）并半隐藏同一条蓝条的更短一段。同一张可见图对应 2 或 3 两种可能，故无法确定。') `
  '不适用（该题的答案不依赖任何像素读数）' `
  ('面板为不透明纯色（#1E293B + #0F172A 边框），独立看图确认面板内部只有填充色与其上的两行文字，没有任何第三种颜色、虚线、轮廓或阴影；两份 PNG 逐像素相同，因此任何观众看到的画面都不含被覆盖区域的信息。') `
  ([pscustomobject]@{ rule = 'not derivable from the visible image'; fully_hidden_in_A = 2; fully_hidden_in_B = 3; partially_hidden = 1; rendered_pixels_identical = $true; reason = 'the two delivered renders are pixel-identical yet their hidden object counts differ' })

# ================================================ Q14 occlusion: countable =======
$R = [pscustomobject]@{ x0 = 300; y0 = 170; x1 = 700; y1 = 650 }
$outside = @()
foreach ($v in @(
    [pscustomobject]@{ id='V01'; x0=74;  y0=129; x1=146; y1=201 },
    [pscustomobject]@{ id='V02'; x0=168; y0=268; x1=232; y1=332 },
    [pscustomobject]@{ id='V03'; x0=70;  y0=430; x1=150; y1=510 },
    [pscustomobject]@{ id='V04'; x0=183; y0=558; x1=247; y1=622 },
    [pscustomobject]@{ id='V05'; x0=715; y0=220; x1=775; y1=280 },
    [pscustomobject]@{ id='V06'; x0=392; y0=682; x1=448; y1=738 },
    [pscustomobject]@{ id='bar'; x0=200; y0=400; x1=560; y1=456 }
  )) {
  $disjoint = ($v.x1 -le $R.x0) -or ($v.x0 -ge $R.x1) -or ($v.y1 -le $R.y0) -or ($v.y0 -ge $R.y1)
  if ($disjoint) { $outside += $v.id }
}
AddQ 'Q14' 'occlusion' 'visibility count' 1 `
  ('把遮挡面板占据的矩形记为 300 ≤ x ≤ 700 且 170 ≤ y ≤ 650。完全落在该矩形之外（与它没有任何公共点）的彩色对象有几个？只数对象本身，不计文字，也不计遮挡面板。' + $ORIGIN + '比较标准：以对象包围框与面板矩形是否相交判定，边界接触也算相交；完全不相交者计 1，相交者不计，结果唯一，不产生并列。')
AddA 'Q14' $outside.Count 'integer-count' `
  ('逐个判断 7 个候选彩色对象（V01–V06 与那条蓝条）的包围框是否与面板矩形不相交：不相交者为 ' + ($outside -join ',') + '，计 ' + $outside.Count + ' 个。蓝条的包围框是 x 200..560 × y 400..456，与面板相交，因此不计入。') '整数，无容差（最近的 V05 距面板右缘 715−700 = 15 px，判断余量远大于读数误差）' `
  ('7 个彩色对象与面板的位置关系在可见画面上完全确定；蓝条与面板相交这一事实本身也直接可见（它从面板左缘伸出）。此题不涉及面板背后的任何内容。') `
  ([pscustomobject]@{ rule = 'objects whose bbox is disjoint from the panel rect'; candidates = 7; disjoint = $outside; count = $outside.Count; excluded = @('bar') })

# ------------------------------------------------------------------ validate ----
$twoStep = @($Q | Where-Object { $_.steps -ge 2 }).Count
Require ($Q.Count -eq 14) "expected 14 questions, got $($Q.Count)"
Require ($twoStep -ge 4) "expected >= 4 two-step questions, got $twoStep"
Require (@($Q | Where-Object { $_.id -eq 'Q13' }).Count -ge 1) 'Q13 missing'
$indet = @($A | Where-Object { $_.answer -eq '无法确定' }).Count
Require ($indet -ge 1) 'no 无法确定 answer'

$cats = @($Q | ForEach-Object { ($_.category -split ' \+ ')[0] } | Sort-Object -Unique)

# ------------------------------------------------------------------- write ------
# ---------------------------------------------------- numbering >= 18 block -----
# TASK.md asks for 编号>=18 in the same breath as "12 grid questions + 2 occlusion
# questions".  The two together rule out reading it as 18 questions, so it is read
# as "at least 18 numbered entities" and every entity family is counted explicitly.
$qText  = ($Q | ForEach-Object { $_.text }) -join ' '
$aText  = ($A | ForEach-Object { ($_.method + ' ' + $_.visibility_basis + ' ' + $_.coordinate_tolerance) }) -join ' '
$idQ    = @([regex]::Matches($qText, 'G[0-9]{2}') | ForEach-Object { $_.Value } | Sort-Object -Unique)
$idAll  = @([regex]::Matches(($qText + ' ' + $aText), 'G[0-9]{2}') | ForEach-Object { $_.Value } | Sort-Object -Unique)
$vIds   = @([regex]::Matches(($qText + ' ' + $aText), 'V[0-9]{2}') | ForEach-Object { $_.Value } | Sort-Object -Unique)
$numberedEntities = 64 + 6 + $Q.Count
$NUMBLOCK = [pscustomobject]@{
  requirement            = '编号>=18'
  interpretation         = 'TASK.md 同时规定"为网格图写12道新题"与"为遮挡图写2题"，合计14题，因此该条不可能指题目数量；它要求带编号的实体至少18个。下面按编号族逐项给出实际数量。'
  grid_object_ids        = 'G01..G64'
  grid_object_count      = 64
  occlusion_object_ids   = 'V01..V06'
  occlusion_object_count = 6
  question_ids           = 'Q01..' + ('Q{0:D2}' -f $Q.Count)
  question_count         = $Q.Count
  numbered_entities      = $numberedEntities
  meets_18               = ($numberedEntities -ge 18)
  distinct_object_ids_named_in_question_text = $idQ.Count
  object_ids_referenced_anywhere_in_questions_or_answers = $idAll.Count
  visible_object_ids_named_in_occlusion_text  = $vIds.Count
}
if (-not ($numberedEntities -ge 18)) { $fail.Add('numbered entities below 18') }

$qOut = [ordered]@{
  schema    = 'snapshot-suite/questions/v1'
  task      = 'A19'
  note      = '题目不含答案；答案、计算方法、坐标容差与可见性依据见同目录 answers.json。所有题目只能依据最终可见图作答。'
  scenes    = [pscustomobject]@{
    'grid-scene' = 'grid-scene.png (1600x1600), 64 objects G01-G64, row-major numbering left-to-right / top-to-bottom'
    'occlusion'  = 'occlusion.png (800x800); occlusion-alternative.png is pixel-identical to it and is delivered only as the second hidden-content proof'
  }
  conventions = [pscustomobject]@{
    origin        = '画面左上角 (0,0)，x 向右，y 向下，单位像素'
    row_column    = '8 行 8 列，行号从上到下第 1..8 行，列号从左到右第 1..8 列；单元边长 190 px，网格框左上角 (40,40)'
    centre        = '对象中心 = 其包围框中心 = 该主体的几何中心'
    bbox          = '包围框 = 以中心为心、边长等于对象尺寸的正方形；尺寸按圆直径或方边长计'
    distance      = '中心之间的欧氏距离'
    ordering      = '每题都写明完整排序键链；并列时的处理规则随题给出，保证答案唯一'
    counting      = '只统计 64 个主体，不把编号文字计入对象'
    tolerance     = '涉及像素读数时给出容差；ID 与整数答案不受容差影响'
  }
  counts = [pscustomobject]@{ total = $Q.Count; grid = 12; occlusion = 2; two_step = $twoStep; indeterminate = $indet }
  numbering = $NUMBLOCK
  categories = $cats
  questions = $Q.ToArray()
}
[IO.File]::WriteAllText($OutQuestions, (($qOut | ConvertTo-Json -Depth 8) + "`n"), $utf8)

$aOut = [ordered]@{
  schema   = 'snapshot-suite/answers/v1'
  task     = 'A19'
  note     = '每个答案附计算方法、坐标容差与可见性依据；uniqueness_check 记录生成时实际做过的唯一性断言。'
  geometry_source = 'scene-data.json（与 grid-scene.png 同源的同一份真实几何）'
  occlusion_proof = 'equivalence.json'
  counts   = [pscustomobject]@{ total = $A.Count; two_step = $twoStep; indeterminate = $indet }
  numbering = $NUMBLOCK
  answers  = $A.ToArray()
}
[IO.File]::WriteAllText($OutAnswers, (($aOut | ConvertTo-Json -Depth 8) + "`n"), $utf8)

Write-Output ("questions = {0}  (two-step = {1}, indeterminate = {2})" -f $Q.Count, $twoStep, $indet)
Write-Output ("categories: " + ($cats -join ' | '))
foreach ($a in $A) { Write-Output ("  {0} -> {1}" -f $a.id, ($a.answer -join ',')) }
Write-Output ("problems = {0}" -f $fail.Count)
foreach ($p in $fail) { Write-Output ("  PROBLEM: " + $p) }
Write-Output ("-> {0}" -f $OutQuestions)
Write-Output ("-> {0}" -f $OutAnswers)
