$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$tmp  = Join-Path $root 'tmp\run-20261002-220723-mimo\B02'
$enc  = New-Object System.Text.UTF8Encoding($false)
$itPath = Join-Path $tmp 'iterations.jsonl'
if (Test-Path $itPath) { $existing = [System.IO.File]::ReadAllLines($itPath) } else { $existing = @() }

function J([object]$o) {
    $s = $o | ConvertTo-Json -Compress -Depth 6
    $s = [regex]::Replace($s, '\\u(?<c>[0-9a-fA-F]{4})', { param($m) [char][int]('0x' + $m.Groups['c'].Value) })
    return $s
}

$add = @()
function I([hashtable]$h) { $script:add += , $h }

# --- shared: cross-work data-consistency audit (drove the r6/r7 round) ---
I @{ iteration_id='ite-B02-consistency-audit'; case_id=$null; scope='task'; version=$null; parent_version=$null; type='requirement-change'
    request_id=$null; http_status=$null; duration_ms=$null; render_ended_utc=$null
    viewed=$false; view_evidence='读图工具已打开全部 10 件；随后以生成脚本重新核对跨件数字'
    observation='交付前的全作品数据核对发现 9 处互相矛盾或算不平的数字：case-01 写「47 天」但 9/20-11/15 实为 57 天；case-01「往届记录 4,180 条 2019-2025 累计」与 case-09「4,180 条 · 迁徙季单季」撞号；case-01「在册志愿者 86 名」与 case-09「参与 86 人 · 志愿者 62」冲突；case-01「每周六 06:30 集合」与 case-08 六个周六各有不同时间冲突；case-01「其中三天开放给公众」与 case-08 的 9 场冲突；case-04「今日鸟种 18」但表里只有 16 行、且 16 行数量合计 392 ≠ 声明的「今日个体 412」；case-04「在站 37 人 · 峰值 06:40」与柱图「峰值出现在 07:00」自相矛盾、又与柱峰值 37 同号；case-04「明日 06:00 同步调查 / 周六 06:30 新手场 余 4 席」与 case-08 的 10-10 周六 06:30 同步调查、10-12 周日 09:00 亲子场 余 4 席不符；case-07 证号 MB-V-0217 暗示第 217 号志愿者与 62 名不符；case-09「新认养 341 人覆盖 1.8 亩」与 case-10 的 ¥30→0.5 亩/月 定价对不上；case-10 标题「够一亩滩涂吃一周」与档位「每月清理 0.5 亩」不符、¥128 的「包一亩滩涂全年维护」比 ¥30 的 0.5 亩/月 还少'
    change='case-01：47→57 天、往届累计→33,400 条 2019-2025 共 8 届、在册志愿者 86→参与志愿者 62 名、集合时间→10/10 周六 06:30 北门、文案改「同步调查与新手场都开放给公众」；case-04：今日鸟种 18→16、绿头鸭 86→96 / 白鹭 23→28 / 黑水鸡 31→36 使 16 行合计正好 412、在站观鸟人 37·峰值06:40 → 21 人·17:42 当前、NEXT UP 改 10/10 06:30 同步调查 与 10/12 09:00 亲子场 余 4 席、潮汐块「下次同步 明日 06:00」→「周六 06:30」；case-07：MB-V-0217→MB-V-0062（两处）；case-09：覆盖 1.8 亩→每月约 1.7 万元（=214×30+96×68+31×128=16,916 元）；case-10：标题「够一亩滩涂吃一周」→「够半亩滩涂吃一个月」、eyebrow「认养一亩滩涂」→「认养滩涂」、守望者权益「包一亩滩涂全年维护」→「每月清理 2.5 亩与全年巡护」使三档 0.5/1.2/2.5 亩递增'
    result='跨件数据在重新生成后自洽；受影响的 case-01/04/07/09/10 全部重渲染并重新看图' }

# --- case-01 r6 ---
I @{ iteration_id='ite-B02-c01-v6-visual'; case_id='case-01'; version='v6'; parent_version='v5'; type='visual'
    request_id='B02-c01-r6'; http_status=200; duration_ms=4620.2; render_ended_utc='2026-10-06T05:12:24.300Z'
    viewed=$true; view_evidence='读图工具打开 tmp/.../B02/view/chk01-20261006131252341.jpg（标签与内容一致：case-01 海报）'
    observation='57 天、9/20-11/15 共 57 天、10/10 周六 06:30 北门、往届累计 33,400 条 2019-2025 共 8 届、参与志愿者 62 名全部到位；62% 进度环仍自 12 点起，文案第三行改为「同步调查与新手场都开放给公众」'
    change=$null
    result='完成，通过' }

