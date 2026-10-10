# Patch portfolio.json (B01) for the case-08 post-closure ring correction.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$p = Join-Path $root 'outputs\run-20261002-220723-mimo\B01\portfolio.json'
$utf8 = New-Object System.Text.UTF8Encoding($false)

$o = Get-Content $p -Raw -Encoding UTF8 | ConvertFrom-Json

$c = $o.cases | Where-Object { $_.id -eq 'case-08' }
if (-not $c) { throw 'case-08 not found' }

$c.visual_intent = '奶油暖色 + 锥形进度环：确定性 DialArc 分段环（100 个 Rotate+C 分段，先铺暗弧再覆盖亮弧）把「4 针中的 3 针」画成自 12 点起顺时针的精确 75% 弧，内圆叠色做甜甜圈镂空，环内留白放「3/4」大字。右侧两张接种卡用淡橙/淡蓝区分疫苗种类，底部 2x2 注意事项用编号方块建立秩序。'

$c.dsl_capabilities = @(
    'Container/Stack/Positioned 栅格',
    'DialArc：Rotate 变换矩阵 + C 矩形分段的确定性进度环（OFF 先铺、ON 后覆盖）',
    'shape=CIRCLE 内圆叠色做甜甜圈镂空',
    'LINEAR 渐变条',
    'borderRadius 卡片 + boxShadow',
    '多级 Text + bold + 居中/右对齐'
)

$c.visual_review = '读图工具实际查看 final.png：r2（B01-c08-r2）逐条核对 4 条完成标准全部通过，橙色亮弧自 12 点起顺时针到 9 点方向即止，缺口落在 9 点→12 点的左上象限，System.Drawing 沿圆周逐 0.5° 复测 542/720 = 75.28%、起点样本 716（= 358°）。另用归档的 v1 DSL 重建渲染 B01-c08-r1b 并打开查看，可见亮弧只覆盖 3 点→6 点→9 点的下半圈（实测 50.14%、自 90° 起），直观复现了首版缺陷。首版 r1 当时记为「首版即合格」的判定已由 ite-B01-c08-v2-visual 撤回。'

$c.request_ids = @('B01-c08-r1', 'B01-c08-r2', 'B01-c08-r1b')
$c.iteration_ids = @('ite-B01-c08-v1-baseline-erroneous-verdict', 'ite-B01-c08-v2-visual', 'ite-B01-c08-v1evidence-reconstruction')
$c.dsl_versions = 2
$c.render_count = 3
$c.unresolved_issues = @()

# extend final_collection_review with the correction
$review = [string]$o.final_collection_review
if ($review -notmatch '关闭后修正') {
    $o.final_collection_review = $review + ' 【关闭后修正 2026-10-06】跨任务环形量测发现 case-08 的进度环并非声明的 75%：实测 50.14%、自 90° 起，根因是真实服务的 SWEEP 渐变不遵循 gradientStops 与 gradientStartAngle（同现象在 B02 case-01 以 f=0.62 复现）。已改用确定性 DialArc 重画并重渲染为 B01-c08-r2，复测 75.28% 自 12 点起，同时以归档 v1 DSL 重建渲染 B01-c08-r1b 保存被取代版本的图像证据。重新生成后 case-06/07/09/10 的 final.snapshot 哈希与修正前完全一致，其余 9 件未受影响。'
}

# extend unresolved_issues only if it lists nothing about this
$ui = @($o.unresolved_issues)
if (-not ($ui -match 'SWEEP')) {
    $ui += '已知服务行为（非本作品遗留缺陷）：真实服务的 SWEEP 渐变不遵循 gradientStops 与 gradientStartAngle，任何需要精确弧度比例的进度环必须用分段构造（lib-b01.ps1 / lib-b02.ps1 的 DialArc）。B01 case-08 已按此修正。'
    $o.unresolved_issues = $ui
}

$json = $o | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($p, $json, $utf8)

$chk = Get-Content $p -Raw -Encoding UTF8 | ConvertFrom-Json
$c2 = $chk.cases | Where-Object { $_.id -eq 'case-08' }
"OK. case-08 dsl_versions=$($c2.dsl_versions) render_count=$($c2.render_count) request_ids=$($c2.request_ids -join ',')"
"review mentions fix: " + ($chk.final_collection_review -match '关闭后修正')