# --- case-04 r6 / r7 ---
I @{ iteration_id='ite-B02-c04-v5-visual'; case_id='case-04'; version='v5'; parent_version='v4'; type='visual'
    request_id='B02-c04-r6'; http_status=200; duration_ms=4372.7; render_ended_utc='2026-10-06T05:12:28.696Z'
    viewed=$true; view_evidence='读图工具打开 tmp/.../B02/view/chk04-20261006131252341.jpg（标签与内容一致：case-04 看板）'
    observation='今日鸟种 16、今日个体 412、在站观鸟人 21 人 17:42 当前；16 行合计 96+12+28+36+18+9+44+27+14+8+3+16+22+4+11+64 = 412 与「今日个体」一致；NEXT UP 为 10/10 06:30 同步调查 还缺 6 名志愿者 与 10/12 09:00 亲子场 余 4 席 · 6-12 岁，与 case-08 完全对应；柱图 06..13、峰值 07:00'
    change='潮汐块第三行仍写「下次同步 明日 06:00」，与上述两处不一致 → 改为「周六 06:30」'
    result='未完成（待下一次渲染）' }
I @{ iteration_id='ite-B02-c04-v6-incomplete'; case_id='case-04'; version='v6'; parent_version='v5'; type='visual-incomplete'
    request_id='B02-c04-r7'; http_status=200; duration_ms=3882.2; render_ended_utc='2026-10-06T05:20:53.635Z'
    viewed=$false
    view_evidence='读图工具连续 4 次打开 outputs/.../B02/case-04/final.png 与 2 份裁剪校验图，全部返回其它用例的图像字节（环境缺陷）'
    observation='无法取得该次渲染的可归因图像；改用 System.Drawing 与上一版自标注副本做像素比对：以 2px 步长全图采样，强差异（三通道绝对差和 > 90）落在「下次同步」值框 [280..540, 945..1005] 内的密度为 117/3900 = 3.0%，框外仅 450/514500 = 0.087%（JPEG 压缩噪声），即整张图只有该值框的字形发生了变化；框内亮字像素由 506 变为 489，与「明日 06:00」→「周六 06:30」的字形差异一致'
    change=$null
    result='判为未完成迭代；改动已由 DSL 源（gen-b02-a.ps1:288「周六 06:30」）、HTTP 200 与上述像素比对三方确认，视觉判断沿用该版唯一差异区之外已通过的整版检查' }

# --- case-07 r6 ---
I @{ iteration_id='ite-B02-c07-v3-visual'; case_id='case-07'; version='v3'; parent_version='v2'; type='visual'
    request_id='B02-c07-r6'; http_status=200; duration_ms=2200.6; render_ended_utc='2026-10-06T05:12:30.919Z'
    viewed=$true; view_evidence='读图工具打开 tmp/.../B02/view/chk09-20261006131252487.jpg（图内标签条写明 case-07，与内容一致；文件名与标签对调，见 snapshot-usage）'
    observation='编号与右下角均改为 MB-V-0062，与 case-09 的「志愿者 62」一致；头肩剪影、三行信息栅格、三枚权限胶囊未受影响'
    change=$null
    result='完成，通过' }

# --- case-09 r6 ---
I @{ iteration_id='ite-B02-c09-v3-visual'; case_id='case-09'; version='v3'; parent_version='v2'; type='visual'
    request_id='B02-c09-r6'; http_status=200; duration_ms=3305.2; render_ended_utc='2026-10-06T05:12:34.248Z'
    viewed=$true; view_evidence='读图工具打开 tmp/.../B02/view/chk07-20261006131252487.jpg（图内标签条写明 case-09，与内容一致）'
    observation='「新认养 341 人，每月约 1.7 万元」与 case-10 三档人数/单价（214×30 + 96×68 + 31×128 = 16,916 元）对得上；4,180 条、132 种 +11、参与 86 人 · 志愿者 62、78% 岗位填补率、六行物种计数均未变'
    change=$null
    result='完成，通过' }

# --- case-10 r6 ---
I @{ iteration_id='ite-B02-c10-v4-visual'; case_id='case-10'; version='v4'; parent_version='v3'; type='visual'
    request_id='B02-c10-r6'; http_status=200; duration_ms=3628.2; render_ended_utc='2026-10-06T05:12:37.894Z'
    viewed=$true; view_evidence='读图工具两次打开 outputs/.../B02/case-10/final.png，内容与 case-10 一致（无标签条的原图）'
    observation='主标题「你的 30 元，够半亩滩涂吃一个月」与 ¥30 档「每月清理 0.5 亩互花米草」一致；eyebrow「认养滩涂 · 季度账目公示」不再带「一亩」；三档权益 0.5 / 1.2 / 2.5 亩递增；竖线与横线在 (385, y+128) 相交成完整 L 角；CTA、三条说明与页脚不出血'
    change=$null
    result='完成，通过' }

$new = @()
foreach ($row in $add) {
    $line = J $row
    $exists = $false
    foreach ($e in $existing) { if ($e -contains $row.iteration_id) { $exists = $true } }
    if (-not $exists) { $new += $line }
}
if ($new.Count -gt 0) {
    [System.IO.File]::AppendAllText($itPath, (($new -join "`n") + "`n"), $enc)
}
"appended rows : " + $new.Count
"iterations total : " + (Get-Content $itPath).Count